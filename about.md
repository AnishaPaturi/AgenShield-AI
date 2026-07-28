## 🏗️ AgentShield AI Autonomous Architecture

  Unlike the 3-agent linear pipeline of the base paper, AgentShield AI uses LangGraph to manage a
  stateful, non-linear multi-agent orchestration framework with 8 specialized agents:

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
    
  ### Specialized Agents in AgentShield AI:

  1. Manager/Router Agent: Orchestrates execution state and distributes workloads.
  2. Hybrid AST Parser Agent: Parses HCL (Terraform), CloudFormation (JSON/YAML), Kubernetes (YAML), and
  Helm; extracts ASTs and pre-evaluates dynamic parameters/conditionals to eliminate parsing ambiguity.
  3. Secrets Scanner Agent: Runs integrated Gitleaks and TruffleHog engines to intercept hardcoded API
  credentials.
  4. RAG-Query Agent: Connects to Qdrant/ChromaDB populated with multi-cloud policies and compliance
  mapping rules.
  5. Security Analyst Agent: Performs Multi-LLM Ensemble Voting (e.g., Claude 3.5 + GPT-4o) and calculates
  calibrated confidence scores. Low-confidence findings are routed to a human review queue.
  6. Remediation Agent: Generates executable code diff patches instead of text explanations.
  7. Code & Sandbox Validator Agent: Performs syntax verification (terraform validate, cfn-lint) and
  executes runtime deployment checks inside a local LocalStack sandbox.
  8. Report Agent: Formats unified security reports mapped to compliance frameworks and stores developer
  feedback for continuous prompt tuning.
  ──────
   📊 Part 3: Comparative Analysis 

   Feature / Metric   | Base Paper (Toprani & Madise… | AgentShield AI (Proposed Existing System)
  --------------------|-------------------------------|---------------------------------------------------
   Analysis Timing    | Pre-deployment (CI/CD)        | Shift-Left (IDE + Pre-commit + CI/CD + Live
                      |                               | Drift)
   Cloud & IaC Scope  | AWS CloudFormation only       | AWS, Azure, GCP across Terraform, CloudFormation,
                      |                               | K8s, & Helm
   Reasoning Engine   | Single-LLM (Claude 3.5        | AST Parsing + RAG + Multi-LLM Ensemble (Claude +
                      | Sonnet)                       | GPT-4o)
   Remediation Output | Text explanations only        | Syntax & Sandbox-Validated Code Diff Patches
   Secrets Scanning   | ❌ None                       | Dedicated Secrets Agent (Gitleaks + TruffleHog
                      |                               | engines)
   Validation Harness | ❌ None                       | Static Linters + LocalStack Runtime Sandbox
                      |                               | Testing
   Compliance Mapping | ❌ None                       | Automated mapping to SOC 2, HIPAA, PCI-DSS, &
                      |                               | NIST 800-53
   Developer Feedback | ❌ None                       | Interactive feedback loop & negative-shot prompt
                      |                               | adaptation