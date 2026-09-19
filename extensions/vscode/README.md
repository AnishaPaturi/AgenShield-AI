# AgentShield AI — VS Code Extension (Task 5.1)

Shift-Left Autonomous Multi-Cloud IaC Security & Remediation directly inside Visual Studio Code.

## Features

- ⚡ **Real-Time Static & Agentic Scanning:** Runs security evaluations on save across Terraform (`.tf`), CloudFormation (`.yaml`/`.json`), and Kubernetes manifests.
- 🔴 **Inline Squiggles & Diagnostics:** Highlights vulnerable resources with rule IDs, descriptions, and severity levels.
- 💡 **One-Click Quick Fixes:** Apply syntactically and sandbox-validated code diff patches directly from the editor's lightbulb icon.
- 🛡️ **Status Bar Posture:** Displays active posture metrics in the status bar (`AgentShield: 0 Crit, 0 High`).
- 🔗 **Direct Web Console Link:** Quickly jump from the editor to the full web dashboard and attack-path visualizer.

## Configuration Settings

- `agentshield.apiUrl`: Base URL for the AgentShield FastAPI backend (default: `http://localhost:8000`).
- `agentshield.scanOnSave`: Enable/disable background scan upon document save (default: `true`).
- `agentshield.strictMode`: Enforce Medium/Low severity alerts as warnings in addition to High/Critical.
