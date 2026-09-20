import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../landing.css'

export default function Landing() {
  const [activeModal, setActiveModal] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState(0)
  const [activeDiffTab, setActiveDiffTab] = useState('terraform')
  const [diffViewMode, setDiffViewMode] = useState('diff') // 'diff' or 'original'

  const agentsList = [
    {
      id: 'manager',
      name: 'Manager / Router',
      role: 'LangGraph Orchestrator',
      engine: 'StateGraph Engine',
      latency: '12ms',
      badge: 'Active Node',
      input: 'Raw IaC Template (.tf, .yaml, .json)',
      output: 'Initialized AgentShieldWorkspace session',
      desc: 'Orchestrates non-linear execution across parallel scanner nodes, tracks state checkpoints, and handles fault-tolerant fallbacks.'
    },
    {
      id: 'ast',
      name: 'Hybrid AST Parser',
      role: 'Static Syntax & Dependency Engine',
      engine: 'HCL2 / YAML / JSON Tree-Sitter',
      latency: '180ms',
      badge: 'AST Extracted',
      input: 'Template source files',
      output: 'Normalized AST & Resource Dependency Graph (RDG)',
      desc: 'Parses code into structured AST nodes, pre-evaluates variables/locals, and unfolds loops (for_each/count) to eliminate ambiguity.'
    },
    {
      id: 'secrets',
      name: 'Secrets Scanner',
      role: 'Zero-Leakage Credential Interceptor',
      engine: 'Gitleaks + TruffleHog + Entropy Scanner',
      latency: '95ms',
      badge: '0 Leaks Sent',
      input: 'Raw IaC content strings',
      output: 'Cryptographically masked code ([REDACTED_HASH])',
      desc: 'Intercepts AWS access keys, RSA private keys, and API tokens, redacting them locally before any data leaves for LLM evaluation.'
    },
    {
      id: 'rag',
      name: 'RAG Query Agent',
      role: 'Compliance & Policy Context Engine',
      engine: 'Qdrant Vector DB + MiniLM Embeddings',
      latency: '210ms',
      badge: 'Top-3 Policies',
      input: 'AST resource types & properties',
      output: 'Contextual CIS Benchmarks, NIST & SOC 2 rules',
      desc: 'Executes hybrid vector similarity and BM25 search against 50,000+ cloud security policies to ground LLM reasoning in verified rules.'
    },
    {
      id: 'analyst',
      name: 'Security Analyst',
      role: 'Multi-LLM Ensemble Consensus',
      engine: 'Claude 3.5 Sonnet + OpenAI GPT-4o',
      latency: '1.4s',
      badge: 'C_ens: 0.96 (High)',
      input: 'Enriched AST nodes & regulatory context',
      output: 'Calibrated vulnerability findings (auto_patchable)',
      desc: 'Executes cross-model verification to eradicate hallucinations. Findings with C_ens >= 0.85 proceed to auto-patching; others route to human triage.'
    },
    {
      id: 'remediation',
      name: 'Remediation Agent',
      role: 'Code Patch Synthesizer',
      engine: 'Deterministic Diff Generator',
      latency: '820ms',
      badge: 'Unified Git Diff',
      input: 'Confirmed vulnerability & AST line range',
      output: 'Executable unified git diff patch',
      desc: 'Synthesizes surgical code patches targeting the exact misconfigured resource block while preserving indentation, comments, and conventions.'
    },
    {
      id: 'validator',
      name: 'Validator Agent',
      role: 'Dual-Stage Sandbox Validation',
      engine: 'terraform validate + LocalStack Sandbox',
      latency: '1.8s',
      badge: 'Sandbox: PASSED',
      input: 'Proposed git diff patch',
      output: 'ValidationCheckResult (Syntax & Runtime)',
      desc: 'Applies patch in memory, verifies syntax via native linters, and dry-run deploys against a local LocalStack sandbox with up to 3 self-healing retries.'
    },
    {
      id: 'reporter',
      name: 'Report & Feedback',
      role: 'Audit Generator & Prompt Adaptor',
      engine: 'Dynamic Few-Shot Learning Store',
      latency: '140ms',
      badge: 'Report Ready',
      input: 'Validated workspace state & developer actions',
      output: 'Audit reports (SOC 2, NIST, PCI) & prompt updates',
      desc: 'Generates compliance reports and captures developer accept/reject actions to inject negative-shot constraints into future analysis prompts.'
    }
  ]

  const diffExamples = {
    terraform: {
      title: 'Terraform — AWS S3 Bucket Public Exposure',
      file: 'modules/storage/main.tf',
      framework: 'SOC 2 CC6.1 • CIS AWS 2.1.1',
      original: `resource "aws_s3_bucket" "audit_records" {
  bucket = "corp-financial-records-2026"
  acl    = "public-read" # CRITICAL: Publicly accessible

  tags = {
    Environment = "production"
  }
}`,
      diff: `@@ -1,6 +1,11 @@
 resource "aws_s3_bucket" "audit_records" {
   bucket = "corp-financial-records-2026"
-  acl    = "public-read"
+  acl    = "private"
+
+  server_side_encryption_configuration {
+    rule {
+      apply_server_side_encryption_by_default {
+        sse_algorithm = "AES256"
+      }
+    }
+  }
   tags = {
     Environment = "production"
   }`
    },
    cloudformation: {
      title: 'CloudFormation — Overprivileged IAM Wildcard Role',
      file: 'infrastructure/auth-roles.yaml',
      framework: 'NIST SP 800-53 AC-3 • PCI-DSS 7.1',
      original: `Resources:
  ApplicationExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      Policies:
        - PolicyName: AppPolicy
          PolicyDocument:
            Statement:
              - Effect: Allow
                Action: "*" # CRITICAL: Wildcard privilege
                Resource: "*"`,
      diff: `@@ -8,2 +8,6 @@
             Statement:
               - Effect: Allow
-                Action: "*"
-                Resource: "*"
+                Action:
+                  - "s3:GetObject"
+                  - "s3:PutObject"
+                Resource: "arn:aws:s3:::app-storage-bucket/*"`
    },
    kubernetes: {
      title: 'Kubernetes — Privileged Container Escalation',
      file: 'deployments/ingress-controller.yaml',
      framework: 'CIS Kubernetes 5.2.1 • HIPAA § 164.312',
      original: `apiVersion: v1
kind: Pod
metadata:
  name: api-gateway
spec:
  containers:
    - name: proxy
      image: nginx:alpine
      securityContext:
        privileged: true # CRITICAL: Host takeover risk`,
      diff: `@@ -9,1 +9,3 @@
       securityContext:
-        privileged: true
+        privileged: false
+        allowPrivilegeEscalation: false
+        readOnlyRootFilesystem: true`
    }
  }

  const cardDetails = {
    privacy: {
      title: 'AST & Secrets Shield',
      subtitle: 'Zero-Leakage Ingestion & Dependency Analysis',
      body: 'AgentShield AI extracts Abstract Syntax Trees (AST) from Terraform, CloudFormation, Kubernetes, and Helm. Dynamic parameters, locals, and conditionals are evaluated in memory. Simultaneously, integrated Gitleaks and TruffleHog engines intercept embedded API keys, tokens, and private certificates, replacing them with cryptographic hashes before any cloud transmission.'
    },
    defense: {
      title: 'Real-Time Threat Defense (Multi-LLM Consensus)',
      subtitle: 'Ensemble Verification: Claude 3.5 Sonnet + GPT-4o',
      body: 'To eliminate hallucinations and false positives, our Security Analyst Agent queries multiple frontier LLMs concurrently. Findings are evaluated using a calibrated consensus scoring formula (C_ens). Only high-confidence vulnerabilities (C_ens >= 0.85) proceed to automated remediation, while edge cases are seamlessly routed to a human security audit queue.'
    },
    identity: {
      title: 'Sandbox Validation & Self-Healing Patches',
      subtitle: 'Dual-Stage Linter & LocalStack Runtime Verification',
      body: 'Generated code diffs are never blindly trusted. The Validator Agent tests patches against native syntax linters (terraform validate, cfn-lint) and executes dry-run infrastructure deployments inside a local LocalStack sandbox. If compiler or runtime errors occur, logs are automatically fed back to the Remediation Agent for up to 3 self-healing iterations.'
    }
  }

  const marqueeItems = [
    'HashiCorp Terraform',
    'AWS CloudFormation',
    'Kubernetes Manifests',
    'Helm Charts',
    'AWS Cloud',
    'Microsoft Azure',
    'Google Cloud Platform',
    'LocalStack Sandbox',
    'Qdrant Vector DB',
    'Anthropic Claude 3.5 Sonnet',
    'OpenAI GPT-4o',
    'Gitleaks Engine',
    'TruffleHog Scanner',
    'SOC 2 Type II',
    'NIST SP 800-53',
    'PCI-DSS v4.0',
    'HIPAA Security Rule'
  ]

  return (
    <div className="sentinel-landing">
      {/* Background ambient lighting and cyber grid */}
      <div className="bg-glow-gold"></div>
      <div className="bg-glow-cyan"></div>
      <div className="bg-cyber-grid"></div>

      {/* Navigation Bar */}
      <nav className="sentinel-nav">
        <div className="nav-brand">
          <div className="brand-shield-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#e5b869" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M12 6L7 9V12C7 15.5 9.5 18.5 12 19.5C14.5 18.5 17 15.5 17 12V9L12 6Z" fill="url(#goldGrad)" opacity="0.3"/>
              <circle cx="12" cy="12.5" r="2" fill="#00e5ff"/>
              <defs>
                <linearGradient id="goldGrad" x1="7" y1="6" x2="17" y2="19.5" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#fae3b4"/>
                  <stop offset="1" stopColor="#b3822a"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span className="brand-title">AgentShield<span className="brand-accent">AI</span></span>
        </div>

        <div className="nav-links">
          <a href="#home" className="nav-link active">Home</a>
          <a href="#pipeline" className="nav-link">Agents</a>
          <a href="#services" className="nav-link">Services</a>
          <a href="#diff-studio" className="nav-link">Patch Studio</a>
          <a href="#bento" className="nav-link">Platform</a>
        </div>

        <div className="nav-actions">
          <Link to="/login" className="nav-link-signin">Sign In</Link>
          <Link to="/signup" className="nav-btn-gold">Get Started</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="sentinel-hero">
        <div className="hero-content">
          {/* 21st.dev Style Floating Announcement Pill */}
          <div className="announcement-pill">
            <span className="pill-dot"></span>
            <span className="pill-badge">v2.4 Live</span>
            <span className="pill-text">Autonomous Multi-Agent IaC Defense • LocalStack Sandbox Enabled</span>
            <span className="pill-arrow">→</span>
          </div>

          <h1 className="hero-headline">
            <span className="line-light">Secure Your</span>
            <span className="line-gold">Cloud Infrastructure</span>
            <span className="line-light">Autonomously</span>
          </h1>

          <p className="hero-subtext">
            Advanced multi-agent AI framework delivering context-aware vulnerability detection,
            automated code patching, and sandbox runtime verification across multi-cloud Infrastructure-as-Code.
          </p>

          <div className="hero-cta-group">
            <a href="#services" className="btn-shimmer-gold">
              <span className="btn-shine"></span>
              Discover More
            </a>
            <Link to="/console" className="btn-dark-outline">Launch Console →</Link>
          </div>

          {/* Quick Metrics Ticker */}
          <div className="hero-metrics-ticker">
            <div className="ticker-item">
              <span className="ticker-val text-gold-gradient">8</span>
              <span className="ticker-lbl">Autonomous Agents</span>
            </div>
            <div className="ticker-sep"></div>
            <div className="ticker-item">
              <span className="ticker-val text-cyan">100%</span>
              <span className="ticker-lbl">Sandbox Validated</span>
            </div>
            <div className="ticker-sep"></div>
            <div className="ticker-item">
              <span className="ticker-val text-gold-gradient">0</span>
              <span className="ticker-lbl">Plaintext Secrets Sent</span>
            </div>
          </div>
        </div>

        {/* 3D Glowing Shield Graphic */}
        <div className="hero-shield-wrapper">
          <div className="shield-aura-gold"></div>
          <div className="shield-aura-cyan"></div>

          <div className="shield-emblem-3d">
            <svg className="shield-svg" viewBox="0 0 320 380" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <radialGradient id="outerBevel" cx="50%" cy="30%" r="70%">
                  <stop offset="0%" stopColor="#fae3b4"/>
                  <stop offset="35%" stopColor="#e5b869"/>
                  <stop offset="70%" stopColor="#8d6419"/>
                  <stop offset="100%" stopColor="#3d2a08"/>
                </radialGradient>
                <linearGradient id="innerBodyGrad" x1="0" y1="0" x2="320" y2="380" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#0a121e"/>
                  <stop offset="40%" stopColor="#060a12"/>
                  <stop offset="100%" stopColor="#04060a"/>
                </linearGradient>
                <filter id="cyanGlow" x="-30%" y="-30%" width="160%" height="160%">
                  <feGaussianBlur stdDeviation="8" result="blur"/>
                  <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
                <filter id="goldShine" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="4" result="blur"/>
                  <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
              </defs>

              {/* Outer Golden Rim */}
              <path d="M160 16L34 68V172C34 264 88 338 160 366C232 338 286 264 286 172V68L160 16Z"
                stroke="url(#outerBevel)" strokeWidth="9" strokeLinejoin="round" filter="url(#goldShine)"/>

              {/* Inner Obsidian Shield Plate */}
              <path d="M160 26L44 74V172C44 256 94 326 160 352C226 326 276 256 276 172V74L160 26Z"
                fill="url(#innerBodyGrad)"/>

              {/* Ambient Cyber Grid Overlay within Shield */}
              <path d="M90 100H230M80 150H240M80 200H240M100 250H220M160 60V320"
                stroke="#00e5ff" strokeWidth="0.8" opacity="0.12" strokeDasharray="4 4"/>

              {/* Glowing Electric Cyan Shield Outline */}
              <path d="M160 68L86 102V176C86 230 118 282 160 300C202 282 234 230 234 176V102L160 68Z"
                stroke="#00e5ff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" filter="url(#cyanGlow)" opacity="0.95"/>

              {/* Inner Cyber Lock / Agent Core Emblem */}
              <circle cx="160" cy="180" r="32" stroke="#00e5ff" strokeWidth="2.5" opacity="0.85" filter="url(#cyanGlow)"/>
              <circle cx="160" cy="180" r="14" fill="#00e5ff" opacity="0.3"/>
              <path d="M160 158V172M160 188V202M138 180H152M168 180H182" stroke="#fae3b4" strokeWidth="2.5" strokeLinecap="round"/>
              <circle cx="160" cy="180" r="4" fill="#fae3b4"/>

              {/* Dynamic Radar Sweeper Line */}
              <path d="M160 180L182 162" stroke="#00e5ff" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        </div>
      </section>

      {/* Infinite Scrolling Tech & Standards Marquee (OriginKit Style) */}
      <section className="marquee-section">
        <div className="marquee-label">SUPPORTED CLOUDS, ENGINES & COMPLIANCE FRAMEWORKS</div>
        <div className="marquee-track">
          <div className="marquee-content">
            {marqueeItems.concat(marqueeItems).map((item, idx) => (
              <div key={idx} className="marquee-pill">
                <span className="marquee-dot"></span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured 3-Card Section with Border-Beam Effect */}
      <section id="services" className="sentinel-cards-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">CORE ARCHITECTURE</span>
          <h2 className="section-title">Engineered for Uncompromising Defense</h2>
        </div>

        <div className="cards-grid">
          {/* Card 1: AST & Secrets Shield */}
          <div className="sentinel-card">
            <div className="card-border-beam"></div>
            <div className="card-shield-badge gold-badge">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#fae3b4" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                <rect x="9" y="11" width="6" height="5" rx="1" stroke="#fae3b4" strokeWidth="1.5"/>
                <path d="M10 11V9C10 7.9 10.9 7 12 7C13.1 7 14 7.9 14 9V11" stroke="#fae3b4" strokeWidth="1.5"/>
              </svg>
            </div>
            <h3 className="card-title">Protect Your Code</h3>
            <p className="card-desc">
              Multi-cloud AST parsing for Terraform, CloudFormation, K8s & Helm with zero-leakage secret redaction engines.
            </p>
            <button className="btn-card-outline" onClick={() => setActiveModal('privacy')}>
              LEARN MORE
            </button>
          </div>

          {/* Card 2: Multi-LLM Threat Defense (Elevated Centerpiece) */}
          <div className="sentinel-card featured-card">
            <div className="card-top-beam"></div>
            <div className="card-border-beam cyan-beam"></div>
            <div className="card-shield-badge cyan-badge">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#00e5ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M12 8V12M12 16H12.01" stroke="#00e5ff" strokeWidth="2.2" strokeLinecap="round"/>
                <circle cx="12" cy="12" r="7" stroke="#00e5ff" strokeWidth="1" strokeDasharray="2 2" opacity="0.6"/>
              </svg>
            </div>
            <h3 className="card-title highlight-title">Real-Time Threat Defense</h3>
            <p className="card-desc">
              Claude 3.5 Sonnet & GPT-4o ensemble voting evaluates misconfigurations with calibrated confidence scoring.
            </p>
            <button className="btn-card-outline cyan-glow-btn" onClick={() => setActiveModal('defense')}>
              LEARN MORE
            </button>
          </div>

          {/* Card 3: Sandbox Validation */}
          <div className="sentinel-card">
            <div className="card-border-beam"></div>
            <div className="card-shield-badge gold-badge">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#fae3b4" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M9 12L11 14L15 10" stroke="#fae3b4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <h3 className="card-title">Sandbox Validation</h3>
            <p className="card-desc">
              Dual-stage validation harness runs static linters and LocalStack runtime deployments for self-healing patches.
            </p>
            <button className="btn-card-outline" onClick={() => setActiveModal('identity')}>
              LEARN MORE
            </button>
          </div>
        </div>
      </section>

      {/* NEW: Interactive 8-Agent Live Pipeline Beam (21st.dev Style) */}
      <section id="pipeline" className="pipeline-interactive-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">LANGGRAPH ORCHESTRATION</span>
          <h2 className="section-title">The 8 Specialized Autonomous Agents</h2>
          <p className="section-desc">Click any agent node to inspect its live state machine role, inputs, and outputs.</p>
        </div>

        {/* Horizontal Node Track with Animated Beam */}
        <div className="pipeline-nodes-container">
          <div className="pipeline-beam-track">
            <div className="pipeline-animated-beam"></div>
          </div>

          <div className="nodes-strip">
            {agentsList.map((agent, index) => (
              <button
                key={agent.id}
                className={`agent-node-btn ${selectedAgent === index ? 'active' : ''}`}
                onClick={() => setSelectedAgent(index)}
              >
                <div className="node-icon-circle">
                  <span className="node-num">{index + 1}</span>
                </div>
                <span className="node-label">{agent.name}</span>
                <span className="node-badge">{agent.badge}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Selected Agent Inspector Card */}
        <div className="agent-inspector-card">
          <div className="inspector-header">
            <div className="inspector-titles">
              <span className="inspector-pill">NODE 0{selectedAgent + 1} // {agentsList[selectedAgent].role}</span>
              <h3 className="inspector-agent-name">{agentsList[selectedAgent].name}</h3>
            </div>
            <div className="inspector-metrics">
              <div className="metric-box">
                <span className="m-label">ENGINE</span>
                <span className="m-val">{agentsList[selectedAgent].engine}</span>
              </div>
              <div className="metric-box">
                <span className="m-label">AVG LATENCY</span>
                <span className="m-val text-cyan">{agentsList[selectedAgent].latency}</span>
              </div>
            </div>
          </div>

          <p className="inspector-desc">{agentsList[selectedAgent].desc}</p>

          <div className="inspector-io-grid">
            <div className="io-card io-input">
              <span className="io-tag">INPUT CONTRACT</span>
              <code>{agentsList[selectedAgent].input}</code>
            </div>
            <div className="io-card io-output">
              <span className="io-tag">OUTPUT ARTIFACT</span>
              <code>{agentsList[selectedAgent].output}</code>
            </div>
          </div>
        </div>
      </section>

      {/* NEW: Interactive Code Remediation Diff Studio (OriginKit Style) */}
      <section id="diff-studio" className="diff-studio-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">ACTIONABLE REMEDIATION</span>
          <h2 className="section-title">Self-Healing Code Patches</h2>
          <p className="section-desc">Surgical unified git diffs generated by AI, validated in LocalStack, ready to merge.</p>
        </div>

        <div className="diff-studio-card">
          {/* Top Bar with Template Selector and View Toggle */}
          <div className="studio-topbar">
            <div className="studio-tabs">
              <button
                className={`studio-tab ${activeDiffTab === 'terraform' ? 'active' : ''}`}
                onClick={() => setActiveDiffTab('terraform')}
              >
                Terraform (AWS S3)
              </button>
              <button
                className={`studio-tab ${activeDiffTab === 'cloudformation' ? 'active' : ''}`}
                onClick={() => setActiveDiffTab('cloudformation')}
              >
                CloudFormation (IAM)
              </button>
              <button
                className={`studio-tab ${activeDiffTab === 'kubernetes' ? 'active' : ''}`}
                onClick={() => setActiveDiffTab('kubernetes')}
              >
                Kubernetes (Pod Security)
              </button>
            </div>

            <div className="studio-controls">
              <div className="mode-pill-toggle">
                <button
                  className={`mode-btn ${diffViewMode === 'diff' ? 'active' : ''}`}
                  onClick={() => setDiffViewMode('diff')}
                >
                  Validated Patch Diff
                </button>
                <button
                  className={`mode-btn ${diffViewMode === 'original' ? 'active' : ''}`}
                  onClick={() => setDiffViewMode('original')}
                >
                  Vulnerable Original
                </button>
              </div>
            </div>
          </div>

          {/* Subheader info bar */}
          <div className="studio-subbar">
            <div className="file-pill">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              <span>{diffExamples[activeDiffTab].file}</span>
            </div>
            <div className="compliance-pill">
              <span>{diffExamples[activeDiffTab].framework}</span>
            </div>
            <div className="sandbox-badge">
              <span className="sandbox-pulse"></span>
              <span>LocalStack Dry-Run: PASSED</span>
            </div>
          </div>

          {/* Code Body */}
          <div className="studio-code-body">
            <pre>
              {diffViewMode === 'diff'
                ? diffExamples[activeDiffTab].diff.split('\n').map((line, i) => {
                    const isAdd = line.startsWith('+')
                    const isRem = line.startsWith('-')
                    const isHeader = line.startsWith('@@')
                    return (
                      <div
                        key={i}
                        className={`code-line ${isAdd ? 'line-add' : ''} ${isRem ? 'line-rem' : ''} ${isHeader ? 'line-hdr' : ''}`}
                      >
                        <span className="line-no">{i + 1}</span>
                        <span className="line-text">{line}</span>
                      </div>
                    )
                  })
                : diffExamples[activeDiffTab].original.split('\n').map((line, i) => (
                    <div key={i} className="code-line">
                      <span className="line-no">{i + 1}</span>
                      <span className="line-text">{line}</span>
                    </div>
                  ))}
            </pre>
          </div>
        </div>
      </section>

      {/* NEW: Bento Grid Platform Showcase (OriginKit / 21st.dev Style) */}
      <section id="bento" className="bento-grid-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">ENTERPRISE CAPABILITIES</span>
          <h2 className="section-title">Built for Modern DevSecOps Teams</h2>
        </div>

        <div className="bento-grid">
          {/* Bento 1 (Span 2): Multi-Cloud AST */}
          <div className="bento-card bento-span-2">
            <div className="bento-glow-gold"></div>
            <div className="bento-content">
              <span className="bento-tag">SHIFT-LEFT INGESTION</span>
              <h3 className="bento-title">Unified AST Across 4 IaC Languages</h3>
              <p className="bento-p">
                Whether your team writes Terraform HCL, AWS CloudFormation, Kubernetes Manifests, or Helm charts,
                AgentShield resolves dynamic parameters and conditionals in memory.
              </p>
              <div className="bento-cloud-logos">
                <span className="cloud-chip">AWS</span>
                <span className="cloud-chip">Azure</span>
                <span className="cloud-chip">GCP</span>
                <span className="cloud-chip">Kubernetes</span>
              </div>
            </div>
          </div>

          {/* Bento 2: Zero Secret Leakage */}
          <div className="bento-card">
            <div className="bento-glow-cyan"></div>
            <div className="bento-content">
              <span className="bento-tag text-cyan">DATA PRIVACY GUARANTEE</span>
              <h3 className="bento-title">Zero Secret Leakage</h3>
              <p className="bento-p">
                Gitleaks and TruffleHog engines intercept credentials locally, replacing them with cryptographic SHA-256 hashes before prompt creation.
              </p>
              <div className="secret-redaction-preview">
                <span className="redacted-tag">[REDACTED_AWS_KEY]</span>
              </div>
            </div>
          </div>

          {/* Bento 3: Multi-LLM Consensus */}
          <div className="bento-card">
            <div className="bento-glow-cyan"></div>
            <div className="bento-content">
              <span className="bento-tag text-gold">HALLUCINATION SUPPRESSION</span>
              <h3 className="bento-title">Multi-LLM Consensus</h3>
              <p className="bento-p">
                Dual inference across Claude 3.5 and GPT-4o with calibrated consensus scoring drops false positive rates from 15% to under 5%.
              </p>
              <div className="consensus-meter">
                <div className="meter-fill" style={{ width: '94%' }}></div>
                <span className="meter-label">94% Inter-Model Agreement</span>
              </div>
            </div>
          </div>

          {/* Bento 4 (Span 2): LocalStack Sandbox Validation */}
          <div className="bento-card bento-span-2">
            <div className="bento-glow-gold"></div>
            <div className="bento-content">
              <span className="bento-tag">PROVEN RELIABILITY</span>
              <h3 className="bento-title">LocalStack Runtime Sandbox Verification</h3>
              <p className="bento-p">
                Patches undergo dry-run deployments in an offline, isolated LocalStack mock container.
                If syntax or cloud API errors occur, the self-healing loop automatically iterates up to 3 times.
              </p>
              <div className="terminal-mini">
                <span className="term-line text-cyan">$ terraform validate && localstack deploy --dry-run</span>
                <span className="term-line text-green">✓ Syntax valid: 0 errors</span>
                <span className="term-line text-green">✓ S3 bucket encryption provisioned in LocalStack [HTTP 200 OK]</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom Showcase Section: Comprehensive Protection */}
      <section id="about" className="sentinel-showcase-section">
        <h2 className="showcase-headline">
          Comprehensive Protection <span className="text-gold-gradient">Against Cyberthreats</span>
        </h2>

        <div className="showcase-split">
          {/* Left Column: Metrics and Checkpoints */}
          <div className="showcase-left">
            {/* Stat Box */}
            <div className="stat-badge-row">
              <div className="shield-stat-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#00e5ff" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M12 7V17M7 12H17" stroke="#00e5ff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <div className="stat-info">
                <div className="stat-number">8+</div>
                <div className="stat-sub">Autonomous Agents</div>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-label-box">
                <span className="stat-lead">Maximum Security</span>
                <span className="stat-tail">for All Cloud Resources</span>
              </div>
            </div>

            {/* Feature List with Cyan Shield Icons */}
            <div className="feature-bullets">
              <div className="bullet-item">
                <div className="bullet-shield-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#00e5ff" strokeWidth="1.8"/>
                    <circle cx="12" cy="12" r="2.5" fill="#00e5ff"/>
                  </svg>
                </div>
                <div className="bullet-text">
                  Shift-Left Ingestion: Full coverage across IDE extension, pre-commit hooks, and CI/CD pipelines
                </div>
              </div>

              <div className="bullet-item">
                <div className="bullet-shield-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#00e5ff" strokeWidth="1.8"/>
                    <path d="M9 12L11 14L15 10" stroke="#00e5ff" strokeWidth="1.8" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="bullet-text">
                  Multi-Cloud Governance: AWS, Azure, and GCP across Terraform, CloudFormation, K8s, and Helm
                </div>
              </div>

              <div className="bullet-item">
                <div className="bullet-shield-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#00e5ff" strokeWidth="1.8"/>
                    <rect x="9" y="10" width="6" height="5" rx="1" stroke="#00e5ff" strokeWidth="1.5"/>
                  </svg>
                </div>
                <div className="bullet-text">
                  Protect your business data and transactions with enterprise-level compliance (SOC 2, HIPAA, PCI-DSS, NIST)
                </div>
              </div>

              <div className="bullet-item">
                <div className="bullet-shield-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#00e5ff" strokeWidth="1.8"/>
                    <path d="M12 7V13L15 15" stroke="#00e5ff" strokeWidth="1.8" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="bullet-text">
                  Access secure automated self-healing diff patches verified against LocalStack runtime sandboxes
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: High-Tech Laptop & Mobile Showcase */}
          <div className="showcase-right">
            <div className="devices-stage">
              {/* Laptop Frame */}
              <div className="laptop-device">
                <div className="laptop-screen">
                  {/* Laptop Screen Header */}
                  <div className="laptop-topbar">
                    <div className="screen-dots">
                      <span></span><span></span><span></span>
                    </div>
                    <div className="screen-title">AgentShield AI Security Console — LIVE</div>
                    <div className="screen-status-pill">
                      <span className="status-dot-pulse"></span> SYSTEM PROTECTED
                    </div>
                  </div>

                  {/* Laptop Screen Body */}
                  <div className="laptop-dashboard">
                    {/* Top Gauge Row */}
                    <div className="dash-row">
                      <div className="dash-gauge-card">
                        <div className="gauge-circle gold-gauge">
                          <span className="gauge-val">98%</span>
                          <span className="gauge-lbl">COMPLIANCE</span>
                        </div>
                      </div>
                      <div className="dash-stat-card">
                        <div className="dash-stat-num cyan-text">0</div>
                        <div className="dash-stat-label">CRITICAL VULNS</div>
                      </div>
                      <div className="dash-stat-card">
                        <div className="dash-stat-num gold-text">100%</div>
                        <div className="dash-stat-label">PATCH PASS RATE</div>
                      </div>
                    </div>

                    {/* Agent Status Indicators */}
                    <div className="agent-chips">
                      <span className="chip active">Manager</span>
                      <span className="chip active">AST Parser</span>
                      <span className="chip active">Secrets</span>
                      <span className="chip active">RAG</span>
                      <span className="chip active">Analyst</span>
                      <span className="chip active">Remediator</span>
                      <span className="chip active">Validator</span>
                      <span className="chip active">Reporter</span>
                    </div>

                    {/* Code Diff Preview */}
                    <div className="mini-diff-box">
                      <div className="diff-line diff-rem">- resource "aws_s3_bucket" "data" &#123; acl = "public-read" &#125;</div>
                      <div className="diff-line diff-add">+ resource "aws_s3_bucket" "data" &#123; acl = "private" &#125;</div>
                      <div className="diff-line diff-add">+ server_side_encryption_configuration &#123; sse_algorithm = "AES256" &#125;</div>
                    </div>
                  </div>
                </div>
                <div className="laptop-base">
                  <div className="laptop-notch"></div>
                </div>
                <div className="laptop-reflection"></div>
              </div>

              {/* Smartphone Frame */}
              <div className="phone-device">
                <div className="phone-speaker"></div>
                <div className="phone-screen">
                  <div className="phone-header">
                    <span className="phone-time">20:14</span>
                    <span className="phone-signal">5G 100%</span>
                  </div>
                  <div className="phone-shield-badge">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L4 6V11C4 16.55 7.84 21.74 12 23C16.16 21.74 20 16.55 20 11V6L12 2Z" stroke="#fae3b4" strokeWidth="2"/>
                      <rect x="9" y="11" width="6" height="5" rx="1" stroke="#fae3b4" strokeWidth="1.5"/>
                      <path d="M10 11V9C10 7.9 10.9 7 12 7C13.1 7 14 7.9 14 9V11" stroke="#fae3b4" strokeWidth="1.5"/>
                    </svg>
                  </div>
                  <div className="phone-alert-title">Cloud Secured</div>
                  <div className="phone-alert-sub">0 Leaks Detected</div>
                  <div className="phone-btn">Verified</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance Frameworks Section */}
      <section id="compliance" className="sentinel-compliance-section">
        <h3 className="compliance-heading">Automated Regulatory Mapping</h3>
        <div className="compliance-badges-grid">
          <div className="comp-card">
            <span className="comp-tag">SOC 2 TYPE II</span>
            <span className="comp-desc">CC6.1, CC6.6, CC6.7 Cloud Baseline</span>
          </div>
          <div className="comp-card">
            <span className="comp-tag">NIST SP 800-53</span>
            <span className="comp-desc">AC-3, SC-7, SC-8 Access & Cryptography</span>
          </div>
          <div className="comp-card">
            <span className="comp-tag">PCI-DSS v4.0</span>
            <span className="comp-desc">Req 1.2, 2.2, 3.4 Cardholder Data Defense</span>
          </div>
          <div className="comp-card">
            <span className="comp-tag">HIPAA SECURITY</span>
            <span className="comp-desc">45 CFR § 164.312 Technical Safeguards</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="sentinel-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="brand-title">AgentShield<span className="brand-accent">AI</span></span>
            <p className="footer-tagline">Autonomous Multi-Agent Framework for Multi-Cloud IaC Security</p>
          </div>
          <div className="footer-actions">
            <Link to="/console" className="btn-shimmer-gold">Launch Security Console →</Link>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2026 AgentShield AI — Team 13 (College Capstone Project). All rights reserved.</span>
        </div>
      </footer>

      {/* Interactive Modal for "LEARN MORE" */}
      {activeModal && (
        <div className="modal-overlay" onClick={() => setActiveModal(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setActiveModal(null)}>×</button>
            <h3 className="modal-title">{cardDetails[activeModal].title}</h3>
            <h4 className="modal-subtitle">{cardDetails[activeModal].subtitle}</h4>
            <p className="modal-body">{cardDetails[activeModal].body}</p>
            <div className="modal-footer">
              <Link to="/console" className="btn-shimmer-gold" onClick={() => setActiveModal(null)}>
                Try in Console →
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
