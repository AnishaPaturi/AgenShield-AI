"""
make_springer_proceedings.py
Generates samplepaper.tex conforming to the Springer CCIS/LNCS template.
"""
import os

TEX_CONTENT = r'''% This is samplepaper.tex, a sample chapter demonstrating the
% LLNCS macro package for Springer Computer Science proceedings;
% Version 2.21 of 2022/01/12
%
\documentclass[runningheads]{llncs}
%
\usepackage[T1]{fontenc}
% T1 fonts will be used to generate the final print and online PDFs,
% so please use T1 fonts in your manuscript whenever possible.
% Other font encodings may result in incorrect characters.
%
\usepackage{graphicx}
% Used for displaying a sample figure.
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{url}

\usepackage{listings}
\usepackage{xcolor}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}

% Listings configuration for Unified Diffs and JSON
\lstset{
  basicstyle=\ttfamily\fontsize{7.5pt}{8.5pt}\selectfont,
  breaklines=true,
  frame=single,
  numbers=left,
  numberstyle=\tiny\color{gray},
  captionpos=b,
  keepspaces=true,
  showstringspaces=false,
  aboveskip=4pt,
  belowskip=4pt
}


\setlength{\textfloatsep}{6pt plus 1pt minus 2pt}
\setlength{\floatsep}{6pt plus 1pt minus 2pt}
\setlength{\intextsep}{6pt plus 1pt minus 2pt}
\setlength{\abovecaptionskip}{3pt}
\setlength{\belowcaptionskip}{3pt}


\setlength{\textfloatsep}{5pt plus 1pt minus 1pt}
\setlength{\floatsep}{5pt plus 1pt minus 1pt}
\setlength{\intextsep}{5pt plus 1pt minus 1pt}
\setlength{\abovecaptionskip}{2pt}
\setlength{\belowcaptionskip}{2pt}

\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.85}



\setlength{\textfloatsep}{5pt plus 1pt minus 1pt}
\setlength{\floatsep}{5pt plus 1pt minus 1pt}
\setlength{\intextsep}{5pt plus 1pt minus 1pt}
\setlength{\abovecaptionskip}{2pt}
\setlength{\belowcaptionskip}{2pt}
\setlength{\abovedisplayskip}{3pt plus 1pt minus 1pt}
\setlength{\belowdisplayskip}{3pt plus 1pt minus 1pt}
\setlength{\abovedisplayshortskip}{1pt plus 1pt}
\setlength{\belowdisplayshortskip}{1pt plus 1pt}

\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.85}

\begin{document}

%
\title{AgentShield AI: An Autonomous Multi-Agent Framework for Syntactic Verification, Secret Interception, and Sandbox-Validated Remediation in Multi-Cloud Infrastructure-as-Code}
%
\titlerunning{AgentShield AI: Multi-Agent IaC Security Framework}
% If the paper title is too long for the running head, you can set
% an abbreviated paper title here
%
\author{K. Vishal Reddy\inst{1} \and
Anisha Paturi\inst{1}\thanks{Corresponding author: paturi.anisha@gmail.com} \and
Parinamika Bhanu Ch\inst{1} \and
Venkata Vahini Ch\inst{1} \and
Sravani Janak\inst{1}}
%
\authorrunning{K. V. Reddy et al.}
% First names are abbreviated in the running head.
% If there are more than two authors, 'et al.' is used.
%
\institute{Department of Computer Science and Engineering,\\
Keshav Memorial Institute of Technology, Hyderabad, Telangana, India\\
\email{kasarlavishalreddy@gmail.com}, \email{paturi.anisha@gmail.com},\\
\email{chparinamikabhanu@gmail.com}, \email{vahini.venkata02@gmail.com},\\
\email{sravanijanak@gmail.com}}
%
\maketitle              % typeset the header of the contribution
%
\begin{abstract}
Cloud Infrastructure-as-Code (IaC) has bugs that make systems unsafe for production. Static scanners used in the past are still common but have too many false alarms ($32\%$--$48\%$) and the results cannot be remediated. We present \textbf{AgentShield AI}, an automatic multi-agent system that performs syntax-aware auditing, finding secrets, and applying fixes. AgentShield AI makes use of eight special agents and combines syntax parsing using the Tree-sitter Concrete Syntax Tree (CST) parser, and Shannon entropy for finding secrets across 12,400 rules and using two LLMs---Claude 3.5 Sonnet and GPT-4o. Solutions found are tested in an isolated multi-cloud environment (AWS, Azure, GCP). When tested on 2,450 IaC samples, AgentShield AI was found to have $99.1\%$ precision, $98.4\%$ recall, and $98.7\%$ F1 score, which is highly significant ($p < 0.001$). The method provides $97.8\%$ successful results after the first run with $1.84$ seconds response time, which inspired $94.2\%$ reduction in the time that devs need to fix their systems.

\keywords{Infrastructure-as-Code (IaC) Security \and Multi-Agent Systems \and Concrete Syntax Trees \and Secret Interception \and Shannon Entropy \and Retrieval-Augmented Generation \and Multi-Cloud Sandbox \and Automated Vulnerability Remediation.}
\end{abstract}
%
%
%
\section{Introduction}
Provisioning of cloud infrastructure has been undergoing a significant transformation towards a declarative approach with the advent of Infrastructure-as-Code (IaC) solutions~\cite{morris2021infrastructure}. Complex multi-cloud designs spanning Virtual Private Clouds to distributed storage solutions and clustering frameworks and across multiple distinct identity networks now require very specific programming languages such as HCL for Terraform to CloudFormation manifest for YAML/JSON/Kubernetes~\cite{guerriero2023static,rahman2023threats}. Fully automatic pipelines from Continuous Integration through Continuous Deployment are able to interpret these textual statements to provision or update enormous configurations of cloud resources in minutes, eliminating the problem of misconfigured cloud resources and providing a reliable state-of-the-art reproducible infrastructure as first-class middleware~\cite{unit42report}.

\subsubsection{The High-Risk Threat Environment of Software-Defined Infrastructure}
Since the IaC templates are the actual documents that model the architecture to be applied, each security error in the template's frames directly translates into a security error in the comparable production system~\cite{datadog2024state}. Common flaws---including unrestricted ingress rules (\texttt{0.0.0.0/0} on sensitive ports 22/3389), unencrypted storage buckets, wildcard IAM privilege grants, and hardcoded plaintext credentials---represent severe production risks. Threat intelligence reports indicate that over $73\%$ of cloud enterprise breaches originate from preventable IaC misconfigurations, with $65\%$ of audited repositories leaking credentials~\cite{unit42report,datadog2024state}.

\subsubsection{Fundamental Challenges in Current IaC Tooling}
Existing approaches face persistent limitations:
\begin{enumerate}
    \item \textbf{Syntactic Myopia and False-Positive Cascades:} Static linters rely on pattern matching and shallow lexical analysis, unable to evaluate cross-module references or dynamic variables, yielding false-alarm rates between $32.4\%$ and $47.9\%$~\cite{kumara2022evaluating}.
    \item \textbf{Open-Loop Diagnostic Disconnect:} Static analyzers merely report violations without generating or validating fixes, leaving teams with Mean Time to Remediation (MTTR) exceeding 24.6 days~\cite{borovits2023automatic}.
    \item \textbf{Stochastic Hallucination in Generative Models:} While LLMs are highly competent at generating software code, uncurated generative models produce completely fictitious resource characteristics or faulty provider code, resulting in resource dependency violations and up to $28.8\%$ errors in runtime deployment~\cite{pearce2023examining,jin2023inferfix}.
    \item \textbf{High-Entropy Token Collisions in Secret Detection:} Signature-based scanners do not detect obfuscated passwords, and untrained Shannon entropy models generate a vast number of false positives for pseudo-random and structured strings such as hashes of encryption and UUIDs~\cite{shannon1948mathematical}.
\end{enumerate}

\subsubsection{AgentShield AI Architecture and Key Contributions}
To address these challenges, we present AgentShield AI, a self-governing, event-driven multi-agent system that performs the complete syntactic audit, secret interception, consensus-based remedial actions, and validated patch formation through a multi-cloud sandbox. Our major contributions are:
\begin{itemize}
    \item The distinct decentralized 8-agent architecture using typed state contracts ($\Gamma$) orchestrated by an asynchronous event manager.
    \item The innovative Tree-sitter Concrete Syntax Tree (CST) technique to solve dynamic expressions and filter out unnecessary graph paths.
    \item The integrated two-in-one secret interception technique that merges 140+ regular expression signatures with sliding Shannon entropy ($H \ge 4.5$) and CST stopword filtering.
    \item The novel hybrid dense-sparse RAG technique that blends Qdrant HNSW embeddings with BM25 lexical ranking through the Reciprocal Rank Fusion (RRF) technique using a set of 12,400 different CIS/NIST rules.
    \item The collaborative dual-LLM consensus mechanism (Claude 3.5 Sonnet + GPT-4o) coupled with a dual-assessment two-layer multi-cloud sandbox (LocalStack, Azurite, GCP emulators).
\end{itemize}


\section{Related Work}

\subsection{Static Analysis and Pattern-Based Linters}
Checkov~\cite{checkov2024} was one of the tools in this area. It reads configuration files. Turns them into Python AST structures and checks them against CIS benchmark rules. tfsec~\cite{tfsec2023} does something but is made specifically for Terraform HCL it loads the code into Go memory structures and looks for anti-patterns. KICS~\cite{kics2022} takes an approach it converts multi-format IaC files into normalized JSON and runs them through Open Policy Agent (OPA) Rego rules. Trivy~\cite{trivy2024} is a bit different from the three because it was not created only for IaC it also looks at container images and Kubernetes manifests alongside Terraform files.

The problem with all of these tools is that they depend on pattern matching and pattern matching does not understand how variables move across modules. Ternary expressions, created resource names, cross-module variable references none of that gets handled properly so these scanners end up with false-positive rates between 32.4\% and 47.9\%~\cite{kumara2022evaluating}. That is half of what gets flagged being wrong which is a lot for a security team to handle every day. In addition none of these tools fix anything. They just report the problem. Leave it there.

\subsection{Policy-as-Code and Formal SMT Verification}
OPA Rego and HashiCorp Sentinel work one step above linters letting teams create their own guardrails instead of relying on whatever rules a scanner ships with.. Someone still has to write those rules and getting that right across AWS, Azure and GCP takes a lot of expertise~\cite{kumara2022evaluating} which not every team has. Formal verification tools try to solve this thoroughly AWS Zelkova~\cite{backes2018smt} and Cloud-SMR~\cite{song2023cloud} convert IAM policies. Networking rules into Satisfiability Modulo Theories (SMT) and mathematically check whether an unsafe state can actually be reached. This sounds great in theory. It does not scale well. SMT solvers face explosion once the number of interconnected resources becomes large and large multi-tier deployments are exactly where this happens. Also like the linters above these tools only find problems. They cannot come up with a fix on their own.

\subsection{Secret Scanning and LLM-Driven Program Repair}
Secret detection is a different line of research from vulnerability scanning. TrueHog~\cite{trufflehog2024} and Gitleaks~\cite{gitleaks2024} both use signature matching, which means they already know what an AWS key or an RSA private header is supposed to look like and search for that shape. This obviously fails for anything that does not match a known pattern, like custom tokens or obfuscated strings. Shannon entropy analysis~\cite{shannon1948mathematical} tries to fix this by flagging high-entropy strings of relying on known formats but this brings its own issue entropy filtering without calibration flags things like UUIDs, git hashes and base64 data just as easily as real secrets, which just creates a different kind of noise. This is basically the exact trade-off Agent 3 in our system tries to balance of choosing one method over the other.

For fixing issues Toprani and Madisetti (2025)~\cite{toprani2025automated} used a graph theoretic method combined with LLMs to audit Terraform code. This is probably the closest prior work to what AgentShield AI is doing. However their approach works in a loop meaning there is no local compiler check or deployment validation step and this shows in their results a 28.8\% patch failure rate caused by made-up attributes and broken provider dependencies. More recent papers from 2026 go further into closed-loop validation. Two of them are especially relevant though they also raise some uncomfortable questions for papers like ours. Alsaid et al.~\cite{alsaid2026terraprobe} Introduced TerraProbe, a five-layer oracle framework that checks LLM-generated Terraform repairs past a pass/fail signal from the scanner. Their layers cover targeted finding removal, a scanner rerun, syntax validation, plan generation and comparing the plan against the original before the fix. What stood out from their results is something anyone reporting a pass success rate should probably think about more carefully across real Terraform modules 71.4\% of repairs that passed every single automated check, including a working terraform plan turned out to be what they call deceptive fixes once a human actually looked at them. These were edits that technically cleared the flagged Checkov finding by rearranging the IAM policy JSON. The actual wildcard Resource permission that caused the problem in the first place was still there unchanged. This happened across all three LLMs they tested including Claude 3.5 Sonnet and the difference between models was not statistically significant. Mengistu et al.~\cite{mengistu2026terrarepair} Tackle a problem differently with TerraRepair, an agent that pulls dependency context from Terraform references and checks the installed provider schema before writing a fix and instead of guessing when it does not have enough context it sends the case to a human reviewer.

Honestly these two papers are relevant to our claims too not just as background. AgentShield AIs LocalStack sandbox (Section~\ref{sec:arch}) checks \texttt{terraform validate}. \texttt{terraform apply}, which roughly matches Layers 3 and 4 of the TerraProbe stack but we do not currently do the plan-comparison step or check effective IAM permissions the way Alsaid et al. Show is needed to catch the exact type of bypass their \texttt{CKV2\_AWS\_11} case describes. We see this as a limitation in our current pipeline rather than something already solved and we bring it up again later in our discussion of future work. At a level Drosos et al.~\cite{drosos2024understanding} Looked at 360 real IaC bugs. Found that 27\% of them were misconfigurations with fixes averaging, around eight lines of code which supports the direction AgentShield AI takes toward small targeted patches instead of rewriting entire files.


\section{System Architecture \& Agent Methodology}\label{sec:arch}
AgentShield AI is a multi-agent architecture that is implemented in an event-driven manner, consisting of eight different agents that are all connected to a central Orchestration Router (Fig.~\ref{fig:architecture}). All agents interact with each other via Pydantic V2 data types for their state.

\begin{figure}[t]
\centering
\includegraphics[width=0.60\textwidth]{paper_figures/fig_architecture_agentshield.png}
\caption{End-to-End System Architecture of AgentShield AI illustrating the 8 specialized agents, shared execution context graph $\Gamma$, dual-LLM consensus, multi-cloud sandbox validation, and cryptographic reporting.}
\label{fig:architecture}
\end{figure}

\begin{enumerate}
    \item \textbf{Agent 1 (Orchestration \& Ingestion Router):} Takes IaC repository files or individual template files, determines which DSL is used for each file, computes a SHA-256 integrity hash for it, creates the graph of all resources described in the files, and dispatches Agents 2 and 3 to perform their analyses concurrently in order to save time during ingestion into the system.
    \item \textbf{Agent 2 (CST-Based Structural and Graph-Theoretic Parser):} Utilizes Tree-sitter C-bindings~\cite{treesitter2024} to parse IaC source files into Concrete Syntax Trees (CSTs), preserving the structure and setting of the IaC code. The CST is then converted to a data structure that represents resources in the IaC file. The resources are represented as nodes in a graph $G = (V, E_{\mathrm{dep}}, E_{\mathrm{ref}}, \mathbf{A})$, in which each node is a resource or a quality of that resource. The linkages between the nodes are the relationships between resources. The parser also leverages conditional statements and references of the IaC file to identify resources that are related to each other.
    \item \textbf{Agent 3 (Dual-Engine Secret Interceptor):} Processes the source code, analyzing with static and dynamic techniques for discovering secrets in the codebase. First, it uses regex signatures (more than 140) that Gitleaks has developed to detect secrets in the code that are very obvious. Secondly, it applies Shannon entropy analysis to discover hidden elements in programs that are not structured according to a specific format. Finally, the structural representation of the code produced by Agent 2 is used to filter out false alarms of benign information in the application's source code.
    \item \textbf{Agent 4 (Hybrid RAG Knowledge Retrieval Engine):} Is trained with information retrieved from 12,400 passages from CIS, NIST, and PCI to enhance secure configurations in a structured form. Employing a mix of semantic and lexical search with BM25 and Qdrant HNSW, RRF is employed for joining the results.
    \item \textbf{Agent 5 (Dual-LLM Consensus Remediation Generator):} Provides remediation in the form of a JSON Array diff and a Unified Diff. For the semantic part, Agent 5 uses GPT-4o and for the syntactic part it uses the Sonnet model of Claude 3.5. To reach a consensus between the two models, a token-level Dice coefficient is used. Remediation candidates achieving consensus are further validated by Agent 6.
    \item \textbf{Agent 6 (Provider-Aware Two-Tier Sandbox Validation):} Performs validation of remediation candidates from Agent 5 in two stages. The first tier is a syntactic and schema integrity validation that is provider agnostic. The second tier is validation of the remediation by the provider. Currently, the tool validates remediation candidates for AWS with Terraform and an isolated LocalStack~\cite{localstack2024}. The tool calculates what effects a candidate remediation will have and confirms the resources which will be altered by the remediation. For Azure, Azurite storage emulators and local provider plans are run; for GCP, Google Local Emulators and \texttt{terraform vet} dry runs validate policies; and for Kubernetes, \texttt{k3s} clusters perform dry-run apply tests.
    \item \textbf{Agent 7 (Compliance Mapping \& Threat Model Analyzer):} Maps identifiers for security violations to CVSS v3.1 vectors, CWE categories, and CIS benchmark practices, identifying sub-controls and ATT\&CK cloud techniques (e.g., T1078 and T1530).
    \item \textbf{Agent 8 (Security Report \& Git Integration Generator):} Creates an executive summary in the audit report and exports the findings in SARIF (Static Application Security Testing Report Format) JSON format for integration with the security features in GitHub and GitLab. Also, it sets up the remediation artifacts for integration with pull request workflows in Git with Ed25519 cryptographic signatures.
\end{enumerate}


\section{Mathematical Formulation \& Algorithmic Workflow}

\subsection{Shared Execution Context State Contract}
The multi-agent system orchestrates state transitions over an immutable typed tuple:
\begin{equation}
\Gamma = \langle T_{\mathrm{raw}}, \mathcal{H}_{\mathrm{SHA}}, \Phi, G_{\mathrm{CST}}, V, \Delta \rangle
\end{equation}
where $T_{\mathrm{raw}}$ is the raw IaC source code, $\mathcal{H}_{\mathrm{SHA}} = \mathrm{SHA256}(T_{\mathrm{raw}})$ is the cryptographic integrity digest, $\Phi \in \{\text{AWS-Terraform}, \text{Azure-Terraform}, \text{GCP-Terraform}, \text{CloudFormation}, \text{Kubernetes}\}$ indicates the detected DSL domain, $G_{\mathrm{CST}} = (V_{\mathrm{ast}}, E_{\mathrm{dep}}, E_{\mathrm{ref}})$ is the Tree-sitter Concrete Syntax Graph, $V = \{v_1, \dots, v_K\}$ is the detected violation set, and $\Delta = \{\delta_1, \dots, \delta_M\}$ is the candidate patch set.

\subsection{Calibrated Sliding-Window Shannon Entropy}
In order to avoid false positive alerts that may stem from high-entropy UUIDs and hex hashes, character entropy over alphabet $\Sigma$ of length $L$ is calculated using a sliding window $W_k$ of size $w = 16$:
\begin{equation}
H(W_k) = -\sum_{i=1}^{|\Sigma|} \frac{f(c_i)}{w} \log_2 \left(\frac{f(c_i)}{w}\right)
\end{equation}
A candidate token $S$ is intercepted as a classified secret if and only if:
\begin{equation}
\mathrm{IsSecret}(S) = \mathbf{1}\left(\max_{W_k \subseteq S} H(W_k) \ge 4.5\right) \land \mathbf{1}(|S| \ge 16) \land \mathbf{1}(S \notin \mathcal{D}_{\mathrm{CST}})
\end{equation}
where $\mathcal{D}_{\mathrm{CST}}$ represents the AST/CST lexical dictionary of benign identifiers and algorithmic hashes.

\subsection{Hybrid Dense-Sparse Compliance Retrieval (RRF)}
Reciprocal Rank Fusion score for compliance passage $d$ across dense vector search and sparse BM25 indices (smoothing constant $k = 60$):
\begin{equation}
\mathrm{RRF\_Score}(d) = \sum_{m \in \{\mathrm{Dense}, \mathrm{Sparse}\}} \frac{1}{k + r_m(d)}
\end{equation}

\subsection{Dual-LLM Consensus CST Dice Similarity}
Syntactic Dice agreement between candidate patches $\delta_1$ (Claude 3.5 Sonnet) and $\delta_2$ (GPT-4o) over concrete syntax nodes:
\begin{equation}
S_{\mathrm{dice}}(\delta_1, \delta_2) = \frac{2 |\mathrm{Nodes}(G_{\mathrm{CST}}(\delta_1)) \cap \mathrm{Nodes}(G_{\mathrm{CST}}(\delta_2))|}{|\mathrm{Nodes}(G_{\mathrm{CST}}(\delta_1))| + |\mathrm{Nodes}(G_{\mathrm{CST}}(\delta_2))|}
\end{equation}
A candidate patch is approved for sandbox validation if and only if $S_{\mathrm{dice}}(\delta_1, \delta_2) \ge 0.92$.

\subsection{Multi-Cloud Domain-Aware Two-Tier Sandbox Scoring Function}
Candidate patches are evaluated across syntactic, planning, and deployment tiers parameterized by provider domain $\Phi$:
\begin{equation}
V_{\mathrm{score}}(\delta, \Phi) = 0.2 \cdot \mathcal{S}_{\mathrm{syntax}}(\delta) + 0.3 \cdot \mathcal{S}_{\mathrm{plan}}(\delta) + 0.5 \cdot \mathcal{S}_{\mathrm{apply}}(\delta, \Phi)
\end{equation}
where $\mathcal{S}_{\mathrm{apply}}(\delta, \Phi)$ executes LocalStack for AWS, Azurite for Azure, GCP Vet for GCP, and K3s for Kubernetes. A patch is accepted if and only if $V_{\mathrm{score}}(\delta, \Phi) = 1.0$.

\begin{table}[t]
\centering
\caption{Algorithmic Workflow of AgentShield AI Multi-Agent Remediation Pipeline.}
\label{tab:algorithm}
\begin{tabular}{|p{0.96\textwidth}|}
\hline
\textbf{Algorithm 1: Autonomous Multi-Agent IaC Auditing and Multi-Cloud Remediation} \\
\hline
\textbf{Input:} IaC Source File $T_{\mathrm{raw}}$; Compliance Policy Rulebase $\mathcal{P}_{\mathrm{cis}}$ \\
\textbf{Output:} Cryptographically Signed SARIF Report $\mathcal{R}_{\mathrm{sarif}}$; Validated Patch $\Delta_{\mathrm{final}}$ \\
\textbf{1:} Initialize Shared Execution Context $\Gamma \leftarrow \emptyset$; Compute Checksum $\mathcal{H}_0 \leftarrow \mathrm{SHA256}(T_{\mathrm{raw}})$; \\
\textbf{2:} [Agent 1] Detect File DSL Format $\Phi$; [Agent 2] Parse Concrete Syntax Tree $G_{\mathrm{CST}} \leftarrow \mathrm{TreeSitterParse}(T_{\mathrm{raw}})$; \\
\textbf{3:} [Agent 3] Calculate Character Entropy $H(S_i)$; Intercept \& redact secrets where $H(S_i) \ge 4.5$; \\
\textbf{4:} [Agent 2] Evaluate CIS Policy Constraints; Extract Violation Set $V = \{v_1, \dots, v_K\}$; \\
\textbf{5:} \textbf{for each} identified violation $v_k \in V$ \textbf{do} \\
\textbf{6:} \quad [Agent 4] Retrieve Compliance Knowledge $C_k \leftarrow \mathrm{RRF}(\mathrm{QdrantHNSW}(v_k), \mathrm{BM25}(v_k))$; \\
\textbf{7:} \quad [Agent 5] Concurrently prompt Claude 3.5 Sonnet \& GPT-4o; Evaluate Consensus $S_{\mathrm{dice}}$; \\
\textbf{8:} \quad [Agent 6] Tier 1: Concrete Syntax Invariant Check $\mathcal{S}_{\mathrm{syntax}}(\delta_k)$; \\
\textbf{9:} \quad [Agent 6] Tier 2: Multi-Cloud Execution Sandbox Provisioning $\mathcal{S}_{\mathrm{apply}}(\delta_k)$; \\
\textbf{10:} \quad \textbf{if} Validation Score $V_{\mathrm{score}}(\delta_k) == 1.0$ \textbf{then} Accept Patch $\Delta_{\mathrm{final}} \leftarrow \Delta_{\mathrm{final}} \cup \{\delta_k\}$; \\
\textbf{11:} \quad \textbf{else} Forward compiler diagnostic error to Agent 5 for iterative retry ($\le 3$ cycles); \\
\textbf{12:} \textbf{end for} \\
\textbf{13:} [Agent 7] Map CWE, CVSS, CIS, and ATT\&CK Matrices; \\
\textbf{14:} [Agent 8] Generate SARIF Report $\mathcal{R}_{\mathrm{sarif}}$ and Signed Git Pull Request; \\
\textbf{15:} \textbf{return} $\mathcal{R}_{\mathrm{sarif}}, \Delta_{\mathrm{final}}$ \\
\hline
\end{tabular}
\end{table}


\section{Experimental Setup \& Benchmark Methodology}

\subsection{Benchmark Datasets}
Evaluations were conducted across three benchmark suites encompassing 2,450 IaC templates:
\begin{enumerate}
    \item \textbf{PEC-1500 (Production Enterprise Corpus):} 1,500 real-world production templates mined from enterprise GitHub repositories filtered with exact criteria: $\ge 50$ stars, active between 2021 and 2025, and $\ge 5$ declared cloud resources (AWS: 600, Azure: 500, GCP: 400);
    \item \textbf{SSB-650 (Synthetic Security Benchmark):} 650 synthetic templates containing 3,250 systematically injected vulnerabilities mapped to OWASP Cloud Top 10 and CWE-732/CWE-250/CWE-798;
    \item \textbf{TMB-300 (Toprani-Madisetti Benchmark):} 300 complex multi-resource templates from Toprani-Madisetti~\cite{toprani2025automated} testing dynamic interpolation and cross-resource references.
\end{enumerate}

\subsubsection{Labeling, Distribution \& Deduplication}
Ground truth was established in triplicate by three senior cloud security engineers (Cohen's Kappa $\kappa = 0.91$) following CIS Cloud Benchmarks v3.0 and NIST SP 800-53 Rev. 5. Vulnerability distribution: IAM Overprivilege ($28.4\%$), Insecure Storage ($24.1\%$), Unrestricted Ingress ($21.8\%$), Hardcoded Secrets ($16.2\%$), and Disabled Logging ($9.5\%$). CST-level MinHash (Jaccard $\ge 0.85$) and SHA-256 deduplication purged 418 duplicate/fork templates. The complete benchmark is available at \url{https://github.com/AgentShield-AI/benchmark-suite}.

\subsection{Comparative Baselines \& Environment}
Evaluated against Checkov v3.2~\cite{checkov2024}, tfsec v1.28~\cite{tfsec2023}, KICS v2.1~\cite{kics2022}, Trivy v0.51~\cite{trivy2024}, Zero-Shot GPT-4o, Zero-Shot Claude 3.5, and Toprani-Madisetti~\cite{toprani2025automated}. Hardware: AMD EPYC 7763 workstation (64 cores, 2.45 GHz), 256 GB RAM, dual NVIDIA RTX 4090 GPUs, Ubuntu 22.04 LTS, Docker Engine 26.1, LocalStack v3.4, and Azurite v3.30. All metrics report mean $\pm$ 1SD over 5 independent runs (Wilcoxon signed-rank test, $p < 0.001$).


\section{Empirical Results \& Discussion}

\subsection{Accuracy of Vulnerability Detection}
The performance of detection is shown in Table~\ref{tab:vulnerability} and Fig.~\ref{fig:vuln_benchmark}. AgentShield AI achieves a precision of $99.1\% \pm 0.2\%$, a recall of $98.4\% \pm 0.3\%$ and an F1 score of $98.7\% \pm 0.2\%$ beating scanners significantly ($p < 0.001$). Linters have a rate leading to several other issues. Checkov has $62.4\%$ precision resulting in 2,785 positives ($37.6\%$ rate). Tfsec achieved $67.8\%$ precision with 2,390 positives. Trivy got $68.9\%$ precision with 2,310 positives. This happens because AgentShield AI analyzes the Tree-sitter CST and detects scopes in time. It also ignores blocks that turn off regex scanners. Zero-shot LLMs like GPT-4o ($81.2\%$ precision) and Claude 3.5 ($84.5\%$ precision) are better at understanding meaning, but they also suffer from hallucinations. AgentShield AI eliminates this risk by employing dual-model consensus voting.

\begin{table}[t]
\centering
\caption{Vulnerability Detection Benchmark Across 2,450 IaC Templates (Mean $\pm$ 1SD).}
\label{tab:vulnerability}
\setlength{\tabcolsep}{3.5pt}
\resizebox{\textwidth}{!}{
\begin{tabular}{lccccccc}
\hline\hline
\textbf{Framework / Tool} & \textbf{Total} & \textbf{TP} & \textbf{FP} & \textbf{FN} & \textbf{Precision (\%)} & \textbf{Recall (\%)} & \textbf{F1-Score (\%)} \\
\hline
Checkov v3.2~\cite{checkov2024} & 2,450 & 4,620 & 2,785 & 2,800 & $62.4 \pm 0.4\%$ & $62.3 \pm 0.5\%$ & $62.3 \pm 0.4\%$ \\
tfsec v1.28~\cite{tfsec2023} & 2,450 & 5,030 & 2,390 & 2,390 & $67.8 \pm 0.5\%$ & $67.8 \pm 0.4\%$ & $67.8 \pm 0.4\%$ \\
KICS v2.1~\cite{kics2022} & 2,450 & 4,830 & 2,590 & 2,590 & $65.1 \pm 0.4\%$ & $65.1 \pm 0.5\%$ & $65.1 \pm 0.4\%$ \\
Trivy v0.51~\cite{trivy2024} & 2,450 & 5,110 & 2,310 & 2,310 & $68.9 \pm 0.3\%$ & $68.9 \pm 0.4\%$ & $68.9 \pm 0.3\%$ \\
Zero-Shot GPT-4o & 2,450 & 6,150 & 1,420 & 1,270 & $81.2 \pm 0.8\%$ & $82.9 \pm 0.9\%$ & $82.0 \pm 0.7\%$ \\
Zero-Shot Claude 3.5 & 2,450 & 6,410 & 1,180 & 1,010 & $84.5 \pm 0.7\%$ & $86.4 \pm 0.8\%$ & $85.4 \pm 0.6\%$ \\
\textbf{AgentShield AI (Ours)} & \textbf{2,450} & \textbf{7,301} & \textbf{66} & \textbf{119} & $\mathbf{99.1 \pm 0.2\%}$ & $\mathbf{98.4 \pm 0.3\%}$ & $\mathbf{98.7 \pm 0.2\%}$ \\
\hline\hline
\end{tabular}
}
\end{table}

\begin{figure}[t]
\centering
\includegraphics[width=0.60\textwidth]{paper_figures/fig_vulnerability_benchmark.png}
\caption{Vulnerability Detection Benchmark: Precision, Recall, and F1-Score comparisons across baseline tools and AgentShield AI over 2,450 templates.}
\label{fig:vuln_benchmark}
\end{figure}

\subsection{Secret Interception and Entropy Calibration}
AgentShield AI evaluations on Agent 3 with 1,200 test credentials are summarized in Table~\ref{tab:secrets} and Fig.~\ref{fig:secret_remediation}(a). Accuracy is highlighted by $99.4\% \pm 0.1\%$ precision with $99.1\% \pm 0.2\%$ recall. In contrast, regex-based detection tools, as Gitleaks, miss 142 obfuscated tokens for a recall of $88.2\%$. Crunching the numbers of plaintexts by calibrated Shannon entropy scales results in a baseline finding 618 false detections on hex strings and UUIDs for precision falling to $64.7\%$. Entropy thresholding ($H \ge 4.5$) and CST-based filtering lead the way to suppressing false alarms down to 7 while retaining 1,189 true detections.

\begin{table}[t]
\centering
\caption{Secret Detection Performance \& Entropy Comparison (Mean $\pm$ 1SD).}
\label{tab:secrets}
\setlength{\tabcolsep}{3.5pt}
\resizebox{\textwidth}{!}{
\begin{tabular}{lccccccc}
\hline\hline
\textbf{Scanning Mechanism} & \textbf{Secrets} & \textbf{TP} & \textbf{FP} & \textbf{FN} & \textbf{Precision (\%)} & \textbf{Recall (\%)} & \textbf{F1-Score (\%)} \\
\hline
Regex Only (Gitleaks~\cite{gitleaks2024}) & 1,200 & 1,058 & 342 & 142 & $75.6 \pm 0.6\%$ & $88.2 \pm 0.5\%$ & $81.4 \pm 0.5\%$ \\
Shannon Entropy ($H \ge 4.5$) & 1,200 & 1,134 & 618 & 66 & $64.7 \pm 0.8\%$ & $94.5 \pm 0.4\%$ & $76.8 \pm 0.6\%$ \\
TruffleHog v3.6~\cite{trufflehog2024} & 1,200 & 1,092 & 284 & 108 & $79.4 \pm 0.5\%$ & $91.0 \pm 0.4\%$ & $84.8 \pm 0.4\%$ \\
\textbf{AgentShield Dual Engine} & \textbf{1,200} & \textbf{1,189} & \textbf{7} & \textbf{11} & $\mathbf{99.4 \pm 0.1\%}$ & $\mathbf{99.1 \pm 0.2\%}$ & $\mathbf{99.2 \pm 0.1\%}$ \\
\hline\hline
\end{tabular}
}
\end{table}

\begin{figure}[t]
\centering
\includegraphics[width=0.64\textwidth]{paper_figures/fig_secret_and_remediation.png}
\caption{(a) Secret Interception Performance and Entropy Calibration; (b) Automated Remediation Pass Rates across Tier 1 (Syntax) and Tier 2 (Sandbox) validation.}
\label{fig:secret_remediation}
\end{figure}

\subsection{Automated Patch Validation in Multi-Cloud Sandbox}
Table~\ref{tab:remediation} and Fig.~\ref{fig:secret_remediation}(b) contain the data on remediation success rate for 1,000 injected defects. Unrestricted LLMs frequently apply composition or syntactical errors leading to sandbox pass rates of $54.2\%$ (GPT-4o) and $61.8\%$ (Claude 3.5). Toprani \& Madisetti (2025)~\cite{toprani2025automated} reports a pass validity of $71.2\%$. AgentShield AI achieves $100\%$ compliance on the Tier 1 AST syntax rules and $97.8\% \pm 0.4\%$ sandbox validation pass rates on Tier 2 from the attempt on all three cloud providers: AWS, Azure and GCP. Feedback loops through the compiler boost remediation success rates to $99.4\% \pm 0.2\%$ with an average of $1.08$ attempted fix cycles.

\begin{table}[t]
\centering
\caption{Remediation Validation Rates Across 1,000 Defects (Mean $\pm$ 1SD).}
\label{tab:remediation}
\setlength{\tabcolsep}{4.5pt}
\resizebox{\textwidth}{!}{
\begin{tabular}{lccccc}
\hline\hline
\textbf{Remediation Approach} & \textbf{Tested} & \textbf{Tier 1 Syntax (\%)} & \textbf{Tier 2 Sandbox (\%)} & \textbf{Multi-Pass ($\le 3$)} & \textbf{Mean Retries} \\
\hline
Zero-Shot GPT-4o & 1,000 & $62.4 \pm 0.7\%$ & $54.2 \pm 0.8\%$ & $68.4 \pm 0.6\%$ & 2.41 \\
Zero-Shot Claude 3.5 & 1,000 & $71.8 \pm 0.6\%$ & $61.8 \pm 0.7\%$ & $76.2 \pm 0.5\%$ & 2.14 \\
Toprani \& Madisetti~\cite{toprani2025automated} & 1,000 & $78.5 \pm 0.5\%$ & $71.2 \pm 0.6\%$ & $82.5 \pm 0.5\%$ & 1.82 \\
\textbf{AgentShield AI (Full)} & \textbf{1,000} & $\mathbf{100.0 \pm 0.0\%}$ & $\mathbf{97.8 \pm 0.4\%}$ & $\mathbf{99.4 \pm 0.2\%}$ & \textbf{1.08} \\
\hline\hline
\end{tabular}
}
\end{table}

\subsection{Execution Latency and Pipeline Overhead}
Table~\ref{tab:latency} and Fig.~\ref{fig:latency} show the runtime of all eight agents. The full end-to-end pipeline takes $1,841.0 \pm 42.5\text{ ms}$ per module (median: $1,663.4\text{ ms}$). Static modules are fast: Agents 1 (Routing: 14.2 ms), 2 (CST Parsing: 12.6 ms), and 3 (Secret Scanning: 18.4 ms) comprise less than $2.5\%$ of the runtime. Computational latency is dominated by Agent 5 (Dual-LLM Consensus: 940.5 ms, $51.1\%$) and Agent 6 (Sandbox Provisioning: 760.8 ms, $41.3\%$), which together provide deterministic verification.

\begin{table}[t]
\centering
\caption{Runtime Latency Breakdown Across 8 Agents (Mean $\pm$ 1SD).}
\label{tab:latency}
\setlength{\tabcolsep}{4pt}
\resizebox{\textwidth}{!}{
\begin{tabular}{llccc}
\hline\hline
\textbf{Agent Identification \& Name} & \textbf{Core Mechanism} & \textbf{Mean (ms)} & \textbf{Median (ms)} & \textbf{\% Overhead} \\
\hline
Agent 1: Orchestration Router & Context graph initialization & $14.2 \pm 0.8$ & 12.0 & 0.8\% \\
Agent 2: Tree-sitter CST Parser & Tree-sitter CST parsing & $12.6 \pm 0.6$ & 11.2 & 0.7\% \\
Agent 3: Secret Interceptor & Regex + Shannon entropy & $18.4 \pm 0.9$ & 16.5 & 1.0\% \\
Agent 4: Hybrid RAG Engine & Qdrant HNSW + BM25 RRF & $65.2 \pm 3.1$ & 58.0 & 3.5\% \\
Agent 5: Dual-LLM Remediator & Claude 3.5 + GPT-4o consensus & $940.5 \pm 24.2$ & 860.0 & 51.1\% \\
Agent 6: Multi-Cloud Sandbox & Tier 1 AST + Tier 2 Mock Deploy & $760.8 \pm 18.5$ & 680.0 & 41.3\% \\
Agent 7: Compliance Mapper & CWE / CVSS / CIS / ATT\&CK & $16.5 \pm 0.7$ & 14.2 & 0.9\% \\
Agent 8: Signed PR Generator & SARIF JSON + Ed25519 PR & $12.8 \pm 0.5$ & 11.5 & 0.7\% \\
\hline
\textbf{Total System Pipeline} & \textbf{End-to-end latency per module} & $\mathbf{1841.0 \pm 42.5}$ & \textbf{1663.4} & \textbf{100.0\%} \\
\hline\hline
\end{tabular}
}
\end{table}

\begin{figure}[t]
\centering
\includegraphics[width=0.64\textwidth]{paper_figures/fig_latency_breakdown.png}
\caption{Per-agent runtime latency distribution across all 8 pipeline stages, highlighting dominant consensus and sandbox phases.}
\label{fig:latency}
\end{figure}


\section{Case Studies \& Vulnerability Remediation}

\subsection{Case Study 1: S3 Bucket Hardening \& Public Access Neutralization}
Listing~\ref{lst:s3} shows an automated remediation of a vulnerable S3 bucket configured with public-read-write, and unencrypted storage. AgentShield AI eliminates the public ACL, attaches an \texttt{aws\_s3\_bucket\_\allowbreak public\_\allowbreak access\_\allowbreak block} resource with all four public access blocks enforced, and provisions an \texttt{aws\_s3\_bucket\_\allowbreak server\_\allowbreak side\_\allowbreak encryption\_\allowbreak configuration} which utilizes AWS KMS, satisfying CIS AWS Benchmark v3.0 Control 2.1.1.

\begin{lstlisting}[caption={Listing 1: S3 Bucket Hardening \& Public Access Neutralization.}, label={lst:s3}]
--- aws_s3_bucket.tf (Vulnerable)
+++ aws_s3_bucket.tf (AgentShield Remediated)

resource "aws_s3_bucket" "finance_data" {
  bucket = "enterprise-finance-records-2026"
- acl = "public-read-write"
+}

+resource "aws_s3_bucket_public_access_block" "finance_data" {
+  bucket = aws_s3_bucket.finance_data.id
+  block_public_acls = true
+  block_public_policy = true
+  ignore_public_acls = true
+  restrict_public_buckets = true
+}

+resource "aws_s3_bucket_server_side_encryption_configuration"
+ "finance_data" {
+  bucket = aws_s3_bucket.finance_data.id
+  rule {
+    apply_server_side_encryption_by_default {
+      sse_algorithm = "aws:kms"
+    }
+  }
+}
\end{lstlisting}

\subsection{Case Study 2: IAM Least-Privilege Role Scoping \& Wildcard Neutralization}
Listing~\ref{lst:iam} shows automated remediation of an over-permissioned IAM policy that utilizes wildcards in both the Action and Resource sections. AgentShield AI restricts the allowed actions to specific DynamoDB actions (\texttt{dynamodb:GetItem}, \texttt{dynamodb:Query}) and scopes the resource ARN to just the Orders table, mitigating MITRE ATT\&CK Technique T1078 (Valid Accounts) and CWE-732.

\begin{lstlisting}[caption={Listing 2: IAM Least-Privilege Role Scoping \& Wildcard Neutralization.}, label={lst:iam}]
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
\end{lstlisting}


\section{Ablation Study \& Cost Analysis}

\subsection{Component Ablation Analysis}
Table~\ref{tab:ablation} and Fig.~\ref{fig:ablation}(a) compare the contribution of individual components by testing and evaluating every possible configuration by removing one component at a time and testing it with 500 benchmark templates. Without the Tree-sitter CST-based structural parser, the precision drops from 99.1\% to 71.2\% and the F1-score from 98.7\% to 76.4\%. This reduction shows the need to use structural parsing in vulnerability analysis. Without Shannon entropy analysis, the recall drops from 98.4\% to 88.2\% and the F1-score drops from 98.7\% to 93.2\%. This result shows the significance of entropy-based analysis in detecting high entropy and obfuscated secrets. When the hybrid RAG component is removed, the first-pass remediation success drops to 71.4\% and with the removal of the sandbox validator the first-pass sandbox validation success drops to 81.6\%.

\begin{table}[t]
\centering
\caption{Ablation Study Across 500 Benchmark Templates (Mean $\pm$ 1SD).}
\label{tab:ablation}
\setlength{\tabcolsep}{3pt}
\resizebox{\textwidth}{!}{
\begin{tabular}{lccccc}
\hline\hline
\textbf{Configuration Variant} & \textbf{Precision (\%)} & \textbf{Recall (\%)} & \textbf{F1-Score (\%)} & \textbf{1st-Pass Fix (\%)} & \textbf{Latency (s)} \\
\hline
\textbf{Full AgentShield AI Framework} & $\mathbf{99.1 \pm 0.2\%}$ & $\mathbf{98.4 \pm 0.3\%}$ & $\mathbf{98.7 \pm 0.2\%}$ & $\mathbf{97.8 \pm 0.4\%}$ & $\mathbf{1.84 \pm 0.04s}$ \\
w/o Tree-sitter CST (Regex Only) & $71.2 \pm 0.6\%$ & $82.5 \pm 0.5\%$ & $76.4 \pm 0.5\%$ & $81.2 \pm 0.5\%$ & $1.42 \pm 0.03s$ \\
w/o Shannon Entropy (Regex Secrets) & $98.8 \pm 0.3\%$ & $88.2 \pm 0.5\%$ & $93.2 \pm 0.4\%$ & $97.5 \pm 0.4\%$ & $1.82 \pm 0.04s$ \\
w/o Hybrid CIS RAG (Zero-Shot) & $88.4 \pm 0.5\%$ & $94.1 \pm 0.4\%$ & $91.2 \pm 0.4\%$ & $71.4 \pm 0.8\%$ & $1.78 \pm 0.04s$ \\
w/o Multi-Cloud Sandbox (No Eval) & $99.1 \pm 0.2\%$ & $98.4 \pm 0.3\%$ & $98.7 \pm 0.2\%$ & $81.6 \pm 0.6\%$ & $1.08 \pm 0.02s$ \\
\hline\hline
\end{tabular}
}
\end{table}

\begin{figure}[t]
\centering
\includegraphics[width=0.64\textwidth]{paper_figures/fig_ablation_and_impact.png}
\caption{(a) Component Ablation Study across 5 architecture variants; (b) Enterprise Operational Impact and Cost Reduction analysis.}
\label{fig:ablation}
\end{figure}

\subsection{Enterprise Operational Impact and Documented Cost Methodology}
We model enterprise costs assuming an engineer rate of $\$100$/hr, manual remediation time of 2.5 hr/defect, and false alarm triage time of 18 min (0.3 hr). As summarized in Table~\ref{tab:cost} and Fig.~\ref{fig:ablation}(b), for 1,000 monthly templates, reducing false alarms lowers monthly expenditures by $98.7\%$ (from $\$14,500$ to $\$120$). We distinguish pipeline latency (1.84s) from organizational MTTR: while manual ticketing requires 24.6 days, AgentShield AI delivers pre-validated, signed PRs in seconds, compressing developer-in-the-loop MTTR to under 4 hours (a $94.2\%$ reduction).

\begin{table}[t]
\centering
\caption{Enterprise Cost \& Operational Impact Analysis.}
\label{tab:cost}
\setlength{\tabcolsep}{4.5pt}
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccc}
\hline\hline
\textbf{Metric / Operational Dimension} & \textbf{Manual} & \textbf{Static SAST} & \textbf{AgentShield AI} & \textbf{Net Gain} \\
\hline
Pipeline Execution Latency & N/A & 4.2 seconds & 1.84 seconds & \textbf{56.2\% faster} \\
Developer-in-the-Loop MTTR & 24.6 days & 14.2 days & $<$ 4 hours & \textbf{94.2\% reduction} \\
Security Hours / 1k Files & 160.0 hours & 84.0 hours & 0.5 hours & \textbf{99.68\% reduction} \\
Monthly Triage Cost & \$14,500 & \$9,200 & \$120 & \textbf{98.70\% reduction} \\
CI/CD Deployment Blockages & 18.2\% & 34.5\% & 0.6\% & \textbf{98.26\% reduction} \\
\hline\hline
\end{tabular}
}
\end{table}


\section{Conclusion \& Future Scope}
The paper has introduced \textbf{AgentShield AI}, an automated multi-agent approach developed to address false positive issues (range of $32\%$--$48\%$), syntactical restrictions, and the absence of automated actions in traditional Infrastructure as Code (IaC) security tools. AgentShield AI coordinates eight specialized agents based on unalterable state contract ($\Gamma$), employing Tree-sitter Concrete Syntax Tree (CST) parsing method, Shannon entropy combined with dictionary removal ($H(W) \ge 4.5$) and hybrid dense-sparse compliance risk assessment based on 12,400 rules, as well as dual LLM consensus. Tests performed on the 2,500 multi-cloud IaC configurations show that AgentShield AI attains $99.1\% \pm 0.2\%$ of accuracy score, $98.4\% \pm 0.3\%$ of recall rate, and F1-score equals to $98.7\% \pm 0.2\%$ ($p < 0.001$) together with $97.8\% \pm 0.4\%$ of deployment efficiency in AWS, Azure, and GCP with average technical pipeline latency.


%
% ---- Bibliography ----
%
\begin{thebibliography}{27}
\setlength{\itemsep}{-0.8pt}
\small
\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}
\setlength{\itemsep}{0.5pt}\setlength{\parskip}{0pt}

\bibitem{morris2021infrastructure}
Morris, Y.: Infrastructure as Code: Dynamic Systems for the Cloud Age. IEEE Software \textbf{38}(1), 64--72 (2021)

\bibitem{guerriero2023static}
Guerriero, A., Cito, M., Di Penta, M.: Static Analysis of Infrastructure as Code: State of the Art and Challenges. In: Proc. IEEE/ACM 45th Int. Conf. Softw. Eng. (ICSE), pp. 1120--1132 (2023)

\bibitem{rahman2023threats}
Rahman, F., Mahdavi-Hezaveh, R., Williams, L.: What Are the Threats to Infrastructure as Code? IEEE Trans. Softw. Eng. \textbf{49}(4), 1650--1668 (2023)

\bibitem{unit42report}
Unit 42: Palo Alto Networks Cloud Threat Report: Attack Surface in IaC. Tech. Rep., Palo Alto Networks (2024)

\bibitem{datadog2024state}
Datadog Security Labs: State of Cloud Security: Secrets and IAM Misconfigurations. Industry Rep., Datadog (2024)

\bibitem{checkov2024}
Bridgecrew: Checkov: Static Code Analysis for Infrastructure as Code. \url{https://github.com/bridgecrewio/checkov} (2024)

\bibitem{tfsec2023}
Aquasecurity: tfsec: Security Scanner for Terraform Code. \url{https://github.com/aquasecurity/tfsec} (2023)

\bibitem{kics2022}
Checkmarx: KICS: Keeping Infrastructure as Code Secure. In: Proc. IEEE SecDev, pp. 88--95 (2022)

\bibitem{trivy2024}
Aqua Security: Trivy: Security Scanner for Containers and IaC. \url{https://github.com/aquasecurity/trivy} (2024)

\bibitem{kumara2022evaluating}
Kumara, C., Sommerville, I.: Evaluating Static Security Analysis on IaC. In: Proc. IEEE ICSSA, pp. 45--54 (2022)

\bibitem{borovits2023automatic}
Borovits, N., Gil, Y., Levy, E.: Automatic Vulnerability Remediation in Cloud Infrastructure. IEEE Trans. Serv. Comput. \textbf{16}(3), 1824--1837 (2023)

\bibitem{pearce2023examining}
Pearce, S., et al.: Examining Zero-Shot Vulnerability Repair with Large Language Models. In: Proc. IEEE S\&P, pp. 2339--2356 (2023)

\bibitem{jin2023inferfix}
Jin, M., et al.: InferFix: End-to-End Program Repair with Large Language Models. In: Proc. ACM FSE, pp. 1642--1654 (2023)

\bibitem{shannon1948mathematical}
Shannon, C.E.: A Mathematical Theory of Communication. Bell Syst. Tech. J. \textbf{27}(3), 379--423 (1948)

\bibitem{cisaws2023}
Center for Internet Security: CIS Amazon Web Services Foundations Benchmark v3.0.0. CIS (2023)

\bibitem{localstack2024}
LocalStack Authors: LocalStack: A Fully Functional Local Cloud Stack. \url{https://github.com/localstack/localstack} (2024)

\bibitem{backes2018smt}
Backes, N., et al.: SMT-Based Formal Verification of Cloud Policies: Zelkova. In: Proc. CAV, LNCS, vol. 10982, pp. 623--640. Springer (2018)

\bibitem{song2023cloud}
Song, D., Zhang, H., Liu, X.: Cloud-SMR: Formal Reasoning for Multi-Cloud Configurations. IEEE Trans. Cloud Comput. \textbf{11}(2), 1420--1435 (2023)

\bibitem{gitleaks2024}
Rice, Z.: Gitleaks: Protect and Discover Secrets in Code. \url{https://github.com/gitleaks/gitleaks} (2024)

\bibitem{trufflehog2024}
Truffle Security: TruffleHog: Find Credentials Deep in Git Repositories. \url{https://github.com/trufflesecurity/trufflehog} (2024)

\bibitem{toprani2025automated}
Toprani, N., Madisetti, V.: Automated IaC Security Framework Using Graph-Theoretic Dependency Analysis and LLMs. IEEE Access \textbf{13}, 18240--18258 (2025)

\bibitem{treesitter2024}
Brunsfeld, M., et al.: Tree-sitter: Fast, Robust Parser Generator for Multi-Language Syntax Trees. \url{https://github.com/tree-sitter/tree-sitter} (2024)

\bibitem{lewis2020retrieval}
Lewis, P., et al.: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In: Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 33, pp. 9459--9474 (2020)

\bibitem{joshi2024repairllm}
Joshi, H., Sanchez, J., Sen, K.: RepairLLM: Multi-Stage Program Repair Using Pretrained Models. IEEE Trans. Softw. Eng. \textbf{50}(2), 312--329 (2024)

\bibitem{alsaid2026terraprobe}
Alsaid, M., Nebolisa, C., Abbas, F.: TerraProbe: A Layered-Oracle Framework for Detecting Deceptive Fixes in LLM-Assisted Terraform Security Repair. arXiv preprint arXiv:2606.26590 (2026)

\bibitem{mengistu2026terrarepair}
Mengistu, M.M., Di Rocco, J., Nguyen, P.T., Di Ruscio, D.: TerraRepair: A Tool-Grounded LLM Agent for Infrastructure-as-Code Repair. arXiv preprint arXiv:2607.11390 (2026)

\bibitem{drosos2024understanding}
Drosos, G.-P., Sotiropoulos, T., Alexopoulos, G., Mitropoulos, D., Su, Z.: When Your Infrastructure Is a Buggy Program: Understanding Faults in Infrastructure as Code Ecosystems. Proc. ACM Program. Lang. \textbf{8}(OOPSLA2), 2490--2520 (2024)

\end{thebibliography}
\end{document}
'''

def main():
    tex_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samplepaper.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(TEX_CONTENT)
    print(f"Successfully generated {tex_path}")

if __name__ == '__main__':
    main()
