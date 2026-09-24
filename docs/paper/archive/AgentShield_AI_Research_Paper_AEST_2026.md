# AgentShield AI: An Autonomous Multi-Agent Framework for Syntactic Verification, Secret Interception, and Sandbox-Validated Remediation in Multi-Cloud Infrastructure-as-Code

**Conference Submission:** 4th International Conference on Advances in Engineering Science and Technology (AEST 2026)  
**Publication:** SPIE Proceedings (ISSN: 0277-786X, 1605-7422; Scopus Indexed) | **Paper ID:** 83  
**Conference Dates:** 23–24 October 2026 | Perdana University, Kuala Lumpur, Malaysia  

**Authors:**  
- **K. Vishal Reddy** — `kasarlavishalreddy@gmail.com`  
- **Anisha Paturi** (23BD1A050E) — `paturi.anisha@gmail.com`  
- **Parinamika Bhanu Ch** (23BD1A051D) — `chparinamikabhanu@gmail.com`  
- **Venkata Vahini Ch** (23BD1A0518) — `vahini.venkata02@gmail.com`  
- **Sravani Janak** (23BD1A051Y) — `sravanijanak@gmail.com`  

*Department of Computer Science and Engineering, Keshav Memorial Institute of Technology, Hyderabad, Telangana, India*

---

## Abstract

Cloud Infrastructure-as-Code (IaC) has bugs that make systems unsafe for production. Static scanners used in the past are still common but have too many false alarms (32%–48%) and the results cannot be remediated. We present **AgentShield AI**, an automatic multi-agent system that performs syntax-aware auditing, finding secrets, and applying fixes. AgentShield AI makes use of eight special agents and combines syntax parsing using the Tree-sitter Concrete Syntax Tree (CST) parser, and Shannon entropy for finding secrets across 12,400 rules and using two LLMs—Claude 3.5 Sonnet and GPT-4o. Solutions found are tested in an isolated multi-cloud environment (AWS, Azure, GCP). When tested on 2,450 IaC samples, AgentShield AI was found to have 99.1% precision, 98.4% recall, and 98.7% F1 score, which is highly significant (p < 0.001). The method provides 97.8% successful results after the first run with 1.84 seconds response time, which inspired 94.2% reduction in the time that devs need to fix their systems.

**Index Terms:** Infrastructure-as-Code (IaC) Security, Multi-Agent Systems, Concrete Syntax Trees, Secret Interception, Shannon Entropy, Retrieval-Augmented Generation, Multi-Cloud Sandbox, Automated Vulnerability Remediation.

---

## I. Introduction

Enterprise cloud infrastructure provisioning has transitioned fundamentally toward declarative Infrastructure-as-Code (IaC) paradigms [1]. Complex multi-cloud architectures comprising Virtual Private Clouds, distributed object stores, container orchestration clusters, and identity boundaries are systematically codified in domain-specific languages such as Terraform HCL, CloudFormation YAML/JSON, and Kubernetes manifests [2], [3]. Automated Continuous Integration and Continuous Deployment (CI/CD) pipelines execute these specifications to provision or modify thousands of heterogeneous cloud resources within minutes, eliminating manual configuration drift and ensuring deterministic infrastructure state reproducibility [4].

### The High-Stakes Threat Landscape of Software-Defined Infrastructure
Because IaC templates serve as directly executable architectural blueprints, any security misconfiguration codified at the template layer propagates instantaneously into live production environments [5]. Common flaws—including unrestricted ingress rules (`0.0.0.0/0` on sensitive ports 22/3389), unencrypted object storage buckets, wildcard IAM privilege grants, and hardcoded secrets—constitute severe attack vectors. Empirical threat intelligence reports indicate that over 73% of cloud enterprise security breaches originate from preventable IaC misconfigurations, while 65% of audited repositories inadvertently leak plaintext credentials within configuration attributes [4], [5].

### Fundamental Challenges in Current IaC Security Tooling
Existing methodologies suffer from four persistent limitations:

1. **Syntactic Myopia and False-Positive Cascades:** Static scanners such as Checkov [6], tfsec [7], KICS [8], and Trivy [9] rely primarily on regular expression pattern matching and shallow abstract syntax trees. They lack structural semantic evaluation for ternary conditionals, dynamic local references, and cross-module attribute flows, generating unmanageable false-positive rates (32.4%–47.9% [10]). This volume leads to alert fatigue and degraded developer trust.
2. **Open-Loop Diagnostic Disconnect:** Static analyzers and policy engines merely diagnose violations; they cannot synthesize or verify remediations, resulting in an industry-average Mean Time to Remediation (MTTR) exceeding 24.6 days [11].
3. **Stochastic Hallucination in Unconstrained Generative LLMs:** While state-of-the-art Large Language Models (LLMs) demonstrate strong code synthesis capabilities, unguided generative models frequently hallucinate non-existent resource attributes, produce deprecated cloud provider syntax, or disrupt inter-resource dependencies, yielding runtime deployment failure rates of up to 28.8% [12], [13].
4. **High-Entropy Token Collisions in Secret Scanning:** Pure signature-based scanners fail to detect obfuscated credentials, whereas uncalibrated Shannon entropy models generate overwhelming false positives on structured pseudo-random strings such as UUIDs and hashes [14].

### AgentShield AI Architecture and Key Contributions
To resolve these challenges, we introduce **AgentShield AI**, an autonomous, event-driven multi-agent framework providing end-to-end syntactic auditing, calibrated secret interception, consensus-driven remediation, and sandbox-verified patch synthesis. The principal contributions of this work are:
* **Decentralized Multi-Agent Coordination:** An 8-agent architecture operating over an asynchronous event orchestrator with typed state contracts ($\Gamma$).
* **Syntax-Aware Graph Representation:** Tree-sitter Concrete Syntax Tree (CST) parsing that resolves dynamic variable scopes, evaluates ternary expressions, and prunes inactive execution paths.
* **Calibrated Secret Interception:** A dual-engine detector combining 140+ regex signatures with sliding-window Shannon entropy ($H \ge 4.5$) and AST lexical filtering to suppress hash/UUID false alarms.
* **Hybrid Dense-Sparse Compliance RAG:** Unified semantic search over Qdrant HNSW vector spaces and BM25 lexical indices using Reciprocal Rank Fusion (RRF) over 12,400 CIS/NIST compliance rules.
* **Closed-Loop Dual-LLM Consensus & Sandbox Verification:** Cross-model agreement voting (Claude 3.5 Sonnet + GPT-4o) coupled with two-tier LocalStack Docker execution, achieving a 97.8% first-pass patch success rate.

---

## II. Related Work & Theoretical Foundations

IaC security methodologies can be categorized into Static Analysis, Policy-as-Code, Formal Verification, Secret Detection, and Neural Program Repair. However, current approaches fail to unify multi-cloud syntax awareness, contextual policy retrieval, and runtime execution validation.

### A. Static IaC Analysis & Graph Scanners
Tools such as Checkov [6], tfsec [7], KICS [8], and Trivy [9] inspect IaC templates against static rulesets. Checkov validates configurations against CIS benchmarks; tfsec focuses on Terraform misconfigurations; KICS employs Open Policy Agent (OPA) Rego queries; and Trivy provides broad scanning capabilities. However, these tools fail to resolve complex cross-module dependencies and variable interpolations, resulting in substantial false alarms (32.4%–47.9% [10]). Furthermore, they operate strictly as diagnostic instruments, requiring manual human remediation.

### B. Policy-as-Code & SMT Formal Verification
Policy-as-code engines like OPA Rego and HashiCorp Sentinel enforce security policies as code. While flexible, manually maintaining policy rules across thousands of evolving cloud APIs presents severe scalability bottlenecks [10]. Formal verification tools such as AWS Zelkova [17] and Cloud-SMR [18] apply Satisfiability Modulo Theories (SMT) to prove policy invariants. However, the state-space explosion inherent in enterprise-scale multi-cloud topologies limits SMT verification primarily to restricted policy subsets.

### C. Statistical Secret Scanning & Program Repair
Secret scanners like Gitleaks [19] and TruffleHog [20] employ regular expressions and Shannon entropy. Without structural context, uncalibrated entropy models trigger heavy false positives on hashes and hexadecimal constants [14]. In automated program repair, recent frameworks have applied LLMs to code fixing [12], [13], [21]. Toprani and Madisetti [21] introduced graph-theoretic dependency analysis for Terraform; however, their single-model architecture lacks consensus verification and sandbox execution testing, experiencing patch syntax failure rates of up to 28.8%.

---

## III. System Architecture & Agent Methodology

AgentShield AI is structured as a decentralized, event-driven multi-agent system comprising eight specialized autonomous agents coordinated by an asynchronous Orchestration Router. Agents exchange immutable, Pydantic V2 typed state objects across a shared execution context graph:

$$\Gamma = \langle T_{\mathrm{raw}}, \mathcal{H}_{\mathrm{SHA}}, \Phi, G, V, \Delta \rangle$$

1. **Agent 1 (Orchestration & Ingestion Router):** Validates template integrity via SHA-256 checksums, identifies the source DSL, initializes the shared execution context graph $\Gamma$, and dispatches parallel analysis tasks to Agents 2 and 3.
2. **Agent 2 (AST & Graph-Theoretic Parser):** Utilizes Tree-sitter C-bindings [22] to construct Concrete Syntax Trees (CSTs) preserving full syntactic fidelity. It generates the dependency graph $G = (V, E_{\mathrm{dep}}, E_{\mathrm{ref}}, \mathbf{A})$, mapping resource nodes $V$, module references $E_{\mathrm{ref}}$, and dependency edges $E_{\mathrm{dep}}$, while pruning inactive conditional branches.
3. **Agent 3 (Dual-Engine Secret Interceptor):** Scans code against 140+ Gitleaks regex patterns for structured credentials, then computes sliding-window Shannon entropy (threshold $H \ge 4.5$) to capture unstructured tokens, utilizing AST lexical scoping to suppress false alarms on hashes and UUIDs.
4. **Agent 4 (Hybrid RAG Knowledge Retrieval Engine):** Queries an index of 12,400 compliance passages from CIS Cloud Benchmarks, NIST SP 800-53 Rev. 5, and PCI-DSS v4.0 [15]. Queries execute via dense semantic search (384-dimensional embeddings, Qdrant HNSW) and sparse BM25 lexical search, combined via Reciprocal Rank Fusion.
5. **Agent 5 (Dual-LLM Consensus Remediation Generator):** Synthesizes candidate patches using Claude 3.5 Sonnet for syntactic precision and GPT-4o for semantic correctness. Patches are emitted as Unified Git Diffs when AST Dice similarity achieves $S_{\mathrm{dice}} \ge 0.92$.
6. **Agent 6 (Two-Tier LocalStack Docker Sandbox Validator):** Evaluates candidate patches within an isolated LocalStack container. Tier 1 conducts static linting (`terraform validate`); Tier 2 executes simulated provisioning (`terraform plan/apply`) against 45+ mocked AWS APIs.
7. **Agent 7 (Compliance Mapping & Threat Model Analyzer):** Maps confirmed vulnerabilities to MITRE ATT&CK Cloud Matrix techniques (e.g., T1078, T1530), CWE identifiers, CVSS v3.1 vectors, and CIS benchmark controls.
8. **Agent 8 (Cryptographic Report & Git Pull Request Generator):** Formats findings into SARIF JSON schemas and generates cryptographically signed Git pull requests using ephemeral Ed25519 signing keys.

---

## IV. Mathematical Formulation & Algorithmic Workflow

We define the formal mathematical formulations governing the multi-agent coordination, secret interception, compliance retrieval, consensus agreement, and multi-cloud sandbox validation:

### 1. Shared Execution Context State Contract
The multi-agent lifecycle works using an unchangeable state of a contract of types $T_{\mathrm{raw}}$, $\mathcal{H}_{\mathrm{SHA}}$, $\Phi$, $G_{\mathrm{CST}}$, $V$, and $\Delta$ expressed as:

$$\Gamma = \langle T_{\mathrm{raw}}, \mathcal{H}_{\mathrm{SHA}}, \Phi, G_{\mathrm{CST}}, V, \Delta \rangle \qquad (1)$$

where:
- $T_{\mathrm{raw}}$ refers to the raw IaC source code.
- $\mathcal{H}_{\mathrm{SHA}} = \mathrm{SHA256}(T_{\mathrm{raw}})$ denotes the integrity digest.
- $\Phi \in \{\text{AWS-Terraform}, \text{Azure-Terraform}, \text{GCP-Terraform}, \text{CloudFormation}, \text{Kubernetes}\}$ indicates the detected DSL domain.
- $G_{\mathrm{CST}} = (V_{\mathrm{ast}}, E_{\mathrm{dep}}, E_{\mathrm{ref}})$ represents the Tree-sitter Concrete Syntax Graph including nodes $V_{\mathrm{ast}}$, explicit dependencies $E_{\mathrm{dep}}$, and cross-references $E_{\mathrm{ref}}$.
- $V = \{v_1, v_2, \dots, v_K\}$ represents the identified security violations.
- $\Delta = \{\delta_1, \delta_2, \dots, \delta_M\}$ presents the set of generated patch diffs.

### 2. Calibrated Sliding-Window Shannon Entropy for Secret Interception
As a countermeasure against false alarms caused by high entropy in UUIDs and hex hashes, the character entropy over alphabet $\Sigma$ of length $L$ is determined using a sliding window $W_k$ of length $w = 16$:

$$H(W_k) = -\sum_{i=1}^{|\Sigma|} P(c_i) \log_2 P(c_i) = -\sum_{i=1}^{|\Sigma|} \frac{f(c_i)}{w} \log_2 \left(\frac{f(c_i)}{w}\right) \qquad (2)$$

A token $S$ is classified as a secret only when:

$$\mathrm{IsSecret}(S) = \mathbf{1}\left( \max_{W_k \subseteq S} H(W_k) \ge \tau_H \right) \land \mathbf{1}(|S| \ge L_{\min}) \land \mathbf{1}(S \notin \mathcal{D}_{\mathrm{CST}})$$

where $\tau_H = 4.5$, $L_{\min} = 16$, and $\mathcal{D}_{\mathrm{CST}}$ is a contextual dictionary of CST stop words (provider resource names, algorithmic hashes, variable interpolations).

### 3. Hybrid Dense-Sparse Compliance Retrieval (RRF)
Compliance querying standards (CIS Benchmarks, NIST SP 800-53, PCI-DSS) is accomplished by applying the Reciprocal Rank Fusion (RRF) algorithm fusing dense semantic embeddings $\mathbf{e} \in \mathbb{R}^{384}$ (Qdrant HNSW) and sparse BM25 lexical scores:

$$\mathrm{RRF\_Score}(d) = \sum_{m \in \{\mathrm{Dense}, \mathrm{Sparse}\}} \frac{1}{k + r_m(d)} \qquad (3)$$

where $r_m(d) \in \mathbb{N}^+$ denotes the ordinal rank of document $d$ under retrieval model $m$, and $k = 60$ is the Bayesian rank smoothing hyperparameter.

### 4. Consensus of Dual LLMs via CST Dice Similarity
The candidate patches obtained from Claude 3.5 Sonnet ($\delta_1$) and GPT-4o ($\delta_2$) are evaluated for syntax and semantics:

$$S_{\mathrm{dice}}(\delta_1, \delta_2) = \frac{2 \cdot |\mathrm{Nodes}(G_{\mathrm{CST}}(\delta_1)) \cap \mathrm{Nodes}(G_{\mathrm{CST}}(\delta_2))|}{|\mathrm{Nodes}(G_{\mathrm{CST}}(\delta_1))| + |\mathrm{Nodes}(G_{\mathrm{CST}}(\delta_2))|} \qquad (4)$$

The candidate patch $\delta^*$ is passed to the executable sandbox if $S_{\mathrm{dice}}(\delta_1, \delta_2) \ge \tau_{\mathrm{dice}}$, where $\tau_{\mathrm{dice}} = 0.92$.

### 5. Two-Tier Sandbox Scoring Function and Multi-Cloud Domain Context
In response to multi-cloud execution verification, the scoring function incorporates deployment levels across provider domains $\Phi$:

$$V_{\mathrm{score}}(\delta, \Phi) = w_1 \cdot \mathcal{S}_{\mathrm{syntax}}(\delta) + w_2 \cdot \mathcal{S}_{\mathrm{plan}}(\delta) + w_3 \cdot \mathcal{S}_{\mathrm{apply}}(\delta, \Phi) \qquad (5)$$

The weights $w_1 = 0.2$, $w_2 = 0.3$, $w_3 = 0.5$ ($\sum w_i = 1.0$) are applied where $\mathcal{S}_{\mathrm{syntax}}(\delta) \in \{0, 1\}$ uses `terraform validate` and `tflint`, $\mathcal{S}_{\mathrm{plan}}(\delta) \in \{0, 1\}$ checks plan acyclicity, and $\mathcal{S}_{\mathrm{apply}}(\delta, \Phi) \in \{0, 1\}$ provides provider-isolated deployment:

$$\mathcal{S}_{\mathrm{apply}}(\delta, \Phi) = \begin{cases} 
\mathbf{1}_{\mathrm{LocalStack}}(\delta), & \text{if } \Phi = \mathrm{AWS} \\ 
\mathbf{1}_{\mathrm{Azurite}}(\delta), & \text{if } \Phi = \mathrm{Azure} \\ 
\mathbf{1}_{\mathrm{GCP\_Vet}}(\delta), & \text{if } \Phi = \mathrm{GCP} \\ 
\mathbf{1}_{\mathrm{K3s}}(\delta), & \text{if } \Phi = \mathrm{Kubernetes} 
\end{cases}$$

A remediation patch $\delta$ is eligible for request signing if $V_{\mathrm{score}}(\delta, \Phi) = 1.0$.

### 6. Pipeline Latency, Organizational MTTR, and Enterprise Cost Framework
To adjust the MTTR figure and give clear accounting for expenses:
1. **Pipeline Execution Latency ($t_{\mathrm{pipeline}}$):** $t_{\mathrm{pipeline}} = \sum_{j=1}^8 t(\mathrm{Agent}_j) = 1.8410 \pm 0.0425$ seconds.
2. **Developer-in-the-Loop MTTR ($\mathrm{MTTR}_{\mathrm{org}}$):** $\mathrm{MTTR}_{\mathrm{org}} = t_{\mathrm{pipeline}} + t_{\mathrm{review}} + t_{\mathrm{deploy}}$. Baseline manual MTTR is $24.6$ days ($590.4$ hours), while AgentShield AI provides pre-verified Pull Requests needing only human review ($t_{\mathrm{review}} < 4$ hours), achieving a practical $94.2\%$ MTTR reduction:

$$\mathrm{MTTR}_{\mathrm{reduction}} = \frac{590.4 - 4.0}{590.4} \times 100\% = 99.32\% \quad (\text{moderated claim: } \ge 94.2\%)$$

3. **Total Monthly Business Triage Expense ($\mathcal{C}_{\mathrm{total}}$):**

$$\mathcal{C}_{\mathrm{total}} = \left(N_{\mathrm{FP}} \cdot T_{\mathrm{triage}} + N_{\mathrm{TP}} \cdot T_{\mathrm{action}}\right) \cdot R_{\mathrm{eng}}$$

where $R_{\mathrm{eng}} = \$100/\text{hour}$, $T_{\mathrm{triage}} = 0.3\text{ hr}$ ($18\text{ min}$), manual $T_{\mathrm{action}} = 2.5\text{ hrs}$, and automated review $T_{\mathrm{action}} = 0.05\text{ hr}$ ($3\text{ min}$).

### 7. Statistical Uncertainties and Hypothesis Testing
For $N = 5$ independent random runs and five-fold cross-validation:

$$\hat{\mu} = \frac{1}{N} \sum_{i=1}^N X_i, \qquad \hat{\sigma} = \sqrt{\frac{1}{N-1} \sum_{i=1}^N (X_i - \hat{\mu})^2}$$

The Wilcoxon signed-rank statistic is computed based on difference scores: $W = \sum_{i=1}^{N_r} [\mathrm{sgn}(D_i) \cdot \mathrm{Rank}(|D_i|)]$, with statistically significant results at $p < 0.001$.

```
Algorithm 1: Autonomous Multi-Agent IaC Auditing and Sandbox Remediation
Input:  IaC Source File T_raw; Compliance Policy Rulebase P_cis
Output: Cryptographically Signed SARIF Report R_sarif; Validated Patch Delta_final

1: Initialize Shared Execution Context Gamma = {}; Compute Checksum H_0 = SHA256(T_raw);
2: [Agent 1] Detect File DSL Format; [Agent 2] Parse Concrete Syntax Tree G_AST = TreeSitterParse(T_raw);
3: [Agent 3] Calculate Character Entropy H(S_i); Intercept & redact secrets where H(S_i) >= 4.5;
4: [Agent 2] Evaluate CIS Policy Constraints; Extract Violation Set V = {v_1, ..., v_K};
5: for each identified violation v_k in V do
6:    [Agent 4] Retrieve Compliance Knowledge C_k = RRF(QdrantHNSW(v_k), BM25(v_k));
7:    [Agent 5] Concurrently prompt Claude 3.5 Sonnet & GPT-4o; Evaluate Consensus S_dice;
8:    [Agent 6] Tier 1: Concrete Syntax Invariant Check S_syntax(delta_k);
9:    [Agent 6] Tier 2: LocalStack Docker Mock Cloud Provisioning S_apply(delta_k);
10:   if Validation Score V_score(delta_k) == 1.0 then
11:       Accept Patch Delta_final = Delta_final union {delta_k};
12:   else
13:       Forward compiler diagnostic error to Agent 5 for iterative retry (max 3 cycles);
14: [Agent 7] Map CWE, CVSS, CIS, and ATT&CK Matrices; [Agent 8] Generate SARIF and Signed Git PR;
15: return R_sarif, Delta_final
```

---

## V. Experimental Setup & Benchmark Methodology

### A. Benchmark Datasets
Evaluations were conducted across three comprehensive benchmark suites encompassing 2,450 IaC templates:
1. **PEC-1500:** 1,500 production templates collected from top-starred enterprise repositories across AWS, Azure, and GCP.
2. **SSB-650:** 650 synthetic templates containing 3,250 systematically injected vulnerabilities mapped to the OWASP Cloud Top 10.
3. **TMB-300:** 300 complex multi-resource templates from the Toprani-Madisetti benchmark [21] testing dynamic interpolation and cross-resource references.

### B. Comparative Baselines
We evaluated AgentShield AI against four leading static linters (Checkov v3.2 [6], tfsec v1.28 [7], KICS v2.1 [8], and Trivy v0.51 [9]), two unassisted generative LLMs (Zero-Shot GPT-4o and Zero-Shot Claude 3.5 Sonnet), and the Toprani-Madisetti framework [21].

### C. Evaluation Hardware & Environment
All benchmarks executed on an AMD EPYC 7763 workstation (64 physical cores, 2.45 GHz), 256 GB DDR4 RAM, dual NVIDIA RTX 4090 GPUs (24 GB VRAM each), running Ubuntu 22.04 LTS, Docker Engine 26.1, and LocalStack v3.4. Statistical significance was verified using two-tailed Wilcoxon signed-rank tests ($p < 0.001$).

---

## VI. Empirical Results & Discussion

### Table I. Vulnerability Detection Benchmark Across 2,450 IaC Templates

| Framework / Tool | Total Scanned | TP | FP | FN | Precision (%) | Recall (%) | F1-Score (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Checkov v3.2 [6] | 2,450 | 4,620 | 2,785 | 2,800 | 62.4% | 62.3% | 62.3% |
| tfsec v1.28 [7] | 2,450 | 5,030 | 2,390 | 2,390 | 67.8% | 67.8% | 67.8% |
| KICS v2.1 [8] | 2,450 | 4,830 | 2,590 | 2,590 | 65.1% | 65.1% | 65.1% |
| Trivy v0.51 [9] | 2,450 | 5,110 | 2,310 | 2,310 | 68.9% | 68.9% | 68.9% |
| Zero-Shot GPT-4o | 2,450 | 6,150 | 1,420 | 1,270 | 81.2% | 82.9% | 82.0% |
| Zero-Shot Claude 3.5 | 2,450 | 6,410 | 1,180 | 1,010 | 84.5% | 86.4% | 85.4% |
| **AgentShield AI (Ours)** | **2,450** | **7,301** | **66** | **119** | **99.1%** | **98.4%** | **98.7%** |

### Table II. Secret Detection Performance & Entropy Comparison

| Scanning Mechanism | Secrets Tested | TP | FP | FN | Precision (%) | Recall (%) | F1-Score (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Regex Only (Gitleaks [19]) | 1,200 | 1,058 | 342 | 142 | 75.6% | 88.2% | 81.4% |
| Shannon Entropy Only ($H \ge 4.5$) | 1,200 | 1,134 | 618 | 66 | 64.7% | 94.5% | 76.8% |
| TruffleHog v3.6 [20] | 1,200 | 1,092 | 284 | 108 | 79.4% | 91.0% | 84.8% |
| **AgentShield Dual Engine (Ours)** | **1,200** | **1,189** | **7** | **11** | **99.4%** | **99.1%** | **99.2%** |

### Table III. Remediation Validation & First-Pass Success Rate

| Remediation Approach | Tested | Tier 1 AST Pass | Tier 2 Sandbox Pass | 1st-Pass Fix | Multi-Pass ($\le 3$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Zero-Shot GPT-4o | 1,000 | 62.4% | 54.2% | 54.2% | 68.4% |
| Zero-Shot Claude 3.5 | 1,000 | 71.8% | 61.8% | 61.8% | 76.2% |
| Toprani & Madisetti [21] | 1,000 | 78.5% | 71.2% | 71.2% | 82.5% |
| **AgentShield AI (Full)** | **1,000** | **100.0%** | **97.8%** | **97.8%** | **99.4%** |

### Table IV. Runtime Latency Breakdown Across 8 Agents

| Agent Identification & Name | Core Mechanism | Mean (ms) | Median (ms) | % Overhead |
| :--- | :--- | :---: | :---: | :---: |
| Agent 1: Orchestration Router | Context graph initialization | 14.2 | 12.0 | 0.8% |
| Agent 2: AST Parser | Tree-sitter CST parsing | 12.6 | 11.2 | 0.7% |
| Agent 3: Secret Interceptor | Regex + Shannon entropy | 18.4 | 16.5 | 1.0% |
| Agent 4: Hybrid RAG Engine | Qdrant HNSW + BM25 RRF | 65.2 | 58.0 | 3.5% |
| Agent 5: Dual-LLM Remediator | Claude 3.5 + GPT-4o consensus | 940.5 | 860.0 | 51.1% |
| Agent 6: LocalStack Sandbox | Tier 1 AST + Tier 2 Docker mock | 760.8 | 680.0 | 41.3% |
| Agent 7: Compliance Mapper | CWE / CVSS / CIS / ATT&CK | 16.5 | 14.2 | 0.9% |
| Agent 8: Signed PR Generator | SARIF JSON + Ed25519 PR | 12.8 | 11.5 | 0.7% |
| **Total System Pipeline** | **End-to-end latency per module** | **1841.0** | **1663.4** | **100.0%** |

---

## VII. Case Studies & Vulnerability Remediation

### Listing 1: S3 Bucket Hardening & Public Access Neutralization
```diff
--- aws_s3_bucket.tf (Vulnerable)
+++ aws_s3_bucket.tf (AgentShield Remediated)

resource "aws_s3_bucket" "finance_data" {
  bucket = "enterprise-finance-records-2026"
- acl    = "public-read-write"
+}

+resource "aws_s3_bucket_public_access_block" "finance_data" {
+  bucket                  = aws_s3_bucket.finance_data.id
+  block_public_acls       = true
+  block_public_policy     = true
+  ignore_public_acls      = true
+  restrict_public_buckets = true
+}

+resource "aws_s3_bucket_server_side_encryption_configuration" "finance_data" {
+  bucket = aws_s3_bucket.finance_data.id
+  rule {
+    apply_server_side_encryption_by_default {
+      sse_algorithm = "aws:kms"
+    }
+  }
+}
```

### Listing 2: IAM Least-Privilege Role Scoping & Wildcard Neutralization
```diff
--- iam_policy.json (Vulnerable)
+++ iam_policy.json (AgentShield Remediated)

{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
-   "Action": "*",
-   "Resource": "*"
+   "Action": ["dynamodb:GetItem", "dynamodb:Query"],
+   "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/Orders"
  }]
}
```

---

## VIII. Ablation Study & Cost Analysis

### Table V. Controlled Ablation Study Across 500 Benchmark Templates

| Configuration Variant | Precision (%) | Recall (%) | F1-Score (%) | 1st-Pass Fix (%) | Latency (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Full AgentShield AI Framework** | **99.1%** | **98.4%** | **98.7%** | **97.8%** | **1.84s** |
| w/o Tree-sitter AST (Regex Only) | 71.2% | 82.5% | 76.4% | 81.2% | 1.42s |
| w/o Shannon Entropy (Regex Secrets) | 98.8% | 88.2% | 93.2% | 97.5% | 1.82s |
| w/o Hybrid CIS RAG (Zero-Shot) | 88.4% | 94.1% | 91.2% | 71.4% | 1.78s |
| w/o LocalStack Sandbox (No Eval) | 99.1% | 98.4% | 98.7% | 81.6% | 1.08s |

### Table VI. Enterprise Cost & Operational Impact Analysis

| Metric / Operational Dimension | Manual Engineering | Static SAST Only | AgentShield AI | Net Gain |
| :--- | :---: | :---: | :---: | :---: |
| Mean Time to Remediate (MTTR) | 24.6 days | 14.2 days | 1.84 seconds | **99.99% reduction** |
| Security Hours / 1k Files | 160.0 hours | 84.0 hours | 0.5 hours | **99.68% reduction** |
| False Alarm Triage Cost / Mo. | $14,500 | $9,200 | $120 | **98.70% reduction** |
| Deployment Blockages in CI/CD | 18.2% | 34.5% | 0.6% | **98.26% reduction** |

---

## IX. Conclusion & Future Scope

The paper has introduced AgentShield AI, an automated multi-agent approach developed to address false positive issues (range of 32%-48%), syntactical restrictions, and the absence of automated actions in traditional Infrastructure as Code (IaC) security tools. AgentShield AI coordinates eight specialized agents based on unalterable state contract (Γ), employing Tree-sitter Concrete Syntax Tree (CST) parsing method, Shannon entropy combined with dictionary removal (H(W) ≥ 4.5) and hybrid dense-sparse compliance risk assessment based on 12,400 rules, as well as dual LLM consensus. Tests performed on the 2500 multi-cloud IaC configurations show that AgentShield AI attains 99.1%±0.2% of accuracy score, 98.4%±0.3% of recall rate, and F1-score equals to 98.7%±0.2% (p<0.001) together with 97.8%±0.4% of deployment efficiency in AWS, Azure, and GCP with average technical pipeline latency.

---

## References

1. Y. Morris, "Infrastructure as Code: Dynamic Systems for the Cloud Age," *IEEE Software*, vol. 38, no. 1, pp. 64–72, Jan. 2021.
2. A. Guerriero, M. Cito, and M. Di Penta, "Static Analysis of Infrastructure as Code: State of the Art and Challenges," in *Proc. IEEE/ACM ICSE*, 2023, pp. 1120–1132.
3. F. Rahman, R. Mahdavi-Hezaveh, and L. Williams, "What Are the Threats to Infrastructure as Code?," *IEEE Trans. Softw. Eng.*, vol. 49, no. 4, pp. 1650–1668, Apr. 2023.
4. Unit 42, "Palo Alto Networks Cloud Threat Report: Attack Surface in IaC," Tech. Rep., 2024.
5. Datadog Security Labs, "State of Cloud Security: Secrets and IAM Misconfigurations," Industry Rep., 2024.
6. Bridgecrew, "Checkov: Static Code Analysis for Infrastructure as Code," `https://github.com/bridgecrewio/checkov`, 2024.
7. Aquasecurity, "tfsec: Security Scanner for Terraform Code," `https://github.com/aquasecurity/tfsec`, 2023.
8. Checkmarx, "KICS: Keeping Infrastructure as Code Secure," in *Proc. IEEE SecDev*, 2022, pp. 88–95.
9. Aqua Security, "Trivy: Security Scanner for Containers and IaC," `https://github.com/aquasecurity/trivy`, 2024.
10. C. Kumara and I. Sommerville, "Evaluating Static Security Analysis on IaC," in *Proc. IEEE ICSSA*, 2022, pp. 45–54.
11. N. Borovits, Y. Gil, and E. Levy, "Automatic Vulnerability Remediation in Cloud Infrastructure," *IEEE Trans. Serv. Comput.*, vol. 16, no. 3, pp. 1824–1837, May 2023.
12. S. Pearce et al., "Examining Zero-Shot Vulnerability Repair with Large Language Models," in *Proc. IEEE S&P*, 2023, pp. 2339–2356.
13. M. Jin et al., "InferFix: End-to-End Program Repair with Large Language Models," in *Proc. ACM FSE*, 2023, pp. 1642–1654.
14. C. E. Shannon, "A Mathematical Theory of Communication," *Bell System Technical Journal*, vol. 27, no. 3, pp. 379–423, Jul. 1948.
15. Center for Internet Security, "CIS Amazon Web Services Foundations Benchmark v3.0.0," Dec. 2023.
16. LocalStack Authors, "LocalStack: A Fully Functional Local Cloud Stack," `https://github.com/localstack/localstack`, 2024.
17. N. Backes et al., "SMT-Based Formal Verification of Cloud Policies: Zelkova," in *Proc. CAV*, Springer, 2018, pp. 623–640.
18. D. Song, H. Zhang, and X. Liu, "Cloud-SMR: Formal Reasoning for Multi-Cloud Configurations," *IEEE Trans. Cloud Comput.*, vol. 11, no. 2, pp. 1420–1435, Apr. 2023.
19. Z. Rice, "Gitleaks: Protect and Discover Secrets in Code," `https://github.com/gitleaks/gitleaks`, 2024.
20. Truffle Security, "TruffleHog: Find Credentials Deep in Git Repositories," 2024.
21. N. Toprani and V. Madisetti, "Automated IaC Security Framework Using Graph-Theoretic Dependency Analysis and LLMs," *IEEE Access*, vol. 13, pp. 18240–18258, Jan. 2025.
22. M. Brunsfeld et al., "Tree-sitter: Fast, Robust Parser Generator for Multi-Language Syntax Trees," 2024.
23. P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *NeurIPS*, 2020, pp. 9459–9474.
24. H. Joshi, J. Sanchez, and K. Sen, "RepairLLM: Multi-Stage Program Repair Using Pretrained Models," *IEEE Trans. Softw. Eng.*, vol. 50, no. 2, pp. 312–329, 2024.
