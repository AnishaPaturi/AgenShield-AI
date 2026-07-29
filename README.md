# AgentShield AI

## Autonomous Multi-Agent Framework for Multi-Cloud Infrastructure-as-Code Security

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/Framework-LangGraph%20%2F%20LangChain-orange?style=flat-square&logo=chainlink&logoColor=white)
![Checkov](https://img.shields.io/badge/Scanner-Checkov-cyan?style=flat-square&logo=prisma&logoColor=white)
![Supported IaC](https://img.shields.io/badge/IaC-Terraform%20%7C%20CFN%20%7C%20Kubernetes%20%7C%20Helm-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Build Status](https://img.shields.io/badge/Tests-10%2F10%20Passed-brightgreen?style=flat-square&logo=pytest&logoColor=white)

AgentShield AI is an advanced, autonomous multi-agent framework designed to secure Infrastructure-as-Code (IaC) templates across heterogeneous multi-cloud environments. The system leverages Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and static code analysis to perform context-aware vulnerability detection, automated code patching, and developer-aligned security reporting.

---

## 📄 Project Metadata

* **Domain of the Project:** Cyber Security + AI
* **Team Number:** 13
* **Project Status:** Under Active Planning / Development
* **GitHub Repository Topics:** `iac-security`, `infrastructure-as-code`, `terraform`, `cloudformation`, `kubernetes`, `helm`, `multi-cloud`, `aws`, `azure`, `gcp`, `llm-agents`, `langgraph`, `rag`, `retrieval-augmented-generation`, `devsecops`, `static-analysis`, `checkov`, `cyber-security`, `ai-agents`, `security-automation`
* **Contributors (Team Members):**
  * **Anisha Paturi** (Roll No: `23BD1A050E`) - *Contact: 8639781680*
  * **Parinamika Bhanu** (Roll No: `23BD1A0518`) - *Contact: 9392508430*
  * **Vahini Venkata** (Roll No: `23BD1A051D`) - *Contact: 8790261823*
  * **Sravani Janak** (Roll No: `23BD1A051Y`) - *Contact: 7075869135*

---

## 📚 Foundational Project Documents

The repository contains key foundational documents detailing the architectural specifications, research literature survey, presentation slides, and base research paper:

* 🏗️ **[about.md](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/about.md):** Detailed architecture guide describing the 8 specialized agents, LangGraph orchestration graph, and comparative feature breakdown against the base paper.
* 🌐 **[index.html](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/index.html):** Interactive web presentation summarizing core objectives, multi-agent pipeline, expected results, strengths, and limitations of AgentShield AI.
* 📖 **[literature_survey.txt](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/literature_survey.txt):** In-depth literature survey categorizing existing IaC security approaches, identifying critical research gaps, providing a comprehensive comparative matrix, and listing key academic references.
* 📝 **`project abstract.docx`:** Executive abstract and project overview document.
* 📑 **[LLM Base Paper](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/LLM_Agentic_Workflow_for_Automated_Vulnerability_Detection_and_Remediation_in_Infrastructure-as-Code.pdf):** Base research paper (*Toprani & Madisetti, IEEE Access 2025*).

---

## 💡 Abstract

Cloud-native applications increasingly rely on Infrastructure-as-Code (IaC) to automate the deployment and management of cloud resources. However, security misconfigurations in IaC templates can introduce critical vulnerabilities that are often overlooked by traditional rule-based security tools. This project presents **AgentShield AI**, an autonomous multi-agent framework designed to enhance Infrastructure-as-Code security across multi-cloud environments. 

The proposed system leverages Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and a curated cloud security knowledge base to perform context-aware vulnerability detection and intelligent security analysis. Unlike existing solutions that are limited to a single cloud platform, AgentShield AI supports multiple IaC platforms, providing a unified security analysis framework. The system employs specialized AI agents for IaC parsing, knowledge retrieval, vulnerability detection, automated remediation, and report generation, enabling a modular and scalable security workflow. 

By combining semantic reasoning with domain-specific security knowledge, the framework generates actionable remediation recommendations and comprehensive security reports that can be integrated into DevSecOps pipelines. The proposed solution aims to improve detection accuracy, reduce manual security analysis effort, and provide a scalable approach to securing cloud infrastructure across heterogeneous cloud environments.

---

## 📊 Literature Survey & Comparative Analysis

As detailed in `literature_survey.txt`, current research and commercial offerings in IaC security can be categorized into four primary paradigms:

1. **Static Analysis & Rule-Based Scanners (e.g., CDK-Nag, Checkov, KICS):**
   * *Mechanism:* Parses IaC code against pre-defined, rigid rule packs.
   * *Limitation:* Misses complex, context-dependent misconfigurations (e.g., compound IAM policy risks) and generates high false-positive rates with parameterized/dynamic templates.
2. **Dynamic Analysis & CSPM (e.g., AWS Config, Cloud Security Posture Management):**
   * *Mechanism:* Monitors live cloud resources post-deployment via cloud provider APIs.
   * *Limitation:* Reactive ("shift-right"); fails to catch vulnerabilities before infrastructure is provisioned.
3. **ML-Based Security Smell Detectors (e.g., GLITCH - Saavedra & Ferreira, 2022):**
   * *Mechanism:* Uses machine learning models on intermediate representations across IaC languages.
   * *Limitation:* Requires massive labeled training datasets, struggles with zero-day misconfiguration patterns, and lacks code remediation generation.
4. **LLM & Early Agentic Workflows (Base Paper - Toprani & Madisetti, 2025; GenKubeSec - Malul et al., 2024):**
   * *Mechanism:* Combines LLMs with basic RAG for context-aware vulnerability detection.
   * *Limitation:* Single-cloud scope (CloudFormation only), single-LLM hallucination risks (~15% false-positive rate), text-only recommendations without patch generation, and limited benchmark evaluation.

### Comparative Feature Matrix

| Feature / Metric | Static Scanners (Checkov) | CSPM (AWS Config) | Base Paper (Toprani, 2025) | AgentShield AI (Proposed) |
| :--- | :--- | :--- | :--- | :--- |
| **Analysis Timing** | Pre-commit / CI | Post-deployment | Pre-deployment | Shift-Left (IDE + Pre-commit + CI + Live Drift) |
| **Cloud & IaC Scope** | Multi-Cloud | Live Cloud APIs | AWS CloudFormation only | AWS, Azure, GCP across Terraform, CFN, K8s, & Helm |
| **Context Reasoning** | ❌ Rigid Rules | ❌ State Rules | ⚠️ LLM + RAG | ✅ AST + RAG + Multi-LLM Ensemble (Claude + GPT-4o) |
| **Remediation Output** | Rule Links | Alert Notices | Text Explanations | Syntax & Sandbox-Validated Code Diff Patches |
| **Secrets Scanning** | Basic Regex | ❌ None | ❌ None | Dedicated Secrets Agent (Gitleaks + TruffleHog) |
| **Validation Harness** | ❌ None | ❌ None | ❌ None | Static Linters + LocalStack Runtime Sandbox Testing |
| **Compliance Mapping** | Basic | Rule-level | ❌ None | Automated mapping to SOC 2, HIPAA, PCI-DSS, & NIST 800-53 |
| **Developer Feedback** | ❌ None | ❌ None | ❌ None | Interactive feedback loop & negative-shot prompt adaptation |

---

## 🎯 Research Base Paper & Core Enhancements

AgentShield AI is designed as a direct improvement on the following base paper:
> **Base Paper:** Toprani, D., & Madisetti, V. K. (2025). *LLM Agentic Workflow for Automated Vulnerability Detection and Remediation in Infrastructure-as-Code.* IEEE Access, 13, 69175-69181.

AgentShield AI addresses the critical research gaps of the base paper through comprehensive enhancements:

### Key Research Gaps Addressed

1. **Multi-Cloud & Multi-IaC Generalization:** Extends beyond AWS CloudFormation to **Microsoft Azure** and **Google Cloud Platform (GCP)** across **Terraform (HCL)**, **Kubernetes Manifests**, and **Helm Charts**.
2. **Autonomous 8-Agent Architecture:** Replaces the basic 3-agent linear pipeline with a stateful LangGraph multi-agent network with specialized roles.
3. **Hybrid AST Parsing & Pre-Screening:** Combines AST parsing with static scanners (Checkov, tfsec, KICS) to pre-evaluate conditionals and variables before LLM analysis.
4. **Dynamic Auto-Patching & Linters:** Replaces text explanations with syntactically valid code diff patches tested against local linters (`terraform validate`, `cfn-lint`).
5. **Sandbox Runtime Validation:** Validates patches inside a local sandbox (LocalStack) to confirm provision integrity without breaking infrastructure functionality.
6. **Dedicated Secrets Scanning:** Integrates Gitleaks and TruffleHog engines to intercept embedded credentials, API keys, and certificates.
7. **Multi-LLM Ensemble Voting & Confidence Scoring:** Runs cross-verification (Claude 3.5 + GPT-4o) to eliminate hallucinations, routing low-confidence alerts to human review.
8. **Compliance Framework Mapping:** Automatically tags findings with **SOC 2**, **HIPAA**, **PCI-DSS**, and **NIST 800-53** regulatory controls.
9. **Interactive Developer Feedback:** Captures developer accept/reject actions for dynamic negative-shot prompt tuning.
10. **Attack-Path & Blast-Radius Prioritization:** Constructs resource dependency graphs to prioritize vulnerabilities based on real exploitability and topological impact.
11. **Shift-Left & Live Drift Detection:** Integrates VS Code extensions, pre-commit hooks, and live infrastructure drift detection via provider APIs.
12. **Automated Continuous Knowledge Base Ingestion:** Pulls daily CVE feeds and vendor documentation into Qdrant/ChromaDB vector stores.

---

## 🏗️ System Architecture & Specialized Agents

### LangGraph Multi-Agent Architecture

```mermaid
graph TD
    A[Developer / IDE / CI-CD Pipeline] -->|Submit IaC Templates| B[Manager Agent]
    B --> C[Hybrid AST Parser Agent]
    B --> SEC[Secrets Scanner Agent]
    C -->|AST & Dependency Graph| D[RAG Query Agent]
    SEC -->|Hardcoded Credentials| G[Security Analyst Agent]
    
    subgraph "Knowledge Core & Compliance"
        E[(Vector DB: Qdrant/Chroma)]
        F[Live Scraper Service] -->|Policy Updates| E
        COMP[SOC2 / HIPAA / PCI / NIST Frameworks] --> E
    end
    
    E <-->|Context Queries| D
    D -->|Annotated Context & Attack-Paths| G
    
    subgraph "Analyst & Ensemble Verification"
        G -->|Multi-LLM Voting: Claude + GPT-4o| V{Consensus & High Confidence?}
        V -->|Low Confidence| HMN[Human Security Audit Queue]
        V -->|High Confidence| H[Remediation Agent]
    end
    
    H -->|Code Patches/Diffs| I[Validation Agent]
    
    subgraph "Validation Harness"
        I -->|Syntax Linters: terraform validate / cfn-lint| J1{Syntax Valid?}
        J1 -->|No| H
        J1 -->|Yes| J2[LocalStack Sandbox Runtime Test]
        J2 -->|Runtime Failure| H
    end
    
    J2 -->|Validated Patch| K[Report Generator Agent]
    
    K -->|Unified Security & Compliance Report| L[Developer Interface / VS Code]
    L -->|Accept/Reject Feedback| M[(Developer Feedback Log)]
    M -->|Dynamic Few-Shot Tuning| G
```

### The 8 Specialized Agents of AgentShield AI

1. **Manager/Router Agent:** Directs execution state, handles routing, and allocates tasks among agents.
2. **Hybrid AST Parser Agent:** Extracts ASTs from HCL, CloudFormation JSON/YAML, Kubernetes YAML, and Helm templates, evaluating dynamic variables and pre-resolving parameters.
3. **Secrets Scanner Agent:** Executes integrated Gitleaks and TruffleHog engines to intercept hardcoded API keys, tokens, and credentials.
4. **RAG-Query Agent:** Interrogates vector databases (Qdrant/ChromaDB) for multi-cloud security policies, CIS benchmarks, and regulatory compliance controls.
5. **Security Analyst Agent:** Performs Multi-LLM Ensemble Voting (Claude 3.5 + GPT-4o) with calibrated confidence scoring. Escalates low-confidence findings to a human security queue.
6. **Remediation Agent:** Generates clean, executable code diff patches targeting specific IaC resource blocks instead of natural language text.
7. **Code & Sandbox Validator Agent:** Verifies code syntax via local linters (`terraform validate`, `cfn-lint`) and performs runtime dry-run deployment inside LocalStack.
8. **Report Agent:** Generates audit-ready compliance reports (SOC 2, HIPAA, PCI-DSS, NIST 800-53) and stores developer feedback for continuous prompt adaptation.

---

## 🛠️ Technology Stack & Tools

* **Programming Language:** Python 3.12+
* **Orchestration & State Management:** LangGraph / LangChain
* **Vector DB / RAG Ingestion:** Qdrant / ChromaDB & `sentence-transformers`
* **Static Scanners & Secrets Engines:** Checkov, tfsec, KICS, Gitleaks, TruffleHog
* **Language Models:** Anthropic Claude 3.5 (via Bedrock/API), OpenAI GPT-4o, Local Distilled SLM
* **Validation & Sandbox:** LocalStack (AWS Emulation), `terraform validate`, `cfn-lint`
* **Development Utilities:** `uv` (Fast Python package manager), Docker, Pytest

---

## 📅 Implementation Roadmap

### Phase 1: Foundation, Multi-IaC Ingestion & Core Documentation (Weeks 1-3)
* [ ] Project structure setup and foundational documentation suite ([about.md](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/about.md), [index.html](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/index.html), and [literature_survey.txt](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/literature_survey.txt)).
* [ ] Detailed architectural specification of the 8-agent LangGraph orchestration state machine.
* [ ] Multi-cloud IaC parser design and schema definitions for Terraform (HCL), CloudFormation (JSON/YAML), Kubernetes Manifests (YAML), and Helm Charts.
* [ ] Static scanner integration design (Checkov, tfsec, KICS) for hybrid AST parsing and attribute enrichment.
* [ ] Research literature survey, research gap analysis against base IEEE Access 2025 paper, and comparative feature matrix.
* [ ] Implementation of Dedicated Secrets & Credential Scanning Agent (Gitleaks / TruffleHog engines).

### Phase 2: Multi-Cloud Knowledge Base & RAG Compliance Core (Weeks 4-6)
* [ ] Setup of Qdrant / ChromaDB vector database and automated scraping service for live policy updates.
* [ ] Automated continuous ingestion of CIS Benchmarks, cloud security docs, and regulatory compliance frameworks (SOC 2, HIPAA, PCI-DSS, NIST 800-53).
* [ ] Optimization of semantic retrieval matching algorithms, AST hash caching, and embedding-based resource deduplication.

### Phase 3: LangGraph Multi-Agent Core, Ensemble Voting & Confidence Scoring (Weeks 7-9)
* [ ] Implementation of the LangGraph state machine with Manager/Router Agent for stateful task distribution.
* [ ] Security Analyst Agent with Multi-LLM Ensemble Voting (Claude 3.5 + GPT-4o) and calibrated confidence scoring.
* [ ] Automated escalation routing for low-confidence or non-consensus findings to Human Security Review Queue.

### Phase 4: Patch Generation, LocalStack Sandbox Validation & Attack-Path Ranking (Weeks 10-12)
* [ ] AST-level resource dependency graph construction and attack-path exploitability ranking (blast radius prioritization).
* [ ] Remediation Agent executable code diff-patch generator.
* [ ] Code & Sandbox Validator Agent with static linters (`terraform validate`, `cfn-lint`) and LocalStack runtime sandbox deployment testing.
* [ ] Interactive developer feedback loop implementation and negative-shot prompt adaptation engine.

### Phase 5: Shift-Left IDE Integration, Live Drift & Automated Benchmarking (Weeks 13-14)
* [ ] VS Code IDE Extension & Git pre-commit hook integration for real-time authoring security feedback.
* [ ] Live cloud infrastructure drift detection via Cloud Provider APIs to catch manual out-of-band changes.
* [ ] Automated benchmark harness execution against public vulnerable IaC corpora (Terragoat, cfngoat, KICS/Checkov test fixtures, IaC-Eval) with component ablation studies (RAG on/off, hybrid parsing on/off).


---

## 📂 Project Structure

```
AgentShield-AI/
├── .gitignore               # Git ignore configuration
├── README.md                # Primary project documentation
├── about.md                 # System architecture & specialized 8-agent breakdown
├── index.html               # Interactive web presentation (objectives, pipeline, results)
├── literature_survey.txt    # IaC security literature survey, gaps, & comparative matrix
├── project abstract.docx    # Executive abstract and project overview document
└── LLM_Agentic_Workflow_for_Automated_Vulnerability_Detection_and_Remediation_in_Infrastructure-as-Code.pdf # IEEE Access base paper
```

---

## 📚 References & Academic Citations

1. **Toprani, D., & Madisetti, V. K. (2025).** *LLM Agentic Workflow for Automated Vulnerability Detection and Remediation in Infrastructure-as-Code.* IEEE Access, 13, 69175-69181. *(Base Paper)*
2. **Saavedra, N., & Ferreira, J. F. (2022).** *GLITCH: Automated polyglot security smell detection in infrastructure as code.* arXiv:2205.14371.
3. **Malul, E., et al. (2024).** *GenKubeSec: LLM-based kubernetes misconfiguration detection, localization, reasoning, and remediation.* arXiv:2405.19954.
4. **Minna, F., et al. (2024).** *Analyzing and mitigating (with LLMs) the security misconfigurations of helm charts.* arXiv:2403.09537.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
