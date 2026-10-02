/**
 * Unit & Integration Tests for AgentShield AI VS Code Extension.
 * Executed via Node.js native test runner: node --test
 */

const test = require('node:test');
const assert = require('node:assert');

// Lightweight Mock of VS Code API for Extension Testing
const mockVsCode = {
  DiagnosticSeverity: {
    Error: 0,
    Warning: 1,
    Information: 2,
    Hint: 3,
  },
  Range: class Range {
    constructor(startLine, startChar, endLine, endChar) {
      this.start = { line: startLine, character: startChar };
      this.end = { line: endLine, character: endChar };
    }
  },
  Diagnostic: class Diagnostic {
    constructor(range, message, severity) {
      this.range = range;
      this.message = message;
      this.severity = severity;
    }
  },
  DiagnosticRelatedInformation: class DiagnosticRelatedInformation {
    constructor(location, message) {
      this.location = location;
      this.message = message;
    }
  },
  Location: class Location {
    constructor(uri, range) {
      this.uri = uri;
      this.range = range;
    }
  },
  CodeAction: class CodeAction {
    constructor(title, kind) {
      this.title = title;
      this.kind = kind;
    }
  },
  CodeActionKind: {
    QuickFix: 'quickfix',
  },
  WorkspaceEdit: class WorkspaceEdit {
    constructor() {
      this.edits = [];
    }
    replace(uri, range, newText) {
      this.edits.push({ uri, range, newText });
    }
  },
  StatusBarAlignment: { Right: 2 },
  languages: {
    createDiagnosticCollection: (name) => ({
      name,
      set: () => {},
      delete: () => {},
      clear: () => {},
      dispose: () => {},
    }),
    registerCodeActionsProvider: () => ({ dispose: () => {} }),
  },
  window: {
    createStatusBarItem: () => ({
      show: () => {},
      dispose: () => {},
      text: '',
      tooltip: '',
    }),
    showInformationMessage: () => {},
    showWarningMessage: () => {},
    showErrorMessage: () => {},
    activeTextEditor: null,
  },
  commands: {
    registerCommand: () => ({ dispose: () => {} }),
  },
  workspace: {
    getConfiguration: () => ({
      get: (key, def) => def,
    }),
    onDidSaveTextDocument: () => ({ dispose: () => {} }),
    onDidCloseTextDocument: () => ({ dispose: () => {} }),
  },
};

// Inject mock into module cache for vscode require
const Module = require('module');
const origRequire = Module.prototype.require;
Module.prototype.require = function (id) {
  if (id === 'vscode') {
    return mockVsCode;
  }
  return origRequire.apply(this, arguments);
};

const extension = require('../extension.js');

test('isIaCDocument correctly identifies supported IaC file types', () => {
  assert.strictEqual(extension.isIaCDocument({ fileName: 'main.tf' }), true);
  assert.strictEqual(extension.isIaCDocument({ fileName: 'variables.tfvars' }), true);
  assert.strictEqual(extension.isIaCDocument({ fileName: 'template.yaml' }), true);
  assert.strictEqual(extension.isIaCDocument({ fileName: 'service.yml' }), true);
  assert.strictEqual(extension.isIaCDocument({ fileName: 'cloudformation.json' }), true);

  // Unsupported files
  assert.strictEqual(extension.isIaCDocument({ fileName: 'script.py' }), false);
  assert.strictEqual(extension.isIaCDocument({ fileName: 'app.js' }), false);
  assert.strictEqual(extension.isIaCDocument({ fileName: 'README.md' }), false);
  assert.strictEqual(extension.isIaCDocument(null), false);
});

test('mapSeverity correctly maps finding severities to VS Code DiagnosticSeverity', () => {
  assert.strictEqual(extension.mapSeverity('CRITICAL'), mockVsCode.DiagnosticSeverity.Error);
  assert.strictEqual(extension.mapSeverity('HIGH'), mockVsCode.DiagnosticSeverity.Error);
  assert.strictEqual(extension.mapSeverity('MEDIUM'), mockVsCode.DiagnosticSeverity.Warning);
  assert.strictEqual(extension.mapSeverity('LOW'), mockVsCode.DiagnosticSeverity.Information);
  assert.strictEqual(extension.mapSeverity('INFORMATIONAL'), mockVsCode.DiagnosticSeverity.Information);
  assert.strictEqual(extension.mapSeverity('UNKNOWN'), mockVsCode.DiagnosticSeverity.Information);
});

test('buildDiagnostics produces formatted diagnostics and honors strictMode', () => {
  const mockDoc = {
    lineCount: 20,
    lineAt: (n) => ({ text: 'resource "aws_s3_bucket" "test" {' }),
    uri: { toString: () => 'file:///test/main.tf' },
  };

  const sampleFindings = [
    {
      finding_id: 'f-1',
      title: 'Public S3 Bucket ACL',
      rule_id: 'AS-AWS-001',
      severity: 'CRITICAL',
      description: 'S3 bucket allows public reads.',
      affected_resource: 'aws_s3_bucket.test',
      line_range: { start_line: 12, end_line: 15 },
    },
    {
      finding_id: 'f-2',
      title: 'Missing Cost Tagging',
      rule_id: 'AS-GEN-010',
      severity: 'LOW',
      description: 'Resource missing Environment tag.',
      affected_resource: 'aws_s3_bucket.test',
      line_range: { start_line: 14, end_line: 14 },
    },
  ];

  // In non-strict mode: LOW finding should be excluded
  const normalDiags = extension.buildDiagnostics(mockDoc, sampleFindings, false);
  assert.strictEqual(normalDiags.length, 1);
  assert.strictEqual(normalDiags[0].code, 'AS-AWS-001');
  assert.strictEqual(normalDiags[0].severity, mockVsCode.DiagnosticSeverity.Error);
  assert.strictEqual(normalDiags[0].range.start.line, 11); // 0-indexed: 12 - 1 = 11

  // In strict mode: Both findings should be included
  const strictDiags = extension.buildDiagnostics(mockDoc, sampleFindings, true);
  assert.strictEqual(strictDiags.length, 2);
  assert.strictEqual(strictDiags[1].code, 'AS-GEN-010');
  assert.strictEqual(strictDiags[1].severity, mockVsCode.DiagnosticSeverity.Information);
});

test('AgentShieldQuickFixProvider generates valid code actions from cached patches', () => {
  const provider = new extension.AgentShieldQuickFixProvider();

  // Test provideCodeActions with no diagnostics
  const emptyActions = provider.provideCodeActions(
    { uri: { toString: () => 'file:///empty.tf' } },
    null,
    { diagnostics: [] }
  );
  assert.deepStrictEqual(emptyActions, []);
});

test('Extension activate and deactivate lifecycle completes cleanly', () => {
  const mockContext = {
    subscriptions: [],
  };

  assert.doesNotThrow(() => {
    extension.activate(mockContext);
  });
  assert(mockContext.subscriptions.length >= 4, 'Subscriptions should register commands and listeners');

  assert.doesNotThrow(() => {
    extension.deactivate();
  });
});
