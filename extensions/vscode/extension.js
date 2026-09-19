/**
 * AgentShield AI VS Code Extension (Task 5.1).
 *
 * Provides real-time shift-left IaC misconfiguration scanning,
 * inline diagnostic squiggles, and one-click quick-fix patch applications.
 */

const vscode = require('vscode');

let diagnosticCollection;
let statusBarItem;
const patchStore = new Map(); // uri -> list of patches

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  diagnosticCollection = vscode.languages.createDiagnosticCollection('agentshield');
  context.subscriptions.push(diagnosticCollection);

  // Status Bar Item
  statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.command = 'agentshield.scanCurrentFile';
  statusBarItem.text = '$(shield) AgentShield';
  statusBarItem.tooltip = 'Click to scan active IaC template with AgentShield AI';
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  // Register Commands
  context.subscriptions.push(
    vscode.commands.registerCommand('agentshield.scanCurrentFile', () => {
      const editor = vscode.window.activeTextEditor;
      if (editor) {
        runScan(editor.document, true);
      } else {
        vscode.window.showInformationMessage('No active editor open to scan.');
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('agentshield.openDashboard', () => {
      const config = vscode.workspace.getConfiguration('agentshield');
      const apiUrl = config.get('apiUrl', 'http://localhost:8000');
      vscode.env.openExternal(vscode.Uri.parse(apiUrl));
    })
  );

  // Document Save Event Listener
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((document) => {
      const config = vscode.workspace.getConfiguration('agentshield');
      if (config.get('scanOnSave', true) && isIaCDocument(document)) {
        runScan(document, false);
      }
    })
  );

  // Quick Fix CodeAction Provider
  context.subscriptions.push(
    vscode.languages.registerCodeActionsProvider(
      [
        { scheme: 'file', language: 'terraform' },
        { scheme: 'file', pattern: '**/*.tf' },
        { scheme: 'file', language: 'yaml' },
        { scheme: 'file', language: 'json' },
      ],
      new AgentShieldQuickFixProvider(),
      {
        providedCodeActionKinds: [vscode.CodeActionKind.QuickFix],
      }
    )
  );

  // Auto-scan on active editor change if IaC
  if (vscode.window.activeTextEditor && isIaCDocument(vscode.window.activeTextEditor.document)) {
    runScan(vscode.window.activeTextEditor.document, false);
  }
}

function isIaCDocument(doc) {
  const fileName = doc.fileName.toLowerCase();
  return (
    fileName.endsWith('.tf') ||
    fileName.endsWith('.yaml') ||
    fileName.endsWith('.yml') ||
    fileName.endsWith('.json')
  );
}

/**
 * Execute scan against AgentShield API backend
 */
async function runScan(document, notifyUser = false) {
  if (!isIaCDocument(document)) {
    if (notifyUser) {
      vscode.window.showWarningMessage('AgentShield: Active file is not an IaC template (.tf, .yaml, .json).');
    }
    return;
  }

  const config = vscode.workspace.getConfiguration('agentshield');
  const apiUrl = config.get('apiUrl', 'http://localhost:8000').replace(/\/$/, '');

  statusBarItem.text = '$(sync~spin) Scanning IaC...';

  try {
    const content = document.getText();
    const formData = new FormData();
    const blob = new Blob([content], { type: 'text/plain' });
    formData.append('file', blob, document.fileName.split(/[/\\]/).pop());

    const response = await fetch(`${apiUrl}/api/scan`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API responded with HTTP ${response.status}`);
    }

    const ws = await response.json();
    processScanResults(document, ws, notifyUser);
  } catch (err) {
    statusBarItem.text = '$(shield) AgentShield: Offline';
    statusBarItem.tooltip = `AgentShield backend error: ${err.message}`;
    if (notifyUser) {
      vscode.window.showErrorMessage(`AgentShield Scan Error: ${err.message}. Ensure backend is running at ${apiUrl}`);
    }
  }
}

function processScanResults(document, workspace, notifyUser) {
  const diagnostics = [];
  const findings = workspace.report ? workspace.report.findings : [];
  const patches = workspace.patches || [];

  // Cache patches for QuickFix provider
  patchStore.set(document.uri.toString(), patches);

  let critCount = 0;
  let highCount = 0;

  findings.forEach((f) => {
    if (f.severity === 'CRITICAL') critCount++;
    if (f.severity === 'HIGH') highCount++;

    let line = 0;
    if (f.line_range && f.line_range.start_line > 0) {
      line = f.line_range.start_line - 1;
    }

    const range = new vscode.Range(
      line,
      0,
      line,
      document.lineAt(Math.min(line, document.lineCount - 1)).text.length
    );

    let severity = vscode.DiagnosticSeverity.Warning;
    if (f.severity === 'CRITICAL' || f.severity === 'HIGH') {
      severity = vscode.DiagnosticSeverity.Error;
    } else if (f.severity === 'LOW' || f.severity === 'INFORMATIONAL') {
      severity = vscode.DiagnosticSeverity.Information;
    }

    const diag = new vscode.Diagnostic(
      range,
      `[AgentShield AI] ${f.title} (${f.rule_id}) - ${f.description}`,
      severity
    );
    diag.code = f.rule_id;
    diag.source = 'AgentShield AI';
    diag.findingId = f.finding_id;
    diagnostics.push(diag);
  });

  diagnosticCollection.set(document.uri, diagnostics);

  if (critCount + highCount > 0) {
    statusBarItem.text = `$(shield) AgentShield: ${critCount} Crit, ${highCount} High`;
    statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
  } else if (findings.length > 0) {
    statusBarItem.text = `$(shield) AgentShield: ${findings.length} findings`;
    statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
  } else {
    statusBarItem.text = '$(shield) AgentShield: Secure';
    statusBarItem.backgroundColor = undefined;
  }

  if (notifyUser) {
    vscode.window.showInformationMessage(
      `AgentShield Scan complete: ${findings.length} findings detected (${patches.length} auto-patches available).`
    );
  }
}

class AgentShieldQuickFixProvider {
  provideCodeActions(document, range, context) {
    const actions = [];
    const patches = patchStore.get(document.uri.toString()) || [];

    context.diagnostics.forEach((diag) => {
      const matchingPatch = patches.find((p) => p.finding_id === diag.findingId);
      if (matchingPatch && matchingPatch.original_code && matchingPatch.patched_code) {
        const action = new vscode.CodeAction(
          `Apply AgentShield AI patch (${diag.code || 'Security Fix'})`,
          vscode.CodeActionKind.QuickFix
        );
        action.diagnostics = [diag];
        action.isPreferred = true;

        const edit = new vscode.WorkspaceEdit();
        const text = document.getText();
        const startIdx = text.indexOf(matchingPatch.original_code);
        if (startIdx !== -1) {
          const startPos = document.positionAt(startIdx);
          const endPos = document.positionAt(startIdx + matchingPatch.original_code.length);
          edit.replace(document.uri, new vscode.Range(startPos, endPos), matchingPatch.patched_code);
          action.edit = edit;
          actions.push(action);
        }
      }
    });

    return actions;
  }
}

function deactivate() {
  if (diagnosticCollection) {
    diagnosticCollection.clear();
    diagnosticCollection.dispose();
  }
  if (statusBarItem) {
    statusBarItem.dispose();
  }
}

module.exports = {
  activate,
  deactivate,
};
