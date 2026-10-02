/**
 * AgentShield AI VS Code Extension (Task 5.1).
 *
 * Provides shift-left IaC misconfiguration scanning,
 * inline diagnostic squiggles, Problems panel integration,
 * and one-click quick-fix remediation diff application.
 */

const vscode = require('vscode');

let diagnosticCollection;
let statusBarItem;
const patchStore = new Map(); // uri string -> list of patches

/**
 * Supported IaC File Extensions matching AgentShield Dispatcher:
 * - Terraform (.tf, .tfvars)
 * - CloudFormation (.yaml, .yml, .json)
 * - Kubernetes (.yaml, .yml)
 * - Helm (Chart.yaml, values.yaml)
 */
function isIaCDocument(doc) {
  if (!doc || !doc.fileName) return false;
  const fileName = doc.fileName.toLowerCase();
  return (
    fileName.endsWith('.tf') ||
    fileName.endsWith('.tfvars') ||
    fileName.endsWith('.yaml') ||
    fileName.endsWith('.yml') ||
    fileName.endsWith('.json')
  );
}

/**
 * Map AgentShield Finding Severity to VS Code DiagnosticSeverity.
 * - CRITICAL / HIGH -> DiagnosticSeverity.Error
 * - MEDIUM -> DiagnosticSeverity.Warning
 * - LOW / INFORMATIONAL -> DiagnosticSeverity.Information
 */
function mapSeverity(severityStr) {
  const sev = (severityStr || '').toUpperCase();
  if (sev === 'CRITICAL' || sev === 'HIGH') {
    return vscode.DiagnosticSeverity.Error;
  }
  if (sev === 'MEDIUM') {
    return vscode.DiagnosticSeverity.Warning;
  }
  return vscode.DiagnosticSeverity.Information;
}

/**
 * Filter and convert AgentShield findings into VS Code Diagnostics.
 */
function buildDiagnostics(document, findings, strictMode) {
  const diagnostics = [];
  if (!document || !Array.isArray(findings)) return diagnostics;

  const totalLines = document.lineCount || 1;

  for (const f of findings) {
    const sev = (f.severity || '').toUpperCase();

    // In non-strict mode, ignore LOW and INFORMATIONAL findings
    if (!strictMode && (sev === 'LOW' || sev === 'INFORMATIONAL')) {
      continue;
    }

    let line = 0;
    if (f.line_range && typeof f.line_range.start_line === 'number' && f.line_range.start_line > 0) {
      line = f.line_range.start_line - 1;
    }

    const safeLine = Math.max(0, Math.min(line, totalLines - 1));
    let lineTextLen = 80;
    try {
      if (document.lineAt && safeLine < totalLines) {
        lineTextLen = document.lineAt(safeLine).text.length;
      }
    } catch {
      // fallback
    }

    const range = new vscode.Range(safeLine, 0, safeLine, Math.max(lineTextLen, 1));
    const diagnostic = new vscode.Diagnostic(
      range,
      `[AgentShield AI] ${f.title || 'Security Finding'} (${f.rule_id || 'AS-GEN-001'}) - ${f.description || ''}`,
      mapSeverity(f.severity)
    );

    diagnostic.code = f.rule_id || 'AS-SEC';
    diagnostic.source = 'AgentShield AI';
    diagnostic.findingId = f.finding_id;

    // Attach related security information where available
    if (f.affected_resource) {
      diagnostic.relatedInformation = [
        new vscode.DiagnosticRelatedInformation(
          new vscode.Location(document.uri, range),
          `Affected Resource: ${f.affected_resource}`
        ),
      ];
    }

    diagnostics.push(diagnostic);
  }

  return diagnostics;
}

/**
 * Execute scan against AgentShield API backend.
 */
async function runScan(document, notifyUser = false) {
  if (!isIaCDocument(document)) {
    if (notifyUser) {
      vscode.window.showWarningMessage(
        'AgentShield: Active file is not a supported IaC template (.tf, .yaml, .yml, .json).'
      );
    }
    return;
  }

  const config = vscode.workspace.getConfiguration('agentshield');
  const apiUrl = config.get('apiUrl', 'http://localhost:8000').replace(/\/$/, '');
  const strictMode = config.get('strictMode', false);
  const authToken = config.get('authToken', '');
  const timeoutMs = config.get('timeoutMs', 10000);

  if (statusBarItem) {
    statusBarItem.text = '$(sync~spin) Scanning IaC...';
  }

  const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timeoutId = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;

  try {
    const content = document.getText();
    if (!content || !content.trim()) {
      if (diagnosticCollection) {
        diagnosticCollection.delete(document.uri);
      }
      patchStore.delete(document.uri.toString());
      if (statusBarItem) {
        statusBarItem.text = '$(shield) AgentShield: Empty';
        statusBarItem.backgroundColor = undefined;
      }
      return;
    }

    const fileName = document.fileName ? document.fileName.split(/[/\\]/).pop() : 'template.tf';
    const formData = new FormData();
    const blob = new Blob([content], { type: 'text/plain' });
    formData.append('file', blob, fileName);

    const headers = {};
    if (authToken && authToken.trim()) {
      headers['Authorization'] = `Bearer ${authToken.trim()}`;
    }

    const response = await fetch(`${apiUrl}/api/scan`, {
      method: 'POST',
      body: formData,
      headers: headers,
      signal: controller ? controller.signal : undefined,
    });

    if (timeoutId) clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Backend responded with HTTP ${response.status} (${response.statusText})`);
    }

    const ws = await response.json();
    processScanResults(document, ws, strictMode, notifyUser);
  } catch (err) {
    if (timeoutId) clearTimeout(timeoutId);

    const isTimeout = err.name === 'AbortError';
    const errorMsg = isTimeout
      ? `Scan timed out after ${timeoutMs / 1000}s. Check if backend at ${apiUrl} is responding.`
      : `AgentShield backend unavailable: ${err.message}.`;

    if (statusBarItem) {
      statusBarItem.text = '$(shield) AgentShield: Offline';
      statusBarItem.tooltip = `${errorMsg}\nRun 'uvicorn agentshield.api.main:app' to start backend.`;
      statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }

    if (notifyUser) {
      vscode.window.showErrorMessage(`AgentShield Scan Error: ${errorMsg}`);
    }
  }
}

/**
 * Process scan results and update diagnostics, patches, and status bar.
 */
function processScanResults(document, workspace, strictMode, notifyUser) {
  const findings = (workspace && workspace.report && workspace.report.findings) || [];
  const patches = (workspace && workspace.patches) || [];

  // Cache patches for QuickFix provider
  patchStore.set(document.uri.toString(), patches);

  const diagnostics = buildDiagnostics(document, findings, strictMode);

  if (diagnosticCollection) {
    diagnosticCollection.set(document.uri, diagnostics);
  }

  const critCount = findings.filter((f) => (f.severity || '').toUpperCase() === 'CRITICAL').length;
  const highCount = findings.filter((f) => (f.severity || '').toUpperCase() === 'HIGH').length;
  const totalReported = diagnostics.length;

  if (statusBarItem) {
    if (critCount + highCount > 0) {
      statusBarItem.text = `$(shield) AgentShield: ${critCount} Crit, ${highCount} High`;
      statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    } else if (totalReported > 0) {
      statusBarItem.text = `$(shield) AgentShield: ${totalReported} findings`;
      statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
      statusBarItem.text = '$(shield) AgentShield: Secure';
      statusBarItem.backgroundColor = undefined;
    }
  }

  if (notifyUser) {
    vscode.window.showInformationMessage(
      `AgentShield Scan complete: ${totalReported} findings displayed (${patches.length} auto-patches available).`
    );
  }
}

/**
 * QuickFix CodeAction Provider offering one-click patch application.
 */
class AgentShieldQuickFixProvider {
  provideCodeActions(document, range, context) {
    const actions = [];
    if (!context || !context.diagnostics) return actions;

    const patches = patchStore.get(document.uri.toString()) || [];

    context.diagnostics.forEach((diag) => {
      const matchingPatch = patches.find((p) => p.finding_id === diag.findingId);
      if (matchingPatch && matchingPatch.original_code && matchingPatch.patched_code) {
        const action = new vscode.CodeAction(
          `Apply AgentShield AI fix: ${diag.code || 'Security Patch'}`,
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

/**
 * Extension entry point.
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

  context.subscriptions.push(
    vscode.commands.registerCommand('agentshield.clearDiagnostics', () => {
      if (diagnosticCollection) {
        diagnosticCollection.clear();
      }
      patchStore.clear();
      if (statusBarItem) {
        statusBarItem.text = '$(shield) AgentShield';
        statusBarItem.backgroundColor = undefined;
      }
      vscode.window.showInformationMessage('AgentShield diagnostics cleared.');
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

  // Document Close Event Listener: clean up cached diagnostics & patches
  context.subscriptions.push(
    vscode.workspace.onDidCloseTextDocument((document) => {
      if (diagnosticCollection) {
        diagnosticCollection.delete(document.uri);
      }
      patchStore.delete(document.uri.toString());
    })
  );

  // Quick Fix CodeAction Provider
  context.subscriptions.push(
    vscode.languages.registerCodeActionsProvider(
      [
        { scheme: 'file', language: 'terraform' },
        { scheme: 'file', pattern: '**/*.tf' },
        { scheme: 'file', pattern: '**/*.tfvars' },
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

function deactivate() {
  if (diagnosticCollection) {
    diagnosticCollection.clear();
    diagnosticCollection.dispose();
  }
  if (statusBarItem) {
    statusBarItem.dispose();
  }
  patchStore.clear();
}

module.exports = {
  activate,
  deactivate,
  isIaCDocument,
  mapSeverity,
  buildDiagnostics,
  AgentShieldQuickFixProvider,
};
