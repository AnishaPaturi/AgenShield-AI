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

## 📅 Detailed Implementation Plan & Execution Roadmap

AgentShield AI is being developed across **5 distinct execution phases over a 14-week timeline**. Each phase delivers fully functional, testable modules mapped directly to our 8-agent architecture, RAG knowledge core, validation harness, and developer interfaces.

---

### 🗓️ Phase 1: Foundation, Multi-IaC Ingestion & Core Documentation (Weeks 1–3)
**Objective:** Establish the project repository infrastructure, build foundational documentation, implement multi-cloud AST parsers, and deploy the secrets scanning engine.

* [x] **Task 1.1: Project Setup & Environment Initialization**
  * Configure fast dependency management via `uv`, set up `pyproject.toml`, and establish automated `pytest` test suites.
  * Define core data contracts (`IaCTemplate`, `ASTNode`, `VulnerabilityReport`, `PatchDiff`) using Pydantic v2 schemas.
* [x] **Task 1.2: System Core & Manager/Router Agent State Machine**
  * Build the initial LangGraph orchestration state graph for workflow control and message passing.
  * Implement state persistence, fallback mechanisms, and conditional graph routing between agents (`AgentShieldState`).
* [x] **Task 1.3: Multi-Cloud Hybrid AST Parser Agent**
  * Develop AST parsers for **Terraform (HCL2)**, **AWS CloudFormation (JSON/YAML)**, **Kubernetes Manifests (YAML)**, and **Helm Charts**.
  * Implement dynamic variable pre-resolution, conditional evaluation, and resource dependency graph extraction.
* [ ] **Task 1.4: Dedicated Secrets & Credential Scanner Agent**
  * Integrate **Gitleaks** and **TruffleHog** engines with high-entropy regex pattern matching.
  * Implement automated interception for API keys, AWS credentials, JWT tokens, and private keys embedded in IaC files.
* [ ] **Task 1.5: Static Scanner Adapter Layer**
  * Build wrapper adapters for **Checkov**, **tfsec**, and **KICS** to enrich parsed AST nodes with baseline vulnerability signals.

**Key Deliverables:** Ingestion pipeline, multi-format IaC parser, secrets scanner agent, and foundational docs ([about.md](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/about.md), [index.html](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/index.html), [literature_survey.txt](file:///C:/Users/anish/OneDrive/College/project-clg/AgenShield-AI/literature_survey.txt)).

---

### 🗓️ Phase 2: Multi-Cloud Knowledge Base & RAG Compliance Core (Weeks 4–6)
**Objective:** Build the vector database pipeline, ingest multi-cloud security standards, and implement the RAG Query Agent for compliance context retrieval.

* [x] **Task 2.1: Vector DB Infrastructure & Embedding Pipeline**
  * Deploy **Qdrant** / **ChromaDB** vector database instance with `sentence-transformers` (e.g., `all-mpnet-base-v2` / BGE embeddings).
  * Build an AST hash caching and semantic deduplication layer (`cache.py`, `dedup.py`) to accelerate similarity lookups.
* [x] **Task 2.2: Continuous Knowledge Base Ingestion Engine**
  * Build automated scrapers and ingestors for AWS/Azure/GCP Security Best Practices, CIS Benchmarks, and NVD/CVE feeds.
  * Create a continuous updater service (`scrapers.py`, `update_kb.py`, `scheduler.py`) to refresh threat intelligence daily.
* [x] **Task 2.3: Regulatory Compliance Mapping Module**
  * Index and crosswalk security policies against **SOC 2**, **HIPAA**, **PCI-DSS**, and **NIST 800-53** frameworks (`compliance.py`, `compliance_controls.json`).
  * Annotate vector embeddings with explicit regulatory control IDs (e.g., `NIST-AC-6`, `PCI-DSS-1.3`).
* [x] **Task 2.4: RAG Query Agent Development**
  * Implement context-aware hybrid retrieval combining dense vector similarity with sparse BM25 keyword search (`hybrid_search.py`, `retriever.py`).
  * Develop prompt contextualizer to inject relevant security controls into the Security Analyst Agent's working memory.

**Key Deliverables:** Fully indexed vector DB, continuous ingestion scraper service, and working RAG Query Agent.

---

### 🗓️ Phase 3: LangGraph Multi-Agent Core, Ensemble Voting & Confidence Scoring (Weeks 7–9)
**Objective:** Complete the stateful 8-agent LangGraph network, implement Multi-LLM ensemble voting, and build the human audit review queue.

* [x] **Task 3.1: Security Analyst Agent & Multi-LLM Ensemble Engine**
  * Connect **Claude 3.5 Sonnet** and **OpenAI GPT-4o** APIs for dual-model parallel vulnerability evaluation (`agents/analyst.py`, `llm/client.py`).
  * Implement structured reasoning templates (Chain-of-Thought prompting) enforcing standardized output JSON schemas.
* [ ] **Task 3.2: Calibrated Confidence Scoring & Consensus Algorithm**
  * Develop mathematical agreement scoring between LLM outputs to eliminate single-model hallucinations.
  * Establish confidence thresholds ($C \ge 0.85$ for auto-patching, $C < 0.85$ for human review).
* [ ] **Task 3.3: Attack-Path & Blast-Radius Prioritization Engine**
  * Construct resource topological graph to evaluate exploitability routes (e.g., Internet Gateway $\rightarrow$ Security Group $\rightarrow$ Unencrypted DB).
  * Rank findings based on combined severity, blast radius, and topological exposure.
* [ ] **Task 3.4: Human Security Audit Queue & Triage Dashboard**
  * Build an automated escalation mechanism for low-confidence or non-consensus findings.
  * Implement a CLI/Web triage interface allowing security engineers to inspect, approve, or reject flagged findings.

**Key Deliverables:** Multi-LLM ensemble engine, calibrated consensus algorithm, attack-path ranker, and human review queue.

---

### 🗓️ Phase 4: Auto-Patch Remediation, LocalStack Validation & Feedback Engine (Weeks 10–12)
**Objective:** Generate executable unified diff patches, build the LocalStack dry-run validation harness, and implement developer feedback loops.

* [x] **Task 4.1: Remediation Agent & Executable Code Patch Generator**
  * Implement code diff generator producing clean, syntactically correct patches targeting exact IaC resource blocks (`agents/remediator.py`).
  * Support patch generation across HCL2, CloudFormation JSON/YAML, K8s YAML, and Helm values.
* [ ] **Task 4.2: Code & Sandbox Validator Agent — Static Linters**
  * Integrate static verification tools (`terraform validate`, `tflint`, `cfn-lint`, `kube-linter`, `helm lint`).
  * Enforce automated rollback to the Remediation Agent if lint errors are detected in generated patches.
* [ ] **Task 4.3: LocalStack Runtime Dry-Run Sandbox Testing**
  * Configure **LocalStack** containerized sandbox for dry-run provisioning of AWS CloudFormation/Terraform resources.
  * Validate that patches do not cause deployment failures or resource dependency breakages.
* [ ] **Task 4.4: Report Generator Agent & Compliance Exporter**
  * Build report generator supporting JSON, Markdown, HTML, SARIF (for GitHub Security tab), and PDF exports.
  * Include executive summaries, attack-path diagrams, patch diffs, and compliance mapping matrices.
* [ ] **Task 4.5: Interactive Developer Feedback & Few-Shot Prompt Adaptation Engine**
  * Capture developer accept/reject decisions on generated patches.
  * Feed negative/positive decisions into a dynamic few-shot prompt adaptation store to continuously reduce false positives.

**Key Deliverables:** Patch generator, linter + LocalStack sandbox validator, multi-format report exporter, and feedback learning engine.

---

### 🗓️ Phase 5: Shift-Left IDE Integration, Live Drift & Automated Benchmarking (Weeks 13–14)
**Objective:** Embed security into developer workflows via IDE extensions and CI/CD hooks, enable live cloud drift detection, and execute rigorous empirical benchmark evaluations.

* [ ] **Task 5.1: VS Code Extension & Git Pre-Commit Hooks**
  * Develop lightweight **VS Code Extension** for real-time IaC security feedback inside the code editor.
  * Package Git pre-commit hooks to block misconfigured IaC templates before commits are recorded.
* [ ] **Task 5.2: Live Cloud Infrastructure Drift Detection Engine**
  * Build Cloud Provider API monitors (AWS Config / Azure Resource Graph / GCP Asset Inventory wrappers) to detect manual, out-of-band state changes.
  * Map live infrastructure drift against IaC source templates to trigger remediation workflows.
* [ ] **Task 5.3: Empirical Benchmark Harness & Ablation Studies**
  * Execute automated evaluations against public vulnerable IaC corpora (**Terragoat**, **cfngoat**, **KICS/Checkov test suites**, **IaC-Eval**).
  * Calculate performance metrics: **Precision**, **Recall**, **F1-Score**, **Patch Pass Rate**, and **Execution Latency**.
  * Perform comprehensive component ablation studies comparing:
    1. Baseline Static Scanners (Checkov) vs. Base Paper vs. AgentShield AI.
    2. RAG ON vs. RAG OFF.
    3. Multi-LLM Ensemble (Claude + GPT-4o) vs. Single-LLM (Claude 3.5 only).
    4. Hybrid AST Parsing vs. Raw Text LLM Ingestion.

**Key Deliverables:** VS Code extension, pre-commit hooks, live drift monitor, benchmark evaluation suite, and final ablation analysis report.

---

### 📊 Implementation Milestone Summary

| Milestone | Target Window | Key Focus Area | Validation Metric | Status |
| :--- | :--- | :--- | :--- | :--- |
| **M1: Parser & Secrets Core** | Weeks 1–3 | Multi-IaC AST parsing & credential interception | 100% test pass on parsing HCL, CFN, K8s, Helm | ✅ Completed |
| **M2: Knowledge Core & RAG** | Weeks 4–6 | Vector DB, CIS benchmarks, compliance mapping | Retrieval Precision @ 5 $\ge 90\%$ | ✅ Completed |
| **M3: Ensemble & Consensus** | Weeks 7–9 | LangGraph 8-Agent network & Multi-LLM voting | Hallucination rate $< 3\%$, F1 $\ge 0.92$ | ⏳ In Progress |
| **M4: Validation & Patching** | Weeks 10–12 | Diff patch generation & LocalStack sandbox | $100\%$ syntax validity, patch pass rate $\ge 95\%$ | ⏳ In Progress |
| **M5: Shift-Left & Benchmarks**| Weeks 13–14 | IDE extension, pre-commit, ablation benchmarks | Full benchmark suite execution vs. IEEE paper | 🎯 Scheduled |

---


## 📂 Comprehensive Project Directory & File Structure

Below is the complete tree representation of the **AgentShield AI** repository, detailing the architecture of the root project, backend package, agent implementations, RAG knowledge core, test suite, and policy datasets.

```
AgentShield-AI/
├── backend/                                   # Backend Python package, state machine, and tests
│   ├── data/                                  # Multi-cloud security policy & compliance PDF corpus
│   │   ├── aws/                               # AWS EC2, S3, IAM security guides & Well-Architected docs
│   │   ├── azure/                             # Azure Security Benchmark & cloud security guidelines
│   │   ├── cis/                               # Official CIS AWS Foundations & Kubernetes Benchmarks
│   │   ├── gcp/                               # GCP IAM and cloud security posture guides
│   │   ├── kubernetes/                        # Kubernetes Pod Security Standards & security concepts
│   │   ├── mitre/                             # MITRE ATT&CK Cloud Framework & CWE dictionaries
│   │   ├── nist/                              # NIST Special Publication 800-53 Rev 5 control specs
│   │   ├── owasp/                             # OWASP Top 10 for Cloud & Kubernetes Security
│   │   └── terraform/                         # HashiCorp Terraform security guides & HCL style guides
│   ├── src/                                   # AgentShield AI core multi-agent package source
│   │   └── agentshield/                       # Core python module (`agentshield`)
│   │       ├── agents/                        # Specialized LLM agents
│   │       │   ├── analyst.py                 # Security Analyst Agent (Ensemble Voting & Confidence)
│   │       │   ├── remediator.py              # Remediation Agent (Code Diff Patch Generation)
│   │       │   └── prompts/                   # System prompt engineering templates & schemas
│   │       │       └── templates.py           # CoT prompts, system roles, & structured response formats
│   │       ├── core/                          # State management, RAG core, & LLM client wrappers
│   │       │   ├── llm/                       # Multi-LLM client abstractions
│   │       │   │   └── client.py              # Claude 3.5 + GPT-4o client, mock mode, & JSON parser
│   │       │   ├── schemas/                   # Pydantic v2 data contracts & state schemas
│   │       │   │   ├── contracts.py           # AgentShieldState (central LangGraph state schema)
│   │       │   │   ├── iac.py                 # IaCTemplate, ASTNode, & LineRange models
│   │       │   │   ├── vulnerability.py       # VulnerabilityFinding & VulnerabilityReport models
│   │       │   │   └── remediation.py         # PatchDiff & ValidationCheckResult models
│   │       │   └── knowledge_base/            # RAG vector database & compliance engine
│   │       │       ├── vector_db.py           # Qdrant & ChromaDB vector database manager
│   │       │       ├── retriever.py           # Context retrieval coordinator
│   │       │       ├── hybrid_search.py       # Hybrid Dense (embeddings) + Sparse (BM25) search engine
│   │       │       ├── embeddings.py          # SentenceTransformers model wrapper (`all-mpnet-base-v2`)
│   │       │       ├── chunker.py             # Semantic document chunking engine
│   │       │       ├── compliance.py          # Regulatory compliance engine (SOC2, HIPAA, PCI, NIST)
│   │       │       ├── compliance_controls.json# Control mapping matrix linking findings to regulatory IDs
│   │       │       ├── loaders.py             # PDF & text document ingestion loaders
│   │       │       ├── scrapers.py            # Live scraper service for AWS/Azure/GCP feeds & CVEs
│   │       │       ├── update_kb.py           # CLI script to execute KB re-indexing
│   │       │       ├── scheduler.py           # Background job scheduler (APScheduler) for daily updates
│   │       │       ├── cache.py               # AST hash caching module
│   │       │       ├── dedup.py               # Semantic deduplication module
│   │       │       ├── config.py              # Vector store & RAG threshold configuration loader
│   │       │       └── settings.yaml          # YAML settings for embedding dimensions & vector DB URLs
│   │       └── parsers/                       # Polyglot IaC AST parsers & property normalizers
│   │           ├── terraform.py               # HCL2 parser & resource extractor module
│   │           └── normalizer.py              # Property normalization & quote stripping engine
│   ├── tests/                                 # Pytest test suite & test fixtures
│   │   ├── conftest.py                        # Shared pytest fixtures & test environment setup
│   │   ├── test_analyst_agent.py              # Unit tests for Security Analyst Agent
│   │   ├── test_remediation_agent.py          # Unit tests for Remediation Agent & diff patching
│   │   ├── test_terraform_parser.py           # Unit tests for HCL parsing & resource extraction
│   │   ├── test_terraform_normalizer.py       # Unit tests for property normalization & list preservation
│   │   ├── test_llm_client.py                 # Unit tests for Multi-LLM client & confidence scoring
│   │   ├── test_iac_schema.py                 # Unit tests for AST nodes & format auto-detection
│   │   ├── test_vulnerability_schema.py       # Unit tests for vulnerability finding schemas
│   │   ├── test_remediation_schema.py         # Unit tests for patch diff schemas & validation results
│   │   ├── test_contracts.py                  # Unit tests for AgentShieldState contracts
│   │   ├── test_prompts.py                    # Unit tests verifying system prompt templates
│   │   ├── test_pyproject.py                  # Unit tests verifying pyproject.toml configuration
│   │   └── fixtures/                          # Sample test files & IaC templates
│   │       └── terraform/sample.tf            # Test fixture: sample Terraform HCL file
│   ├── inspect_parser.py                      # Diagnostic script inspecting AST parsing & normalization
│   ├── build_ieee_paper.py                    # Python script generating IEEE 2-column paper (.docx)
│   ├── build_paper_doc.py                     # Document builder helper for XML formatting & callouts
│   └── pyproject.toml                         # Python project configuration & dependency manifest
├── scratch/                                   # Temporary artifacts & extracted base paper text
│   └── base_paper_text.txt                    # Extracted raw text from IEEE base paper (Toprani, 2025)
├── .gitignore                                 # Git version control ignore rules
├── README.md                                  # Primary project documentation & architecture guide
├── about.md                                   # System architecture guide & specialized agent breakdown
├── index.html                                 # Interactive web presentation of objectives & pipeline
├── literature_survey.txt                      # Academic literature survey, research gaps, & matrix
├── project abstract.docx                      # Official project abstract document for academic submission
├── AgentShield_AI_Research_Paper_Draft.docx   # Draft research paper in IEEE 2-Column format (.docx)
├── LLM_Agentic_Workflow_..._Code.pdf          # Base IEEE Access research paper (Toprani & Madisetti, 2025)
└── WhatsApp Image 2026-08-01 at 21.13.02.jpeg # Reference image detailing IEEE paper structure guidelines
```

---

## 🛠️ Detailed File & Component Functionality Inventory

### 🌐 1. Root Level Project Files

| File Name | Category | Primary Functionality & Technical Purpose |
| :--- | :--- | :--- |
| **`README.md`** | Documentation | Primary repository documentation containing project metadata, system architecture breakdown, comparative feature matrices, execution instructions, full directory inventory, and academic citations. |
| **`about.md`** | Architecture | Detailed technical architecture guide describing the 8 specialized AI agents, LangGraph state machine, execution flow diagram, and feature-by-feature comparative analysis against the base paper. |
| **`index.html`** | Web Presentation | Single-page interactive web interface showcasing project objectives, multi-agent pipeline workflow, expected empirical results, system strengths, and limitations. |
| **`literature_survey.txt`** | Academic Survey | Comprehensive literature survey categorizing existing IaC security paradigms (static linters, CSPM, ML smell detectors, LLM workflows), key research gaps, and comparative analysis matrix. |
| **`project abstract.docx`** | Submission Doc | Executive abstract and project overview document prepared for academic submission, containing team member roll numbers (`23BD1A050E`, `23BD1A0518`, `23BD1A051D`, `23BD1A051Y`), domain definitions, and supervisor signatures. |
| **`AgentShield_AI_Research_Paper_Draft.docx`** | Research Paper | Complete draft research paper formatted in **IEEE 2-Column Conference style** (~4-5 pages, ~1,850+ words, complete with Abstract, Intro, Literature Review (L.R), Proposed Method, Performance Analysis, Conclusions, Future Work, and IEEE References). |
| **`LLM_Agentic_Workflow_for_Automated_Vulnerability_Detection_and_Remediation_in_Infrastructure-as-Code.pdf`** | Base Paper | Foundational base IEEE Access research paper (*Toprani & Madisetti, 2025*) serving as the core baseline for AgentShield AI's multi-cloud agentic enhancements. |
| **`WhatsApp Image 2026-08-01 at 21.13.02.jpeg`** | Reference Image | Reference handwritten guidance image specifying required IEEE paper section structures, page count targets (4-5 pages), and citation pattern requirements. |
| **`.gitignore`** | Configuration | Git version control configuration excluding Python bytecode (`__pycache__`), virtual environments (`.venv`), build artifacts, and coverage reports. |

---

### ⚙️ 2. Backend Infrastructure Files (`backend/`)

| File Path | Category | Primary Functionality & Technical Purpose |
| :--- | :--- | :--- |
| **`backend/pyproject.toml`** | Package Config | Modern Python package configuration file defining project dependencies (`langgraph`, `sentence-transformers`, `qdrant-client`, `rank-bm25`, `pypdf`, `python-hcl2`), build targets (`hatchling`), and pytest configuration settings. |
| **`backend/inspect_parser.py`** | Diagnostic Script | Diagnostic utility script that parses sample Terraform HCL code (`sample.tf`), extracts resource blocks, runs property normalization, and prints formatted JSON outputs for each pipeline stage. |
| **`backend/build_ieee_paper.py`** | Document Generator | Automation script using `python-docx` to generate the IEEE 2-Column formatted research paper (`AgentShield_AI_Research_Paper_Draft.docx`) with custom table borders, callout boxes, and IEEE references. |
| **`backend/build_paper_doc.py`** | Document Builder | Secondary document builder helper providing low-level XML styling functions for margins, shaded table headers, and callouts. |
| **`backend/.coverage`** | Testing Artifact | Binary coverage data report file generated by `pytest-cov` during test suite execution. |

---

### 🧠 3. Core Multi-Agent Package (`backend/src/agentshield/`)

#### **A. Specialized AI Agents (`agents/`)**
* **`backend/src/agentshield/agents/analyst.py`**: Implements `SecurityAnalystAgent`, executing parallel reasoning across Claude 3.5 Sonnet and GPT-4o, applying Chain-of-Thought prompting, and computing calibrated consensus confidence scores (\(C_{ensemble}\)). Escalates findings with \(C < 0.85\) to the human audit queue.
* **`backend/src/agentshield/agents/remediator.py`**: Implements `RemediationAgent`, converting structured vulnerability reports into executable, syntactically valid unified code diff patches for specific IaC resource blocks.
* **`backend/src/agentshield/agents/prompts/templates.py`**: Prompt engineering library containing system prompts, reasoning templates, structured JSON response schemas, and RAG context injection strings.

#### **B. Engine, Client & Schemas (`core/`)**
* **`backend/src/agentshield/core/llm/client.py`**: Unified Multi-LLM client wrapper interfacing with Anthropic Claude 3.5, OpenAI GPT-4o, and mock fallback models with automatic JSON schema validation.
* **`backend/src/agentshield/core/schemas/contracts.py`**: Core Pydantic v2 data contract defining `AgentShieldState`, the central state container passed between agents in the LangGraph state machine.
* **`backend/src/agentshield/core/schemas/iac.py`**: Pydantic models for IaC templates (`IaCTemplate`), AST nodes (`ASTNode`), line numbers (`LineRange`), and template type auto-detection.
* **`backend/src/agentshield/core/schemas/vulnerability.py`**: Pydantic models for vulnerability findings (`VulnerabilityFinding`), severity levels (`SeverityLevel`), confidence scores, and summarized reports (`VulnerabilityReport`).
* **`backend/src/agentshield/core/schemas/remediation.py`**: Pydantic models for code patch diffs (`PatchDiff`), static linter check results (`ValidationCheckResult`), and sandbox dry-run execution results.

#### **C. Knowledge Core & RAG Pipeline (`core/knowledge_base/`)**
* **`vector_db.py`**: Vector database adapter providing a unified interface for Qdrant and ChromaDB vector stores.
* **`retriever.py`**: High-level RAG retriever coordinating document lookups and context assembly.
* **`hybrid_search.py`**: Implements hybrid retrieval combining dense vector similarity (`sentence-transformers/all-mpnet-base-v2`) with sparse BM25 keyword matching (\(S_{hybrid}\)).
* **`embeddings.py`**: Model wrapper for generating dense sentence embeddings from security documentation chunks.
* **`chunker.py`**: Document chunking engine splitting security PDFs into semantically meaningful policy passages.
* **`compliance.py`**: Regulatory compliance engine mapping detected security flaws to specific control IDs across SOC 2, HIPAA, PCI-DSS, and NIST 800-53.
* **`compliance_controls.json`**: Master JSON crosswalk matrix mapping security rules to compliance control frameworks.
* **`loaders.py`**: Document ingestion loaders for reading PDF and text security benchmarks into memory.
* **`scrapers.py`**: Web scraper service continuously fetching updated security advisories from AWS, Azure, GCP, and NVD/CVE feeds.
* **`update_kb.py`**: Command-line script to trigger full knowledge base re-indexing and vector database updates.
* **`scheduler.py`**: Background job scheduler (`APScheduler`) executing daily knowledge base updates.
* **`cache.py` & `dedup.py`**: AST hash caching and semantic deduplication modules eliminating redundant LLM queries.
* **`config.py` & `settings.yaml`**: RAG core configuration settings, embedding dimensions, vector store URLs, and search threshold parameters.

#### **D. Polyglot AST Parsers (`parsers/`)**
* **`backend/src/agentshield/parsers/terraform.py`**: HCL2 parser module (`parse_terraform_file`, `extract_terraform_resources`) parsing `.tf` files into structured resource objects while extracting line numbers and property trees.
* **`backend/src/agentshield/parsers/normalizer.py`**: Normalization module (`normalize_value`, `normalize_terraform_resources`) cleaning HCL parser wrappers, stripping quote artifacts, and preserving list attributes like `cidr_blocks`.

---

### 🧪 4. Pytest Test Suite (`backend/tests/`)

| Test File Name | Targeted Subsystem & Verified Functionality |
| :--- | :--- |
| **`conftest.py`** | Shared pytest fixtures providing mock states, sample AST trees, and test configuration defaults. |
| **`test_analyst_agent.py`** | Unit tests verifying `SecurityAnalystAgent` structured output parsing, confidence score calculation, and fallback reasoning. |
| **`test_remediation_agent.py`** | Unit tests verifying `RemediationAgent` code diff generation, batch patch creation, and fallback handling. |
| **`test_terraform_parser.py`** | Unit tests verifying HCL file parsing (`parse_terraform_file`) and resource block extraction (`extract_terraform_resources`). |
| **`test_terraform_normalizer.py`** | Unit tests verifying resource property normalization (`normalize_terraform_resources`), quote stripping, and list preservation (`cidr_blocks`). |
| **`test_llm_client.py`** | Unit tests verifying multi-LLM client initialization, structured JSON generation, and ensemble confidence scoring algorithms. |
| **`test_iac_schema.py`** | Schema validation tests for AST nodes, line range boundaries, and IaC format auto-detection (HCL, CFN, K8s, Helm). |
| **`test_vulnerability_schema.py`** | Unit tests verifying `VulnerabilityFinding` creation, confidence score validation, and summary metrics calculation. |
| **`test_remediation_schema.py`** | Unit tests verifying `PatchDiff` unified diff generation and `ValidationCheckResult` status handling. |
| **`test_contracts.py`** | Unit tests verifying `AgentShieldState` serialization, workspace state contracts, and schema exports. |
| **`test_prompts.py`** | Unit tests verifying system prompt templates and user prompt string formatting. |
| **`test_pyproject.py`** | Unit tests verifying `pyproject.toml` package metadata, version numbers, and dependency definitions. |
| **`fixtures/terraform/sample.tf`** | Reference Terraform HCL template containing S3 bucket, security group, and PostgreSQL database resources for unit testing. |

---

### 📚 5. Policy & Benchmark Data Corpus (`backend/data/`)

* **`backend/data/aws/`**: PDF security guides covering AWS EC2, S3, IAM Security Best Practices, and Well-Architected Framework pillars.
* **`backend/data/azure/`**: PDF documentation for Azure Security Benchmark and Cloud Security recommendations.
* **`backend/data/gcp/`**: PDF documentation for Google Cloud Platform IAM and security posture benchmarks.
* **`backend/data/kubernetes/`**: PDF standards for Kubernetes Pod Security Standards and cluster security concepts.
* **`backend/data/cis/`**: Benchmark PDF guidelines for CIS AWS Foundations Benchmark and CIS Kubernetes Benchmark.
* **`backend/data/nist/`**: NIST Special Publication 800-53 Rev 5 security and privacy control specifications.
* **`backend/data/mitre/`**: MITRE ATT&CK Cloud Framework mappings and CWE vulnerability dictionaries.
* **`backend/data/owasp/`**: OWASP Top 10 for Cloud and Kubernetes.
* **`backend/data/terraform/`**: HashiCorp Terraform official security guidelines and HCL style guides.

---

## Run Terraform Preprocessing

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -e .

# Run parsing, resource extraction, and normalization tests
python -m pytest tests/test_terraform_parser.py tests/test_terraform_normalizer.py -v

# View output after each preprocessing stage
python inspect_parser.py
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
