# AgentShield AI — VS Code Extension (Task 5.1)

Shift-Left Autonomous Multi-Cloud Infrastructure-as-Code (IaC) Security & Remediation directly inside Visual Studio Code.

---

## ⚡ Overview

The **AgentShield AI VS Code Extension** integrates AgentShield's autonomous security intelligence directly into your development workflow. It inspects Terraform, CloudFormation, Kubernetes, and Helm manifests on save or on-demand, flags security vulnerabilities via inline squiggles and the VS Code **Problems** panel, and provides **one-click QuickFix patches** synthesized and validated by AgentShield's multi-agent pipeline.

---

## 🚀 Key Features

1. **Polyglot IaC Support:**
   - Terraform (`.tf`, `.tfvars`)
   - AWS CloudFormation (`.yaml`, `.yml`, `.json`)
   - Kubernetes manifests (`.yaml`, `.yml`)
   - Helm templates and values (`Chart.yaml`, `values.yaml`)

2. **Real-Time Shift-Left Feedback:**
   - Scans active files upon saving (`scanOnSave: true`) or manually via the command palette.
   - Highlights vulnerable resources with rule IDs, descriptions, and affected cloud resource names.

3. **Severity Mapping to VS Code Diagnostics:**
   - `CRITICAL` & `HIGH` $\rightarrow$ **Error** (Red squiggles, blocks CI/CD)
   - `MEDIUM` $\rightarrow$ **Warning** (Yellow squiggles)
   - `LOW` & `INFORMATIONAL` $\rightarrow$ **Information** (Blue squiggles, configurable via `strictMode`)

4. **One-Click Automated Patching:**
   - Interactive lightbulb / QuickFix actions apply syntactically validated code diffs directly into your editor.

5. **Status Bar & Resilience:**
   - Displays real-time posture indicators in the bottom status bar (`$(shield) AgentShield: Secure` or `$(shield) AgentShield: 1 Crit, 2 High`).
   - Fails gracefully with non-intrusive offline warnings when the backend is unreachable.

---

## 🛠️ Configuration Settings

Configure these settings in VS Code (`settings.json` or Preferences $\rightarrow$ Settings $\rightarrow$ AgentShield AI):

| Setting | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `agentshield.apiUrl` | `string` | `"http://localhost:8000"` | Base URL of the running AgentShield FastAPI backend. |
| `agentshield.scanOnSave` | `boolean` | `true` | Automatically run security scans whenever an IaC document is saved. |
| `agentshield.strictMode` | `boolean` | `false` | When enabled, reports Low and Informational findings in addition to Critical/High. |
| `agentshield.authToken` | `string` | `""` | Optional Bearer JWT or API key for authenticated AgentShield deployments. |
| `agentshield.timeoutMs` | `number` | `10000` | Scanner API timeout in milliseconds before failing safely. |

---

## 📦 Installation & Usage

### 1. Prerequisites
- Visual Studio Code version `1.75.0` or later.
- Running AgentShield AI Backend (`python -m uvicorn agentshield.api.main:app --port 8000`).

### 2. Manual Development Installation
1. Clone or navigate to the AgentShield repository:
   ```bash
   cd integrations/vscode
   ```
2. Open VS Code in the directory:
   ```bash
   code .
   ```
3. Press `F5` to launch an Extension Development Host window.
4. In the Extension Host window, open any `.tf` or `.yaml` file. The extension activates automatically!

### 3. Registered Commands
- `AgentShield: Scan Current IaC File` (`agentshield.scanCurrentFile`)
- `AgentShield: Open Security Dashboard` (`agentshield.openDashboard`)
- `AgentShield: Clear Security Diagnostics` (`agentshield.clearDiagnostics`)

---

## 🔧 Troubleshooting

- **"AgentShield: Offline" in status bar:**
  - Verify that the AgentShield backend is running: `curl http://localhost:8000/health`.
  - Check `agentshield.apiUrl` in your VS Code settings.
- **Diagnostics not appearing:**
  - Ensure the active file has a supported extension (`.tf`, `.yaml`, `.yml`, `.json`).
  - Check the output in the VS Code Developer Tools console (`Help -> Toggle Developer Tools`).
