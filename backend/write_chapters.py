"""
write_chapters.py
Appends Chapter 1, 2, 3, and 4 to the docx document with rich academic text,
detailed explanations, equations, tables, and images from Review-AgentSheild-AI.pptx.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

IMG_DIR = Path("docs/college/extracted_images")

def format_run(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)

def add_h1(doc, text):
    p = doc.add_paragraph(style='Heading 1')
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=16, bold=True)
    return p

def add_h2(doc, text):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=14, bold=True)
    return p

def add_h3(doc, text):
    p = doc.add_paragraph(style='Heading 3')
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=13, bold=True)
    return p

def add_p(doc, text, bold_prefix=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        format_run(r_pre, font_name="Times New Roman", size_pt=12, bold=True)
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=12, bold=False)
    return p

def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Paragraph')
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        format_run(r_pre, font_name="Times New Roman", size_pt=12, bold=True)
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=12, bold=False)
    return p

def add_figure(doc, img_filename, caption_text, width_in=6.4):
    img_path = IMG_DIR / img_filename
    if not img_path.exists():
        print(f"Warning: Image {img_path} not found!")
        return None
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(14)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(str(img_path), width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(12)
    p_cap.paragraph_format.keep_with_next = True
    r_cap = p_cap.add_run(caption_text)
    format_run(r_cap, font_name="Times New Roman", size_pt=11, bold=True, italic=True)
    return p_img

def append_all_chapters(doc):
    print("Writing Chapter 1: Introduction...")
    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_h1(doc, "CHAPTER - 1")
    add_h1(doc, "INTRODUCTION")

    add_h2(doc, "1.1 Purpose of the Project")
    add_p(doc, 
        "Modern cloud infrastructure engineering has undergone a fundamental transformation from manual, ad-hoc console configurations "
        "to declarative Infrastructure-as-Code (IaC) blueprints. Technologies such as HashiCorp Terraform, AWS CloudFormation, Kubernetes "
        "manifests, and Helm charts allow organizations to define complex multi-tier topologies—including Virtual Private Clouds (VPCs), "
        "identity access boundaries, security groups, distributed container clusters, and object storage tiers—in machine-readable domain-specific "
        "languages (DSLs). These blueprints are automatically executed by automated Continuous Integration and Continuous Deployment (CI/CD) pipelines "
        "to provision thousands of heterogeneous multi-cloud resources within seconds, ensuring consistency and eliminating manual setup drift."
    )
    add_p(doc, 
        "However, because IaC templates serve as directly executable blueprints, any latent security misconfiguration codified at the code layer "
        "instantly replicates across production cloud infrastructure. Critical vulnerabilities—including unrestricted security group ingress (allowing "
        "0.0.0.0/0 on sensitive ports like 22 SSH or 3389 RDP), unencrypted object storage buckets (Amazon S3, Azure Blob, Google Cloud Storage), "
        "overly permissive IAM wildcard privileges ('Action': '*'), and accidentally committed hardcoded credentials (API keys, JWT tokens, AWS access keys)—"
        "represent the leading entry points for catastrophic enterprise security breaches. Industry threat intelligence reports establish that over 73% of "
        "cloud security incidents stem from preventable IaC flaws, while 65% of audited cloud repositories inadvertently leak plaintext credentials within configuration attributes."
    )
    add_p(doc, 
        "The purpose of this project, AgentShield AI, is to design, implement, and validate an autonomous, stateful, multi-agent artificial intelligence framework "
        "specifically engineered for multi-cloud IaC security. AgentShield AI bridges the gap between static code analysis, semantic AI reasoning, and runtime sandbox "
        "verification. By utilizing specialized AI agents coordinated through a formal state machine (LangGraph), the system automates the complete lifecycle: "
        "ingesting multi-cloud templates, constructing Abstract Syntax Trees (ASTs) and dependency graphs, intercepting exposed secrets using entropy metrics, "
        "retrieving compliance standards (CIS Benchmarks, NIST SP 800-53, PCI-DSS) via hybrid dense-sparse vector RAG, evaluating vulnerabilities through a "
        "multi-LLM consensus engine, synthesizing syntactically valid Unified Git Diff patches, and testing the patches inside an isolated two-tier sandbox harness "
        "before recommending deployment to developers."
    )

    add_h2(doc, "1.2 Problem with Existing Systems")
    add_p(doc, 
        "Current industry practices and tooling for securing Infrastructure-as-Code suffer from four fundamental systemic deficiencies:"
    )
    add_bullet(doc, 
        "Syntactic Myopia and False-Positive Cascades: Leading static analysis tools (such as Checkov, tfsec, KICS, and Trivy) inspect templates using regular "
        "expression matching and shallow abstract syntax trees. They evaluate rules in isolation without understanding cross-resource attribute flows, variable interpolations, "
        "or dynamic local evaluations. Consequently, they suffer from high false-positive rates (ranging between 32% and 48%), leading to severe alert fatigue and "
        "developer skepticism.", bold_prefix="1. "
    )
    add_bullet(doc, 
        "Open-Loop Diagnostic Disconnect: Conventional static scanners and Policy-as-Code engines (e.g., Open Policy Agent Rego, Sentinel) merely diagnose violations; "
        "they cannot synthesize, test, or apply remediation code. Fixing identified misconfigurations remains an entirely manual, labor-intensive responsibility, "
        "resulting in an industry-average Mean Time to Remediation (MTTR) exceeding 24.6 days.", bold_prefix="2. "
    )
    add_bullet(doc, 
        "Stochastic Hallucination in Unconstrained Generative LLMs: While recent efforts leverage Large Language Models (LLMs) to inspect code, single-model zero-shot "
        "generative architectures frequently hallucinate non-existent resource arguments, generate deprecated provider syntax, or produce patches that break topological "
        "resource dependencies, resulting in deployment failure rates up to 28.8%.", bold_prefix="3. "
    )
    add_bullet(doc, 
        "High-Entropy Token Collisions in Secret Scanning: Signature-based secret scanners fail against obfuscated credentials, while uncalibrated Shannon entropy "
        "scanners produce unmanageable false alarms on structured pseudo-random strings like UUIDs, hexadecimal resource IDs, and base64 configuration blocks.", bold_prefix="4. "
    )

    add_h2(doc, "1.3 Proposed System")
    add_p(doc, 
        "To overcome the limitations of conventional static linters and single-model LLM approaches, AgentShield AI introduces an autonomous, decentralized, "
        "event-driven multi-agent framework comprising eight specialized autonomous agents operating over an immutable, Pydantic v2 typed shared execution context graph (Γ):"
    )
    add_bullet(doc, "Validates template integrity via SHA-256 digests, auto-detects the IaC DSL format (Terraform, CloudFormation, Kubernetes, Helm), initializes workspace state, and dispatches parallel analysis tasks.", bold_prefix="• Agent 1 (Orchestration & Ingestion Router): ")
    add_bullet(doc, "Parses declarative templates into structured Concrete Syntax Trees (CSTs) and AST representations, extracting declared properties, tracking variable scopes, and building directed resource dependency graphs.", bold_prefix="• Agent 2 (AST & Graph-Theoretic Parser): ")
    add_bullet(doc, "Dual-engine secret scanner combining pattern signatures (AWS keys, GitHub tokens, JWTs, private keys) with sliding-window Shannon entropy calculations to identify and redact sensitive credentials prior to LLM exposure.", bold_prefix="• Agent 3 (Dual-Engine Secret Interceptor): ")
    add_bullet(doc, "Performs hybrid dense semantic search (Qdrant HNSW vector store with 384-dimensional embeddings) and sparse BM25 keyword search over CIS Cloud Benchmarks, NIST SP 800-53, and PCI-DSS compliance repositories, fusing scores via Reciprocal Rank Fusion (RRF).", bold_prefix="• Agent 4 (Hybrid RAG Knowledge Retrieval Engine): ")
    add_bullet(doc, "Prompts frontier LLMs concurrently, evaluating security findings through cross-model consensus voting and confidence calibration to structurally suppress individual model hallucinations.", bold_prefix="• Agent 5 (Security Analyst & Consensus Engine): ")
    add_bullet(doc, "Generates targeted, minimal Unified Git Diff code patches specifically scoped to the vulnerable line offsets, avoiding unnecessary template refactoring.", bold_prefix="• Agent 6 (Auto-Patch Remediation Agent): ")
    add_bullet(doc, "Executes candidate patches through a two-tier verification harness comprising static syntax checking (terraform validate, tflint) and simulated runtime dry-run provisioning in an isolated LocalStack sandbox, executing automated rollback and self-healing retry cycles.", bold_prefix="• Agent 7 (Code & Sandbox Validator Agent): ")
    add_bullet(doc, "Compiles comprehensive security findings into multi-format compliance reports (JSON, Markdown, HTML, SARIF, and PDF), maps CWE/CVSS/MITRE ATT&CK vectors, routes low-confidence findings to a human audit queue, and captures developer accept/reject feedback for dynamic prompt adaptation.", bold_prefix="• Agent 8 (Reporting, Audit Queue & Feedback Agent): ")

    add_h2(doc, "1.4 Scope of the Project")
    add_p(doc, 
        "The functional and operational scope of AgentShield AI encompasses:"
    )
    add_bullet(doc, "Multi-Cloud Coverage: Broad cross-platform support across Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), and container orchestration environments managed by Kubernetes and Helm.", bold_prefix="• ")
    add_bullet(doc, "Multi-Format Polyglot Parsing: Native handling of Terraform HCL (.tf), AWS CloudFormation YAML and JSON, Kubernetes Pod/Deployment/Service manifests (.yaml), and Helm chart packages.", bold_prefix="• ")
    add_bullet(doc, "Shift-Left CI/CD & IDE Integration: Frictionless pre-commit enforcement via a lightweight Git pre-commit hook (agentshield-hook), real-time inline diagnostics via a VS Code extension, a terminal triage CLI (agentshield-triage), and an interactive React-based SOC Control Room dashboard.", bold_prefix="• ")
    add_bullet(doc, "Closed-Loop Self-Healing: Dynamic feedback loop between validator diagnostics and remediation agents, allowing up to three automated self-correction retries when a patch fails syntax or sandbox validation.", bold_prefix="• ")
    add_bullet(doc, "Audit-Ready Compliance: Automated mapping of detected misconfigurations to industry-standard regulatory frameworks including CIS Foundations Benchmarks, NIST SP 800-53 Rev. 5, SOC 2, HIPAA, and MITRE ATT&CK Cloud Matrix.", bold_prefix="• ")

    add_h2(doc, "1.5 Architecture Diagram")
    add_p(doc, 
        "The architectural blueprint of AgentShield AI establishes a stateful, event-driven multi-agent pipeline designed for modularity, resilience, and high throughput. "
        "Figure 1.1 illustrates the end-to-end architecture flow, tracing the lifecycle of an IaC template from developer ingestion through multi-agent analysis, RAG context enrichment, "
        "consensus voting, automated code patching, sandbox validation, and compliance delivery."
    )
    add_figure(doc, "slide_11_img_11.png", "Figure 1.1: End-to-End Multi-Agent Architecture Flow of AgentShield AI", width_in=6.4)
    add_p(doc, 
        "As illustrated in Figure 1.1, the architecture is partitioned into eight modular functional subsystems:"
    )
    add_bullet(doc, "Developers, DevOps engineers, and CI managers submit IaC files (.tf, .yaml, .json) through command-line interfaces, Git pre-commit hooks, or the web dashboard. This triggers the LangGraph Orchestrator (Manager Agent), which initializes the shared execution state.", bold_prefix="1. User & CI/CD Layer: ")
    add_bullet(doc, "The Manager Agent routes the template concurrently to the Hybrid AST Parser Agent (which constructs the AST and builds the resource dependency graph) and the Secrets Scanner Agent (which identifies and redacts credentials using pattern matching and Shannon entropy).", bold_prefix="2. Ingestion & Analysis Subsystem: ")
    add_bullet(doc, "The Compound Risk Orchestrator receives normalized AST resources and masked templates, triggering the RAG Query Agent. The RAG subsystem queries local Qdrant vector collections and BM25 lexical indices over CIS, NIST, and cloud security advisories, enriching the AST with pertinent regulatory controls.", bold_prefix="3. Knowledge Retrieval & RAG Hub: ")
    add_bullet(doc, "The Security Analyst Agent dispatches prompts in parallel to frontier LLM engines (Claude 3.5 Sonnet, GPT-4o, and Gemini). An agreement voting engine evaluates consensus; findings meeting the confidence threshold (>= 0.85) proceed to auto-patching, while ambiguous findings escalate to the Human-in-the-Loop Audit Queue.", bold_prefix="4. Multi-LLM Ensemble Engine: ")
    add_bullet(doc, "The Remediation Agent synthesizes minimal Unified Git Diff patches. Patches are forwarded to the Validation Harness, which executes static syntax checks (terraform validate, tflint) followed by runtime provisioning dry-runs inside an isolated LocalStack sandbox container.", bold_prefix="5. Remediation & Validation Harness: ")
    add_bullet(doc, "If validation fails (J1 or J2 failure paths), the compiler error trace is routed back to the Remediation Agent for up to three self-healing iterations. Upon passing, the Report Generator compiles multi-format audits, delivers PRs to developers, and logs decisions into the Developer Feedback Store for continuous few-shot prompt adaptation.", bold_prefix="6. Delivery & Continuous Learning: ")

    add_p(doc, 
        "To provide a granular operational perspective of each subsystem's responsibilities, Figure 1.2 presents the detailed six-stage architectural breakdown."
    )
    add_figure(doc, "slide_12_img_12.png", "Figure 1.2: Six-Stage Subsystem Architecture & Execution Trace", width_in=6.4)
    add_p(doc, 
        "Figure 1.2 delineates the operational contracts governing each stage: Stage 1 handles multi-cloud template intake and sanitization; Stage 2 achieves parallel syntax tree generation and credential masking; "
        "Stage 3 performs context-aware risk retrieval via vector similarity and BM25 rank fusion; Stage 4 executes parallel LLM inference, structured JSON output validation, and consensus scoring; "
        "Stage 5 conducts two-tier static and runtime sandbox validation with automated self-healing; and Stage 6 executes atomic code patch application, report compilation, and deployment-ready delivery."
    )

    print("Writing Chapter 2: Literature Survey...")
    # =========================================================================
    # CHAPTER 2: LITERATURE SURVEY
    # =========================================================================
    add_h1(doc, "CHAPTER – 2")
    add_h1(doc, "LITERATURE SURVEY")

    add_h2(doc, "2.1 Overview & Evolution of IaC Security")
    add_p(doc, 
        "The rapid migration of enterprise workloads to public cloud platforms has established declarative Infrastructure-as-Code (IaC) as the de facto standard "
        "for provisioning virtual networks, compute instances, identity boundaries, and data stores. While IaC eliminates configuration drift and enforces deterministic "
        "deployments, it fundamentally shifts cloud security boundaries to the software development lifecycle. Consequently, securing cloud infrastructure prior to "
        "deployment ('Shift-Left' security) has become a paramount research frontier."
    )

    add_h2(doc, "2.2 In-Depth Review of Base Paper (Toprani & Madisetti, IEEE Access 2025)")
    add_p(doc, 
        "The theoretical foundation of this work builds upon the seminal research by Dheer Toprani and Vijay K. Madisetti titled "
        "\"LLM Agentic Workflow for Automated Vulnerability Detection and Remediation in Infrastructure-as-Code\", published in IEEE Access (Volume 13, 2025). "
        "Figure 2.1 displays the publication header and abstract of this foundation research article."
    )
    add_figure(doc, "slide_3_img_3.png", "Figure 2.1: Base Research Article in IEEE Access (Toprani & Madisetti, 2025)", width_in=5.0)
    add_p(doc, 
        "Toprani and Madisetti proposed an AI-driven, multi-agent pre-deployment workflow combining Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) "
        "to detect context-sensitive vulnerabilities in cloud infrastructure templates. Their core objective was to overcome the rigidity of rule-based scanners (e.g., Checkov, CDK-Nag) "
        "and bridge the gap left by post-deployment Cloud Security Posture Management (CSPM) tools. Figure 2.2 provides a structured breakdown of their methodology, architecture, "
        "experimental results, and limitations."
    )
    add_figure(doc, "slide_3_img_2.png", "Figure 2.2: Base Paper Objective, Architecture, and Performance Benchmark", width_in=6.4)
    add_p(doc, 
        "The architecture introduced by Toprani and Madisetti utilized an AWS-specific RAG retrieval agent coupled with an OpenSearch vector database and Amazon Titan embeddings. "
        "Vulnerability detection was delegated to a single Claude 3.5 Sonnet agent, which generated natural language security recommendations and Markdown reports. "
        "Empirical benchmarks reported an 85% vulnerability detection rate with an estimated 15% false-positive rate across 10 sample AWS CloudFormation configurations, "
        "with an execution latency of 80–100 seconds per template."
    )
    add_p(doc, 
        "Despite its foundational merits, our analysis identifies several critical architectural limitations in the base paper:"
    )
    add_bullet(doc, "Single Cloud and Single IaC Format: The framework was strictly confined to AWS CloudFormation templates, lacking support for HashiCorp Terraform, Kubernetes, Helm, Azure, or GCP.", bold_prefix="1. ")
    add_bullet(doc, "Single-LLM Hallucination Vulnerability: Utilizing a single LLM without cross-model consensus voting exposed the system to unverified hallucinations and non-deterministic policy judgments.", bold_prefix="2. ")
    add_bullet(doc, "Absence of Automated Remediation: The system generated descriptive text advice rather than executable, syntactically verified code patches.", bold_prefix="3. ")
    add_bullet(doc, "Zero Validation Harness: Generated advice was not subjected to static compiler verification or sandbox dry-run execution, risking runtime provisioning failures.", bold_prefix="4. ")
    add_bullet(doc, "Omission of Secret Scanning: The workflow lacked credential interception capabilities, potentially exposing sensitive tokens to external LLM prompts.", bold_prefix="5. ")

    add_h2(doc, "2.3 Traditional Rule-Based Static Analyzers")
    add_p(doc, 
        "Static Application Security Testing (SAST) for IaC includes mature open-source analyzers such as Checkov (Bridgecrew/Palo Alto), tfsec (Aqua Security), "
        "KICS (Checkmarx), and Trivy. Checkov verifies configurations against extensive CIS Benchmark rulesets using Python-based AST inspections; tfsec specializes in "
        "Terraform HCL structural analysis; KICS employs Open Policy Agent (OPA) Rego queries over JSON representations; and Trivy scans multiple targets including container images "
        "and IaC manifests. While these linters execute rapidly (1–5 seconds per file), they lack structural semantic understanding of ternary conditionals, dynamic local module "
        "references, and inter-resource dependencies. As a result, they produce severe false-positive cascades (32%–48%) and cannot synthesize code patches."
    )

    add_h2(doc, "2.4 Cloud Security Posture Management (CSPM) and Runtime Scanners")
    add_p(doc, 
        "Enterprise CSPM solutions (e.g., Prisma Cloud, AWS Security Hub, Microsoft Defender for Cloud) operate by continuously polling live cloud provider APIs to detect "
        "deployed configuration drift. While highly effective at identifying exposed production assets, CSPM operates reactively after infrastructure is already provisioned, "
        "exposing organizations to exploitation windows before security teams can intervene."
    )

    add_h2(doc, "2.5 Machine Learning & Neural Approaches (GLITCH Framework)")
    add_p(doc, 
        "Recent academic studies have explored machine learning for IaC defect detection. The GLITCH framework (Mlali et al., 2024) utilizes supervised learning and "
        "structural code metrics to identify code smells and security weaknesses in Puppet and Chef scripts. However, traditional ML models require massive labeled datasets, "
        "struggle with emerging multi-cloud resource schemas, and lack generative capabilities required for automated patch synthesis."
    )

    add_h2(doc, "2.6 Secret Detection Mechanisms (Gitleaks, TruffleHog, Shannon Entropy)")
    add_p(doc, 
        "Dedicated secret scanners like Gitleaks and TruffleHog employ regex signatures to identify structured credentials (such as AWS keys starting with 'AKIA' or GitHub tokens). "
        "To capture unstructured passwords and private keys, statistical tools apply Shannon entropy formulas. However, uncalibrated entropy models trigger heavy false positives "
        "on random hashes, GUIDs, and base64 strings, necessitating AST-guided lexical scoping."
    )

    add_h2(doc, "2.7 Existing System Analysis: Workflow, Advantages, and Limitations")
    add_p(doc, 
        "To establish a clear comparative baseline, Figure 2.3 synthesizes the literature landscape, comparing rule-based linters, ML models, the base paper, and our proposed approach."
    )
    add_figure(doc, "slide_4_img_4.png", "Figure 2.3: Comparative Analysis of State-of-the-Art Approaches in Literature", width_in=6.4)
    add_p(doc, 
        "Figure 2.4 details the workflow of existing LLM-assisted systems (as embodied by Toprani & Madisetti 2025), illustrating the linear pipeline from template ingestion "
        "through OpenSearch RAG retrieval to single-model Claude 3.5 Sonnet analysis."
    )
    add_figure(doc, "slide_5_img_5.png", "Figure 2.4: Existing System Architecture Workflow and Limitations", width_in=6.4)
    add_p(doc, 
        "Figure 2.5 highlights the core advantages of existing systems, including automated vulnerability discovery, multi-agent concept division, and natural-language "
        "context-aware reasoning."
    )
    add_figure(doc, "slide_6_img_6.png", "Figure 2.5: Advantages of the Existing System", width_in=6.4)
    add_p(doc, 
        "Figure 2.6 outlines the critical disadvantages and architectural bottlenecks of existing systems, including heavy LLM hallucination risks, high computational costs, "
        "lack of automated patch generation, absence of sandbox validation, and zero continuous learning mechanisms."
    )
    add_figure(doc, "slide_7_img_7.png", "Figure 2.6: Architectural Disadvantages and Bottlenecks of Existing Systems", width_in=6.4)

    add_h2(doc, "2.8 Proposed System Innovations and Advantages")
    add_p(doc, 
        "AgentShield AI resolves the aforementioned research gaps through an end-to-end autonomous multi-agent architecture. Figure 2.7 outlines the core objectives "
        "and pipeline flow of the proposed system."
    )
    add_figure(doc, "slide_8_img_8.png", "Figure 2.7: Proposed System Objective and Key Pipeline Architecture", width_in=6.4)
    add_p(doc, 
        "Figure 2.8 and Table 2.1 illustrate the dimensional advantages of AgentShield AI compared to traditional static linters and the base paper."
    )
    add_figure(doc, "slide_9_img_9.png", "Figure 2.8: Architectural Advantages and Dimensional Comparison of Proposed Framework", width_in=6.4)

    add_h2(doc, "2.9 Trade-off and Disadvantage Analysis of Proposed Approach")
    add_p(doc, 
        "Engineering an advanced multi-agent system introduces deliberate architectural trade-offs. Figure 2.9 summarizes the computational, cost, and complexity "
        "considerations inherent in AgentShield AI alongside a comparative approach matrix."
    )
    add_figure(doc, "slide_10_img_10.png", "Figure 2.9: Trade-off and Disadvantage Analysis of Proposed Multi-Agent Approach", width_in=6.4)
    add_p(doc, 
        "As outlined in Figure 2.9, while AgentShield AI requires higher initial setup complexity and API compute resources than simple local regex scanners, "
        "it drastically reduces developer triage fatigue, eliminates single-model hallucinations, and provides mathematically verified, sandbox-tested code patches."
    )

    print("Writing Chapter 3: Software Requirement Specification...")
    # =========================================================================
    # CHAPTER 3: SOFTWARE REQUIREMENT SPECIFICATION
    # =========================================================================
    add_h1(doc, "CHAPTER - 3")
    add_h1(doc, "SOFTWARE REQUIREMENT SPECIFICATION")

    add_h2(doc, "3.1 Introduction to SRS")
    add_p(doc, 
        "This Software Requirements Specification (SRS) document provides a comprehensive, rigorous specification of the functional, non-functional, "
        "interface, and performance requirements for the AgentShield AI platform. It serves as the definitive engineering contract between software developers, "
        "security compliance officers, system architects, and university project evaluators."
    )

    add_h2(doc, "3.2 Role and Purpose of SRS")
    add_p(doc, 
        "The primary purpose of this SRS is to establish a verified blueprint for developing and evaluating an autonomous multi-agent IaC security framework. "
        "It defines the precise input formats, agent state contracts, consensus mechanisms, sandbox execution protocols, and reporting standards necessary "
        "to deliver automated shift-left security in multi-cloud DevSecOps pipelines."
    )

    add_h2(doc, "3.3 Requirements Specification Document")
    add_p(doc, 
        "Figure 3.1 details the functional architecture, target users, inputs, outputs, analysis agents, and security knowledge sources specified for AgentShield AI."
    )
    add_figure(doc, "slide_13_img_16.png", "Figure 3.1: Software Requirements Specification Functional & Agent Architecture", width_in=6.4)
    add_p(doc, 
        "As delineated in Figure 3.1, the system serves three primary user personas: Cloud & DevOps Engineers (who submit IaC code and review patches), "
        "Security & Compliance Auditors (who inspect attack paths and export regulatory reports), and DevSecOps Administrators (who configure consensus thresholds "
        "and manage organizational policies). The system accepts Terraform HCL, AWS CloudFormation, Kubernetes YAML, and Helm charts, producing structured vulnerability "
        "findings, Unified Git Diff patches, and audit-ready compliance documentation."
    )

    add_h2(doc, "3.4 Functional Requirements")
    add_p(doc, 
        "Figure 3.2 provides a consolidated overview of the eight core functional requirements (FR-01 to FR-08), non-functional quality attributes, and the software/hardware stack."
    )
    add_figure(doc, "slide_14_img_17.png", "Figure 3.2: Comprehensive Functional, Non-Functional, and Hardware/Software Requirements", width_in=6.4)
    add_p(doc, 
        "The system's eight formal functional requirements are specified as follows:"
    )
    add_bullet(doc, "The system shall ingest IaC templates (.tf, .yaml, .json) via REST API, pre-commit hook, or CLI, calculate a SHA-256 integrity hash, auto-detect the DSL format, and initialize the shared AgentShieldWorkspace state.", bold_prefix="• FR-01 (Multi-Format Ingestion): ")
    add_bullet(doc, "The system shall parse Terraform, CloudFormation, Kubernetes, and Helm manifests into structured AST representations, extract declared properties, normalize attribute values, and construct directed resource dependency graphs.", bold_prefix="• FR-02 (Polyglot AST & Dependency Parsing): ")
    add_bullet(doc, "The system shall scan templates for hardcoded credentials (AWS keys, GitHub tokens, JWTs, private keys) using regex signatures and sliding-window Shannon entropy, masking detected secrets before any external LLM prompt transmission.", bold_prefix="• FR-03 (Calibrated Secret Interception): ")
    add_bullet(doc, "The system shall execute hybrid semantic-lexical retrieval (combining Qdrant HNSW cosine similarity and BM25Okapi lexical scores via Reciprocal Rank Fusion) over CIS Benchmarks, NIST SP 800-53, and PCI-DSS knowledge repositories.", bold_prefix="• FR-04 (Hybrid Compliance RAG Retrieval): ")
    add_bullet(doc, "The system shall concurrently prompt frontier LLMs (Claude 3.5 Sonnet, GPT-4o, Gemini 2.0) with AST snippets and compliance context, computing cross-model consensus and calibrated confidence scores (auto-patch threshold >= 0.85).", bold_prefix="• FR-05 (Multi-LLM Ensemble Consensus): ")
    add_bullet(doc, "The system shall synthesize syntactically valid Unified Git Diff remediation patches specifically targeting vulnerable line offsets without modifying unrelated infrastructure attributes.", bold_prefix="• FR-06 (Automated Remediation Patch Generation): ")
    add_bullet(doc, "The system shall evaluate candidate patches through a two-tier verification harness comprising static linting (terraform validate, tflint, cfn-lint) and LocalStack sandbox dry-run execution, supporting up to 3 self-healing retry cycles upon error detection.", bold_prefix="• FR-07 (Two-Tier Sandbox Validation & Self-Healing): ")
    add_bullet(doc, "The system shall generate compliance reports across five standard formats (JSON, Markdown, HTML, SARIF v2.1.0, and PDF), route low-confidence findings to a human audit queue, and store developer accept/reject feedback for dynamic few-shot prompt adaptation.", bold_prefix="• FR-08 (Compliance Reporting & Feedback Loop): ")

    add_h2(doc, "3.5 Non-Functional Requirements")
    add_p(doc, 
        "The non-functional requirements define the quality attributes and operational constraints of the platform:"
    )
    add_bullet(doc, "The end-to-end scanning and analysis pipeline shall complete within 20 seconds for standard templates containing up to 500 lines of code.", bold_prefix="• Performance: ")
    add_bullet(doc, "Multi-model consensus and RAG grounding shall maintain a target false-positive rate below 5%, eliminating developer alert fatigue.", bold_prefix="• Accuracy: ")
    add_bullet(doc, "100% of detected plaintext secrets, passwords, and private keys must be intercepted and redacted prior to external API transmission.", bold_prefix="• Secret Protection: ")
    add_bullet(doc, "All candidate patch dry-runs must execute inside containerized LocalStack or mock sandboxes completely isolated from production cloud accounts.", bold_prefix="• Sandboxing: ")
    add_bullet(doc, "Upon encountering compiler syntax errors or lint breakages, the system shall autonomously trigger up to 3 iterative self-correction cycles.", bold_prefix="• Self-Healing: ")
    add_bullet(doc, "The FastAPI backend server and triage dashboard shall maintain a target operational uptime of 99.5%.", bold_prefix="• Availability: ")
    add_bullet(doc, "The architecture must support modular integration of additional IaC formats (e.g., Pulumi, Bicep) and custom organizational policy rules.", bold_prefix="• Extensibility: ")
    add_bullet(doc, "The Python backend shall maintain a minimum of 85% automated test coverage across all agent, parser, and API modules.", bold_prefix="• Maintainability: ")

    add_h2(doc, "3.6 Performance Requirements")
    add_p(doc, 
        "AgentShield AI enforces strict performance bounds across all components: REST API request handling must maintain sub-100ms response times for health and workspace "
        "queries; vector similarity lookups in Qdrant must execute in under 50ms; thread pool workers must limit parallel LLM timeouts to 60 seconds; and SQLite database transactions "
        "must utilize Write-Ahead Logging (WAL) mode to support concurrent read and write operations without database locking."
    )

    add_h2(doc, "3.7 Software Requirements")
    add_p(doc, 
        "The software architecture of AgentShield AI integrates modern, industrial-grade open-source technologies across every layer of the stack. "
        "Figure 3.3 illustrates the end-to-end system workflow across the five operational phases and the AgentShieldWorkspace state lifecycle."
    )
    add_figure(doc, "slide_15_img_18.png", "Figure 3.3: High-Level End-to-End System Workflow and Agent State Lifecycle", width_in=6.4)
    add_p(doc, 
        "The software dependencies and execution environments comprise:"
    )
    add_bullet(doc, "Python 3.12 or 3.13, FastAPI (ASGI web framework), Uvicorn (production ASGI server), Pydantic v2 (data validation and schema contracts), SQLite with WAL mode.", bold_prefix="• Backend Core: ")
    add_bullet(doc, "LangGraph (stateful agent execution graph), LangChain Core & Community (agent abstractions and text splitters).", bold_prefix="• Multi-Agent Framework: ")
    add_bullet(doc, "Qdrant Client (dense vector database), Sentence-Transformers ('all-MiniLM-L6-v2'), Rank-BM25 (sparse lexical scoring), PyPDF (PDF document extraction).", bold_prefix="• Vector Search & RAG: ")
    add_bullet(doc, "Python-HCL2 (Terraform parser), PyYAML (CloudFormation/Kubernetes parser), NetworkX (graph-theoretic attack-path modeling).", bold_prefix="• Parsers & Modeling: ")
    add_bullet(doc, "LocalStack Community Edition (AWS emulation), TFLint, Terraform CLI, CFN-Lint, Kube-Linter.", bold_prefix="• Validation & Sandboxing: ")
    add_bullet(doc, "ReportLab (PDF document generation), SARIF Tools, Rich (terminal UI formatting).", bold_prefix="• Reporting & Compliance: ")
    add_bullet(doc, "React 18, Vite 5, React Router v6, TailwindCSS / custom SOC Control Room styles.", bold_prefix="• Frontend Dashboard: ")

    add_h2(doc, "3.8 Hardware Requirements")
    add_p(doc, 
        "The platform is optimized for commodity developer workstations as well as enterprise cloud servers:"
    )
    add_bullet(doc, "Intel Core i5 / AMD Ryzen 5 (minimum 4 cores, 8 threads); Recommended: Intel Core i7 / AMD Ryzen 7 (8+ cores).", bold_prefix="• Processor: ")
    add_bullet(doc, "Minimum: 16 GB DDR4 RAM; Recommended: 32 GB RAM (accommodates concurrent LocalStack, Qdrant, and multi-model thread pools).", bold_prefix="• Memory: ")
    add_bullet(doc, "Minimum 20 GB free solid-state storage (SSD) for vector database embeddings, audit logs, and container images.", bold_prefix="• Storage: ")
    add_bullet(doc, "Broadband internet connection required for API communication with frontier LLM endpoints (OpenAI, Anthropic, Gemini, OpenRouter).", bold_prefix="• Network: ")
    add_bullet(doc, "Optional NVIDIA CUDA-compatible GPU (6GB+ VRAM) for accelerated local sentence-transformers embedding generation.", bold_prefix="• GPU (Optional): ")

    print("Writing Chapter 4: System Design...")
    # =========================================================================
    # CHAPTER 4: SYSTEM DESIGN
    # =========================================================================
    add_h1(doc, "CHAPTER – 4")
    add_h1(doc, "SYSTEM DESIGN")

    add_h2(doc, "4.1 Introduction to UML")
    add_p(doc, 
        "The Unified Modeling Language (UML) is the international standard visual modeling language used to specify, visualize, construct, and document "
        "the artifacts of software-intensive systems. In modern software engineering, UML provides a standardized vocabulary across structural views (class diagrams, "
        "deployment diagrams) and behavioral views (use case diagrams, sequence diagrams, statechart diagrams). In multi-agent autonomous systems, UML is essential "
        "for formally modeling decentralized state transitions, asynchronous message passing, and typed data contracts."
    )

    add_h2(doc, "4.2 UML Diagrams in AgentShield AI")
    add_p(doc, 
        "To provide a complete architectural specification, the system design of AgentShield AI is documented using five comprehensive UML diagrams: "
        "Use Case Diagram, Class Diagram, Sequence Diagram, State Chart Diagram, and Deployment Diagram."
    )

    add_h2(doc, "4.3 Use Case Diagram")
    add_p(doc, 
        "The Use Case Diagram defines the functional boundary of the AgentShield AI platform, illustrating interactions between human actors, external system actors, "
        "and the eleven core system use cases. Figure 4.1 presents the complete UML Use Case Diagram."
    )
    add_figure(doc, "slide_20_img_23.png", "Figure 4.1: UML Use Case Diagram for AgentShield AI Platform", width_in=6.4)
    add_p(doc, 
        "As detailed in Figure 4.1, the platform encompasses three human actor roles and four external system actors:"
    )
    add_bullet(doc, "DevOps / Cloud Developer: Submits IaC templates (UC-01), reviews vulnerability findings, and applies verified remediation patches.", bold_prefix="1. ")
    add_bullet(doc, "Security & Compliance Auditor: Reviews security findings, inspects attack-path graphs, and exports compliance reports across CIS, NIST, and HIPAA standards.", bold_prefix="2. ")
    add_bullet(doc, "System / DevSecOps Administrator: Configures consensus thresholds, manages API keys, sets automated retry budgets, and monitors agent telemetry.", bold_prefix="3. ")
    add_bullet(doc, "External System Actors: GitHub Actions CI/CD runner (triggers automated pull request scans), External LLM APIs (provide parallel model inference), LocalStack Sandbox (executes isolated AWS dry-runs), and Qdrant Vector DB (stores and queries compliance embeddings).", bold_prefix="4. ")
    add_p(doc, 
        "The diagram formally specifies mandatory functional inclusions (<<include>>) and conditional extensions (<<extend>>): "
        "UC-01 (Submit IaC Template) includes UC-02 (Parse AST & Build Dependency Graph) and UC-03 (Scan for Secrets). UC-05 (Analyze Vulnerabilities) includes UC-04 "
        "(Retrieve Security Knowledge). If findings are confirmed, UC-06 (Generate Remediation Patch) is included. UC-07 (Validate Patch) executes static and sandbox checks. "
        "If validation fails, the flow conditionally extends into UC-08 (Self-Healing Retry, max 3 attempts). If finding confidence is low (< 0.85), the flow conditionally extends "
        "into UC-10 (Human Audit Queue). Finally, UC-09 generates reports and UC-11 captures developer accept/reject feedback."
    )

    add_h2(doc, "4.4 Class Diagram / Class Architecture")
    add_p(doc, 
        "The Class Diagram models the static structural design of AgentShield AI, detailing the Pydantic v2 data models, immutable state contracts, "
        "domain enumerations, and autonomous agent class interfaces. Figure 4.2 presents the complete Class Architecture."
    )
    add_figure(doc, "slide_16_img_19.png", "Figure 4.2: UML Class Diagram & Pydantic Data Contracts Architecture", width_in=6.4)
    add_p(doc, 
        "The class architecture establishes four primary structural groupings:"
    )
    add_bullet(doc, "IaCType (TERRAFORM, CLOUDFORMATION, KUBERNETES, HELM), CloudProvider (AWS, AZURE, GCP, MULTI_CLOUD), Severity (CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL), RemediationStatus (PENDING, SYNTAX_VALIDATED, SANDBOX_PASSED, APPLIED, REJECTED, FAILED), ComplianceFramework (SOC2, HIPAA, PCI_DSS, NIST_800_53, CIS_BENCHMARK), and LineRange (start_line, end_line).", bold_prefix="1. Enumerations & Value Objects: ")
    add_bullet(doc, "IaCTemplate (represents input code and parsed AST root), ASTNode (hierarchical tree node with attributes and dependencies), VulnerabilityFinding (finding metadata, severity, confidence, attack path), ComplianceMapping (framework, control ID), VulnerabilityReport (aggregated report summary and risk score), PatchDiff (original code, patched code, unified diff), ValidationCheckResult (check name, pass/fail status, diagnostic error), and AgentShieldWorkspace (top-level session state containing template, report, patches, attack graph, and execution logs).", bold_prefix="2. Core Data Contracts (Pydantic v2): ")
    add_bullet(doc, "ManagerAgent (execute_workflow), ASTParserAgent (parse_template), SecretsScannerAgent (scan_secrets), RAGQueryAgent (retrieve_context), SecurityAnalysisAgent (analyze_vulnerabilities), RemediationAgent (generate_patches), ValidatorAgent (validate_patches), and ReportFeedbackAgent (generate_report).", bold_prefix="3. Autonomous Agents: ")
    add_bullet(doc, "Strict multiplicity guarantees that an IaCTemplate has 1..* ASTNodes; a VulnerabilityFinding maps to 0..* ComplianceMappings and generates 0..* PatchDiffs; each PatchDiff is evaluated by 0..* ValidationCheckResults; and an AgentShieldWorkspace encapsulates the unified state contract.", bold_prefix="4. Structural Relationships: ")

    add_h2(doc, "4.5 Sequence Diagram")
    add_p(doc, 
        "The UML Sequence Diagram illustrates the dynamic, chronological message exchanges occurring across the thirteen system participants during an end-to-end "
        "security analysis, remediation, and verification run. Figure 4.3 depicts this complete execution trace."
    )
    add_figure(doc, "slide_17_img_20.png", "Figure 4.3: UML Sequence Diagram — Execution Trace from Ingestion to Sandbox Remediation", width_in=6.4)
    add_p(doc, 
        "The sequence execution proceeds through seventeen numbered chronological steps organized across five pipeline phases:"
    )
    add_bullet(doc, "1. The developer submits an IaC template via submit_template(). The Manager Agent initializes workspace status to INITIALIZED. In a parallel block ('par'), 2. the AST Parser parses the template into an ASTNode tree, while 3. the Secrets Scanner intercepts credentials, returning masked code.", bold_prefix="Phase 1 (Ingestion & Pre-Processing): ")
    add_bullet(doc, "4. The Manager calls enrich_context() on the RAG Query Agent. 5. The RAG Agent invokes hybrid_search() on the Qdrant vector database, returning top-k compliance controls mapped to the declared cloud resources.", bold_prefix="Phase 2 (Knowledge & Context Enrichment): ")
    add_bullet(doc, "6. Security Analyst calls evaluate_security(). 7. The multi-LLM ensemble prompts Claude 3.5 Sonnet and GPT-4o in parallel threads. An agreement formula calculates consensus score C_ens. In an alternative block ('alt'), if C_ens < 0.85, 8. the finding escalates to the Human Audit Queue; if C_ens >= 0.85, verified findings proceed to auto-patching.", bold_prefix="Phase 3 (Analysis & Consensus Engine): ")
    add_bullet(doc, "9. Remediation Agent executes generate_patch() producing a Unified Git Diff. 10. The patch is passed to the Validator Agent via validate_patch(). In a loop block (max 3 retries), 11. static linters run. If syntax check fails, the linter error is fed back to the Remediation Agent for re-synthesis. 13. If syntax passes, a dry-run deploy executes in the LocalStack Sandbox. If runtime passes, status transitions to SANDBOX_PASSED.", bold_prefix="Phase 4 (Remediation & Self-Healing Validation): ")
    add_bullet(doc, "15. Report & Feedback Agent generates JSON/PDF/SARIF reports. 16. Results are delivered to the developer. 17. The developer submits accept/reject feedback, which is stored in the Developer Feedback Store for future prompt tuning.", bold_prefix="Phase 5 (Delivery & Continuous Learning): ")

    add_h2(doc, "4.6 State Chart Diagram")
    add_p(doc, 
        "The State Chart Diagram models the formal discrete state transitions of the AgentShieldWorkspace session container and candidate PatchDiff entities "
        "from initial file ingestion to final verified remediation. Figure 4.4 illustrates the state machine architecture."
    )
    add_figure(doc, "slide_18_img_21.png", "Figure 4.4: UML Statechart Diagram — Workspace & Remediation Patch Lifecycle", width_in=6.4)
    add_p(doc, 
        "As formalized in Figure 4.4, the state machine comprises eight discrete states governed by specific transition guards and actions:"
    )
    add_bullet(doc, "State 1 (INITIALIZED): The template file is validated for existence, non-emptiness, and valid extension (.tf, .yaml, .json). Invalid inputs transition immediately to an error terminal state.", bold_prefix="• ")
    add_bullet(doc, "State 2 (PARSING & SCANNING): Parallel workers execute AST parsing and credential scanning. Detected secrets are redacted, variable scopes resolved, and dependency graphs generated, transitioning state to PARSED.", bold_prefix="• ")
    add_bullet(doc, "State 3 (CONTEXT ENRICHING): Resource types are extracted and queried against Qdrant and BM25 indices. Compliance control mappings are attached, transitioning state to ENRICHED.", bold_prefix="• ")
    add_bullet(doc, "State 4 (ANALYZING & CONSENSUS): Prompts are dispatched to parallel LLMs. If consensus C_ens >= 0.85, findings are marked auto-patchable; otherwise, findings escalate to the Human Audit Queue.", bold_prefix="• ")
    add_bullet(doc, "State 5 (REMEDIATION): The Remediation Agent synthesizes Unified Git Diffs, setting patch status to PENDING and workspace status to REMEDIATING.", bold_prefix="• ")
    add_bullet(doc, "State 6 (VALIDATION): Static linters and LocalStack sandboxes evaluate the patch. If validation fails and retry count < 3, compiler errors are fed back for re-remediation. If retries are exhausted, the patch transitions to FAILED and escalates to human review. If validation passes, status transitions to SANDBOX_PASSED.", bold_prefix="• ")
    add_bullet(doc, "State 7 (REPORTING): Multi-format reports (SARIF, PDF, Markdown) are generated and delivered, transitioning workspace status to COMPLETED.", bold_prefix="• ")
    add_bullet(doc, "State 8 (DEVELOPER FEEDBACK): Developer accept/reject actions are logged into feedback stores, updating negative few-shot exemplar prompts for subsequent analysis cycles.", bold_prefix="• ")

    add_h2(doc, "4.7 Deployment Diagram")
    add_p(doc, 
        "The UML Deployment Diagram illustrates the physical and containerized node topologies, runtime execution environments, microservices, "
        "and network communication protocols governing AgentShield AI. Figure 4.5 depicts this deployment topology."
    )
    add_figure(doc, "slide_19_img_22.png", "Figure 4.5: UML Deployment Diagram — Containerized Microservices and Cloud Infrastructure", width_in=6.4)
    add_p(doc, 
        "The deployment topology is organized across four distinct computational nodes:"
    )
    add_bullet(doc, "Developer Workstation (Client Node): Hosts client execution artifacts including the AgentShield VS Code Extension, the CLI terminal tool (agentshield scan), the Git pre-commit hook (.pre-commit-hooks.yaml), and local repository storage. Communicates with the backend via HTTP/REST on port 8000.", bold_prefix="1. ")
    add_bullet(doc, "Local Docker Host / Container Engine: Hosts containerized microservices managed via Docker Compose. The 'agentshield-backend:latest' container executes a Python 3.12+ runtime containing the FastAPI REST server, the LangGraph multi-agent core, the hybrid AST parser engine, and embedded native linters. The 'qdrant/qdrant:latest' container provides HNSW vector search exposed on gRPC port 6334 and REST port 6333, backed by persistent volume mounts. The 'localstack/localstack:latest' container emulates 45+ AWS APIs on HTTP port 4566.", bold_prefix="2. ")
    add_bullet(doc, "External Frontier LLM Infrastructure: Cloud-hosted model provider endpoints (Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o, Google Gemini) accessed over secure HTTPS/TLS 1.3 on port 443 with encrypted API token authentication.", bold_prefix="3. ")
    add_bullet(doc, "Remote Version Control & CI/CD: GitHub Actions runners executing automated pull request scans via webhook triggers, as well as optional notification services (Email/SMTP, Slack alerts).", bold_prefix="4. ")

    add_h2(doc, "4.8 TECHNOLOGIES USED")
    add_p(doc, 
        "AgentShield AI integrates an advanced, modern technology stack chosen specifically to maximize performance, type safety, modularity, and security:"
    )
    add_bullet(doc, "Python 3.12 / 3.13: Chosen for its native asynchronous capabilities, rich AI/ML ecosystem, and enterprise library support. FastAPI provides high-performance ASGI REST endpoints with automated OpenAPI schema generation. Pydantic v2 enforces strict data validation and immutable state contracts at C-speed via pydantic-core.", bold_prefix="• Core Language & Backend Framework: ")
    add_bullet(doc, "LangGraph & LangChain: LangGraph orchestrates the multi-agent execution pipeline as a cyclical state graph, supporting state persistence, conditional edge routing, parallel execution forks, and self-healing error loops.", bold_prefix="• Multi-Agent Workflow Engine: ")
    add_bullet(doc, "Qdrant Vector Database: High-performance vector database with HNSW (Hierarchical Navigable Small World) indexing, cosine distance metrics, and metadata filtering. Supports embedded local on-disk storage as well as containerized clustering.", bold_prefix="• Vector Database & Similarity Search: ")
    add_bullet(doc, "Rank-BM25 & Sentence-Transformers: Sentence-Transformers generates 384-dimensional dense semantic embeddings using 'all-MiniLM-L6-v2'. Rank-BM25 implements the BM25Okapi algorithm for sparse lexical keyword scoring. Reciprocal Rank Fusion (RRF) mathematically fuses dense and sparse rankings with Bayesian smoothing (k = 60).", bold_prefix="• Hybrid RAG & Embedding Models: ")
    add_bullet(doc, "Python-HCL2 & PyYAML: Fast AST parsers for Terraform HCL, CloudFormation, Kubernetes, and Helm templates, extracting resource blocks, attributes, line numbers, and dependencies.", bold_prefix="• Multi-IaC Parsing Engines: ")
    add_bullet(doc, "NetworkX: Graph-theoretic library used to model cloud resource dependencies as directed graphs (ResourceGraph), calculate downstream blast radius via topological traversals, and identify architectural choke points.", bold_prefix="• Attack Path Modeling: ")
    add_bullet(doc, "LocalStack & Native Linters: LocalStack provides containerized mock cloud runtimes for AWS Terraform and CloudFormation. Static linters (terraform validate, tflint, cfn-lint, kube-linter) provide automated compiler verification.", bold_prefix="• Validation & Sandbox Harness: ")
    add_bullet(doc, "ReportLab & SARIF: ReportLab powers automated PDF report rendering with custom tables and risk gauges. SARIF v2.1.0 output integrates natively with GitHub Security and enterprise DevSecOps pipelines.", bold_prefix="• Compliance Reporting: ")
    add_bullet(doc, "React 18 & Vite: High-speed frontend development environment with modern component-driven UI for vulnerability inspection, diff comparison, and audit queue management.", bold_prefix="• Frontend Dashboard: ")

    print("All chapters written successfully!")

if __name__ == "__main__":
    import subprocess
    import sys
    print("Executing complete document build pipeline via build_college_document.py...")
    subprocess.run([sys.executable, "backend/build_college_document.py"], check=True)
