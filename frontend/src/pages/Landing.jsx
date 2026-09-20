import { useState } from 'react'
import { Link } from 'react-router-dom'
import '../landing.css'

export default function Landing() {
  const [activeModal, setActiveModal] = useState(null)
  const [selectedAgent, setSelectedAgent] = useState(0)
  const [activeDiffTab, setActiveDiffTab] = useState('terraform')
  const [diffViewMode, setDiffViewMode] = useState('diff') // 'diff' or 'original'

  // Pricing toggle: 'monthly' or 'annual'
  const [billingCycle, setBillingCycle] = useState('annual')

  // FAQ accordion active item
  const [activeFaq, setActiveFaq] = useState(0)

  // Demo Video player state
  const [isPlayingDemo, setIsPlayingDemo] = useState(false)

  // Contact form state
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    inquiryType: 'Demo Request',
    message: ''
  })
  const [contactSubmitted, setContactSubmitted] = useState(false)

  const handleContactSubmit = (e) => {
    e.preventDefault()
    setContactSubmitted(true)
    setTimeout(() => {
      setContactSubmitted(false)
      setContactForm({ name: '', email: '', inquiryType: 'Demo Request', message: '' })
    }, 4000)
  }

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

  const faqs = [
    {
      q: 'How does AgentShield AI differ from traditional static scanners like Checkov or tfsec?',
      a: 'Traditional scanners rely on rigid regular expressions and static rule files that struggle with dynamic variables, count loops, and inter-resource dependencies, leading to high false-positive rates. AgentShield AI builds a full AST dependency graph, enriches it with semantic RAG policies, verifies findings using a multi-LLM ensemble (Claude 3.5 + GPT-4o), and generates executable code patches tested in a local LocalStack sandbox.'
    },
    {
      q: 'Are our sensitive cloud credentials or API keys sent to external LLM providers?',
      a: 'Never. AgentShield AI enforces a strict Zero-Secret Leakage guarantee. The integrated Secrets Scanner Agent runs Gitleaks and TruffleHog engines locally to detect API keys, tokens, and private certificates, replacing them with SHA-256 cryptographic placeholders before any prompt payload is constructed.'
    },
    {
      q: 'How does the LocalStack Sandbox Validation prevent broken infrastructure deployments?',
      a: 'Unlike tools that generate untested textual suggestions, AgentShield AI’s Validator Agent applies the synthesized code patch in an isolated buffer and runs native linters (terraform validate, cfn-lint) followed by a dry-run deployment against a local LocalStack AWS emulator. If errors occur, the compiler stderr is fed back to the Remediation Agent for up to 3 automated self-healing iterations.'
    },
    {
      q: 'What happens when the two LLMs in the ensemble disagree on a vulnerability?',
      a: 'The Consensus Engine calculates a calibrated agreement score (C_ens). If C_ens falls below the 0.85 threshold, the finding is marked as low confidence and routed to the Human Security Review Queue rather than generating a speculative patch, preventing alert fatigue and erroneous code modifications.'
    },
    {
      q: 'Can AgentShield AI integrate into our existing CI/CD pipelines and IDEs?',
      a: 'Yes. AgentShield AI is built for shift-left DevSecOps. It operates as a local CLI (agentshield scan), a VS Code extension with inline diffs, a Git pre-commit hook, and an automated GitHub Actions / GitLab CI runner that posts validated pull-request reviews.'
    },
    {
      q: 'Can we run AgentShield AI in an air-gapped or self-hosted environment?',
      a: 'Yes. The entire multi-agent orchestration is containerized via Docker. You can deploy LocalStack and Qdrant locally, and route the Security Analyst Agent to self-hosted LLM endpoints (such as Ollama or vLLM running Mistral or CodeLlama) without any internet connectivity.'
    }
  ]

  const testimonials = [
    {
      quote: 'AgentShield AI caught 14 overprivileged IAM wildcard policies and unencrypted S3 buckets before our terraform apply ever ran. The automated LocalStack-tested diffs saved our platform team dozens of engineering hours every sprint.',
      author: 'Sarah Jenkins',
      role: 'Principal Cloud Security Architect',
      company: 'FinTech Global',
      avatar: 'SJ'
    },
    {
      quote: 'The multi-LLM consensus voting completely eliminated the hallucination problem we faced with single-LLM security scripts. When AgentShield flags a high-confidence finding, our engineers trust the patch immediately.',
      author: 'David Chen',
      role: 'Head of DevSecOps',
      company: 'CloudNative Systems',
      avatar: 'DC'
    },
    {
      quote: 'Integrating AgentShield into our pre-commit hooks and CI/CD pipelines gave us audit-ready SOC 2 and NIST compliance reports out of the box. It is the gold standard for shift-left IaC governance.',
      author: 'Marcus Vance',
      role: 'Staff Platform Engineer',
      company: 'Enterprise SaaS Corp',
      avatar: 'MV'
    }
  ]

  return (
    <div className="sentinel-landing">
      {/* Background ambient lighting and cyber grid */}
      <div className="bg-glow-gold"></div>
      <div className="bg-glow-cyan"></div>
      <div className="bg-cyber-grid"></div>

      {/* 14. BRAND LOGO & NAVIGATION */}
      <nav className="sentinel-nav">
        <div className="nav-brand">
          <div className="brand-shield-icon">
            <img src="/logo.png" alt="AgentShield AI Logo" className="brand-logo-img" />
          </div>
          <span className="brand-title">AgentShield<span className="brand-accent">AI</span></span>
        </div>

        <div className="nav-links">
          <a href="#home" className="nav-link active">Home</a>
          <a href="#benefits" className="nav-link">Benefits</a>
          <a href="#demo" className="nav-link">Demo</a>
          <a href="#pipeline" className="nav-link">Agents</a>
          <a href="#diff-studio" className="nav-link">Remediation</a>
          <a href="#pricing" className="nav-link">Pricing</a>
          <a href="#faq" className="nav-link">FAQ</a>
          <a href="#contact" className="nav-link">Contact</a>
        </div>

        {/* 1. CALL TO ACTION BUTTON (HEADER) */}
        <div className="nav-actions">
          <Link to="/login" className="nav-link-signin">Sign In</Link>
          <Link to="/signup" className="nav-btn-gold">Get Started</Link>
        </div>
      </nav>

      {/* HERO SECTION */}
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

          {/* 1. PRIMARY CALL TO ACTION BUTTON */}
          <div className="hero-cta-group">
            <Link to="/signup" className="btn-shimmer-gold">
              <span className="btn-shine"></span>
              Start Free Trial →
            </Link>
            <a href="#demo" className="btn-dark-outline">Watch Demo Video ▶</a>
          </div>

          {/* 3. SOCIAL PROOF (HERO METRICS TICKER) */}
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
            <div className="ticker-sep"></div>
            <div className="ticker-item">
              <span className="ticker-val text-cyan">&lt; 5%</span>
              <span className="ticker-lbl">False Positive Rate</span>
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

              <path d="M160 16L34 68V172C34 264 88 338 160 366C232 338 286 264 286 172V68L160 16Z"
                stroke="url(#outerBevel)" strokeWidth="9" strokeLinejoin="round" filter="url(#goldShine)"/>
              <path d="M160 26L44 74V172C44 256 94 326 160 352C226 326 276 256 276 172V74L160 26Z"
                fill="url(#innerBodyGrad)"/>
              <path d="M90 100H230M80 150H240M80 200H240M100 250H220M160 60V320"
                stroke="#00e5ff" strokeWidth="0.8" opacity="0.12" strokeDasharray="4 4"/>
              <path d="M160 68L86 102V176C86 230 118 282 160 300C202 282 234 230 234 176V102L160 68Z"
                stroke="#00e5ff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" filter="url(#cyanGlow)" opacity="0.95"/>
              <circle cx="160" cy="180" r="32" stroke="#00e5ff" strokeWidth="2.5" opacity="0.85" filter="url(#cyanGlow)"/>
              <circle cx="160" cy="180" r="14" fill="#00e5ff" opacity="0.3"/>
              <path d="M160 158V172M160 188V202M138 180H152M168 180H182" stroke="#fae3b4" strokeWidth="2.5" strokeLinecap="round"/>
              <circle cx="160" cy="180" r="4" fill="#fae3b4"/>
              <path d="M160 180L182 162" stroke="#00e5ff" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        </div>
      </section>

      {/* 3. SOCIAL PROOF: INFINITE PARTNER & CLOUD MARQUEE */}
      <section className="marquee-section">
        <div className="marquee-label">POWERING SECURITY FOR CLOUD-NATIVE ENVIRONMENTS</div>
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

      {/* 4. THE PROBLEM WE SOLVE & 13. UNIQUE VALUE */}
      <section id="problem-solution" className="problem-solution-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">THE PARADIGM SHIFT</span>
          <h2 className="section-title">The Problem With Existing IaC Security</h2>
          <p className="section-desc">Why traditional static scanners and single-LLM bots fail modern cloud teams.</p>
        </div>

        <div className="comparison-grid">
          {/* The Broken Traditional Way */}
          <div className="comparison-card broken-way">
            <div className="comp-header">
              <span className="comp-badge bad">TRADITIONAL SCANNERS (CHECKOV / SNYK)</span>
              <h3 className="comp-heading">High Noise, Zero Verification</h3>
            </div>
            <ul className="comp-list">
              <li>
                <span className="icon-cross">✕</span>
                <div>
                  <strong>Rigid Static Regex Rules:</strong> Misses multi-resource IAM escalation paths and complex parameter conditions.
                </div>
              </li>
              <li>
                <span className="icon-cross">✕</span>
                <div>
                  <strong>15%+ False Positive Rates:</strong> Overwhelms platform engineers with alert fatigue, causing teams to disable scanners.
                </div>
              </li>
              <li>
                <span className="icon-cross">✕</span>
                <div>
                  <strong>Abstract Text Suggestions:</strong> Gives vague documentation links rather than executable, syntax-tested code patches.
                </div>
              </li>
              <li>
                <span className="icon-cross">✕</span>
                <div>
                  <strong>Reactive Post-Deployment Scans:</strong> Catches security flaws only after vulnerable infrastructure is already live in production.
                </div>
              </li>
            </ul>
          </div>

          {/* The AgentShield AI Solution */}
          <div className="comparison-card modern-way">
            <div className="comp-header">
              <span className="comp-badge good">THE AGENTSHIELD AI SOLUTION</span>
              <h3 className="comp-heading">Autonomous, Sandbox-Proven Security</h3>
            </div>
            <ul className="comp-list">
              <li>
                <span className="icon-check">✓</span>
                <div>
                  <strong>Hybrid AST & Dependency Parsing:</strong> Evaluates dynamic variables, count loops, and inter-resource links in memory.
                </div>
              </li>
              <li>
                <span className="icon-check">✓</span>
                <div>
                  <strong>Multi-LLM Consensus Voting:</strong> Claude 3.5 Sonnet + GPT-4o ensemble cuts false positives to under 5%.
                </div>
              </li>
              <li>
                <span className="icon-check">✓</span>
                <div>
                  <strong>LocalStack Sandbox Validation:</strong> Every patch is dry-run deployed locally to prove runtime viability before merging.
                </div>
              </li>
              <li>
                <span className="icon-check">✓</span>
                <div>
                  <strong>True Shift-Left DevSecOps:</strong> Seamlessly hooks into IDEs, pre-commit git checks, and PR reviews.
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 2. KEY BENEFITS SECTION */}
      <section id="benefits" className="key-benefits-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">KEY BENEFITS</span>
          <h2 className="section-title">Built for Speed, Accuracy, and Developer Trust</h2>
          <p className="section-desc">Everything engineering teams need to eliminate cloud misconfigurations permanently.</p>
        </div>

        <div className="benefits-grid">
          <div className="benefit-card">
            <div className="benefit-icon-wrap gold-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </div>
            <h3 className="benefit-title">Zero Secret Leakage</h3>
            <p className="benefit-desc">
              Integrated Gitleaks and TruffleHog engines intercept credentials locally, substituting cryptographic hashes before any cloud API payload is created.
            </p>
          </div>

          <div className="benefit-card">
            <div className="benefit-icon-wrap cyan-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <h3 className="benefit-title">Multi-LLM Consensus</h3>
            <p className="benefit-desc">
              Dual-model inference with calibrated consensus scoring eliminates hallucinations and ensures only verified vulnerabilities trigger auto-patching.
            </p>
          </div>

          <div className="benefit-card">
            <div className="benefit-icon-wrap gold-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <h3 className="benefit-title">Self-Healing Patches</h3>
            <p className="benefit-desc">
              Synthesizes unified git diff patches validated against terraform validate and LocalStack sandbox runtimes with up to 3 automatic healing iterations.
            </p>
          </div>

          <div className="benefit-card">
            <div className="benefit-icon-wrap cyan-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="16 18 22 12 16 6"/>
                <polyline points="8 6 2 12 8 18"/>
              </svg>
            </div>
            <h3 className="benefit-title">Shift-Left Integration</h3>
            <p className="benefit-desc">
              Runs as a fast developer CLI, a VS Code extension, a git pre-commit hook, or a CI/CD GitHub Action to stop flaws before code review.
            </p>
          </div>
        </div>
      </section>

      {/* 11. PRODUCT DEMO (INTERACTIVE VIDEO PLAYER SIMULATOR) */}
      <section id="demo" className="demo-video-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">PRODUCT DEMO</span>
          <h2 className="section-title">See AgentShield AI in Action</h2>
          <p className="section-desc">Watch how AgentShield ingests vulnerable Terraform, parses AST, runs multi-LLM consensus, and validates the fix in LocalStack.</p>
        </div>

        <div className="video-player-container">
          <div className="video-topbar">
            <div className="video-dots">
              <span></span><span></span><span></span>
            </div>
            <div className="video-title">AgentShield AI — Automated Scan & Sandbox Remediation Demo</div>
            <div className="video-pill">
              <span className="live-dot"></span> SIMULATED RUNTIME
            </div>
          </div>

          <div className="video-screen">
            {!isPlayingDemo ? (
              <div className="video-poster">
                <div className="poster-shield-icon">
                  <img src="/logo.png" alt="Play Demo" className="poster-logo" />
                </div>
                <h3 className="poster-headline">Autonomous Multi-Agent Scan & LocalStack Validation</h3>
                <p className="poster-sub">Click below to start the interactive walkthrough</p>
                <button
                  type="button"
                  className="btn-play-video"
                  onClick={() => setIsPlayingDemo(true)}
                >
                  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  <span>Play Interactive Demo</span>
                </button>
              </div>
            ) : (
              <div className="video-active-playback">
                <div className="terminal-stream">
                  <div className="stream-line text-cyan">$ agentshield scan ./infrastructure --sandbox=localstack --remediate</div>
                  <div className="stream-line text-gold">[1/8] ManagerAgent: Ingested 3 files (Terraform HCL, CloudFormation YAML)</div>
                  <div className="stream-line text-green">[2/8] SecretsScanner: 0 plaintext credentials found. SHA-256 masks active.</div>
                  <div className="stream-line">[3/8] ASTParser: Extracted 28 resource nodes. Built Dependency Graph.</div>
                  <div className="stream-line text-cyan">[4/8] RAGQuery: Attached top-3 CIS AWS & NIST SP 800-53 controls from Qdrant.</div>
                  <div className="stream-line text-green">      &rarr; Consensus Agreement: C_ens = 0.96 (High Confidence)</div>
                  <div className="stream-line">      &rarr; Detected Vulnerability: aws_s3_bucket.public_records (Unencrypted Public S3)</div>
                  <div className="stream-line text-cyan">[6/8] RemediationAgent: Synthesized Unified Git Diff Patch (+ server_side_encryption).</div>
                  <div className="stream-line text-gold">[7/8] ValidatorAgent: Running terraform validate... PASSED.</div>
                  <div className="stream-line text-green">      &rarr; Deploying to LocalStack Sandbox (http://localhost:4566)... SUCCESS [HTTP 200].</div>
                  <div className="stream-line text-cyan">[8/8] ReportAgent: Mapped to SOC 2 CC6.1 & HIPAA § 164.312. Patch ready to merge!</div>
                </div>

                <div className="video-controls-bar">
                  <button
                    type="button"
                    className="control-btn"
                    onClick={() => setIsPlayingDemo(false)}
                  >
                    ❚❚ Pause
                  </button>
                  <div className="video-scrubber">
                    <div className="scrubber-fill" style={{ width: '68%' }}></div>
                  </div>
                  <span className="video-timer">01:42 / 02:30</span>
                  <Link to="/console" className="btn-video-console">Try in Console →</Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 9. TRUST BADGES & REGULATORY COMPLIANCE */}
      <section id="compliance" className="sentinel-compliance-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">ENTERPRISE ASSURANCE</span>
          <h2 className="section-title">Verified Trust & Compliance Standards</h2>
          <p className="section-desc">Automated control mapping against the world's most demanding cybersecurity frameworks.</p>
        </div>

        <div className="compliance-badges-grid">
          <div className="comp-card">
            <div className="comp-seal gold-seal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            </div>
            <span className="comp-tag">SOC 2 TYPE II</span>
            <span className="comp-desc">CC6.1, CC6.6, CC6.7 Access & Cloud Baseline</span>
          </div>

          <div className="comp-card">
            <div className="comp-seal cyan-seal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <span className="comp-tag">NIST SP 800-53</span>
            <span className="comp-desc">AC-3, SC-7, SC-8 Access & Cryptography</span>
          </div>

          <div className="comp-card">
            <div className="comp-seal gold-seal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="5" width="20" height="14" rx="2"/>
                <line x1="2" y1="10" x2="22" y2="10"/>
              </svg>
            </div>
            <span className="comp-tag">PCI-DSS v4.0</span>
            <span className="comp-desc">Req 1.2, 2.2, 3.4 Cardholder Data Defense</span>
          </div>

          <div className="comp-card">
            <div className="comp-seal cyan-seal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            <span className="comp-tag">HIPAA SECURITY</span>
            <span className="comp-desc">45 CFR § 164.312 Technical Safeguards</span>
          </div>
        </div>
      </section>

      {/* CORE 3-CARD ARCHITECTURE */}
      <section id="services" className="sentinel-cards-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">CORE CAPABILITIES</span>
          <h2 className="section-title">Engineered for Uncompromising Defense</h2>
        </div>

        <div className="cards-grid">
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

      {/* 8-AGENT LIVE PIPELINE BEAM */}
      <section id="pipeline" className="pipeline-interactive-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">LANGGRAPH ORCHESTRATION</span>
          <h2 className="section-title">The 8 Specialized Autonomous Agents</h2>
          <p className="section-desc">Click any agent node to inspect its live state machine role, inputs, and outputs.</p>
        </div>

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

      {/* CODE REMEDIATION DIFF STUDIO */}
      <section id="diff-studio" className="diff-studio-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">ACTIONABLE REMEDIATION</span>
          <h2 className="section-title">Self-Healing Code Patches</h2>
          <p className="section-desc">Surgical unified git diffs generated by AI, validated in LocalStack, ready to merge.</p>
        </div>

        <div className="diff-studio-card">
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

      {/* 5. TESTIMONIALS SECTION */}
      <section id="testimonials" className="testimonials-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">CUSTOMER SUCCESS</span>
          <h2 className="section-title">Trusted by Engineering Leaders</h2>
          <p className="section-desc">See what platform architects and security leads say about AgentShield AI.</p>
        </div>

        <div className="testimonials-grid">
          {testimonials.map((t, idx) => (
            <div key={idx} className="testimonial-card">
              <div className="testimonial-stars">★★★★★</div>
              <p className="t-quote">"{t.quote}"</p>
              <div className="t-profile">
                <div className="t-avatar">{t.avatar}</div>
                <div className="t-info">
                  <span className="t-name">{t.author}</span>
                  <span className="t-role">{t.role}</span>
                  <span className="t-company">{t.company}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 10. CLEAR PRICING SECTION */}
      <section id="pricing" className="pricing-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">TRANSPARENT PRICING</span>
          <h2 className="section-title">Predictable Pricing for Teams of All Sizes</h2>
          <p className="section-desc">Choose the plan that fits your cloud infrastructure and compliance scale.</p>

          <div className="billing-toggle-wrap">
            <button
              type="button"
              className={`billing-btn ${billingCycle === 'monthly' ? 'active' : ''}`}
              onClick={() => setBillingCycle('monthly')}
            >
              Monthly
            </button>
            <button
              type="button"
              className={`billing-btn ${billingCycle === 'annual' ? 'active' : ''}`}
              onClick={() => setBillingCycle('annual')}
            >
              Annual <span className="save-badge">SAVE 20%</span>
            </button>
          </div>
        </div>

        <div className="pricing-grid">
          {/* Tier 1: Community */}
          <div className="pricing-card">
            <div className="pricing-header">
              <span className="plan-name">Community</span>
              <p className="plan-desc">For individual developers and open-source contributors.</p>
              <div className="plan-price">
                <span className="currency">$</span>
                <span className="amount">0</span>
                <span className="period">/forever</span>
              </div>
            </div>
            <ul className="plan-features">
              <li>✓ Local CLI Scanner (`agentshield scan`)</li>
              <li>✓ Terraform & CloudFormation AST Parsing</li>
              <li>✓ Gitleaks Secret Detection</li>
              <li>✓ LocalStack Sandbox Dry-Run (Local)</li>
              <li>✓ Community Support</li>
            </ul>
            <Link to="/signup" className="btn-plan-outline">Get Started Free</Link>
          </div>

          {/* Tier 2: Pro (Featured) */}
          <div className="pricing-card featured-pricing">
            <div className="pricing-badge-popular">MOST POPULAR</div>
            <div className="pricing-header">
              <span className="plan-name text-gold-gradient">Pro DevSecOps</span>
              <p className="plan-desc">For growing engineering teams requiring automated PR remediation.</p>
              <div className="plan-price">
                <span className="currency">$</span>
                <span className="amount">{billingCycle === 'annual' ? '39' : '49'}</span>
                <span className="period">/seat/mo</span>
              </div>
            </div>
            <ul className="plan-features">
              <li>✓ Everything in Community</li>
              <li>✓ Multi-LLM Ensemble Voting (Claude 3.5 + GPT-4o)</li>
              <li>✓ Automated Self-Healing Git Diff Patches</li>
              <li>✓ GitHub Actions & GitLab CI Integrations</li>
              <li>✓ Qdrant Vector DB Policy Enrichment</li>
              <li>✓ SOC 2, HIPAA, PCI-DSS & NIST Reports</li>
              <li>✓ Priority Support & Slack Channel</li>
            </ul>
            <Link to="/signup" className="btn-shimmer-gold w-full">
              <span className="btn-shine"></span>
              Start 14-Day Free Trial
            </Link>
          </div>

          {/* Tier 3: Enterprise */}
          <div className="pricing-card">
            <div className="pricing-header">
              <span className="plan-name">Enterprise</span>
              <p className="plan-desc">For large cloud organizations with strict security & private VPC needs.</p>
              <div className="plan-price">
                <span className="amount">Custom</span>
              </div>
            </div>
            <ul className="plan-features">
              <li>✓ Everything in Pro</li>
              <li>✓ Self-Hosted / Air-Gapped Deployment</li>
              <li>✓ Private VPC & On-Premises LocalStack</li>
              <li>✓ Custom Internal Policy & CVE Ingestion</li>
              <li>✓ Dedicated Security Engineer & 24/7 SLA</li>
              <li>✓ Custom LLM (vLLM / Ollama) Integration</li>
            </ul>
            <a href="#contact" className="btn-plan-outline">Contact Enterprise Sales</a>
          </div>
        </div>
      </section>

      {/* 12. FAQ SECTION (ACCORDION) */}
      <section id="faq" className="faq-section">
        <div className="section-title-wrap">
          <span className="section-eyebrow">FREQUENTLY ASKED QUESTIONS</span>
          <h2 className="section-title">Everything You Need to Know</h2>
          <p className="section-desc">Got questions about our multi-agent architecture, privacy, or LocalStack validation? We've got answers.</p>
        </div>

        <div className="faq-accordion">
          {faqs.map((faq, idx) => (
            <div
              key={idx}
              className={`faq-item ${activeFaq === idx ? 'open' : ''}`}
              onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
            >
              <div className="faq-question-row">
                <h3 className="faq-question">{faq.q}</h3>
                <span className="faq-toggle-icon">{activeFaq === idx ? '−' : '+'}</span>
              </div>
              {activeFaq === idx && (
                <div className="faq-answer">
                  <p>{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 15. CONTACT OPTION SECTION */}
      <section id="contact" className="contact-section">
        <div className="contact-card">
          <div className="contact-info">
            <span className="section-eyebrow">GET IN TOUCH</span>
            <h2 className="contact-title">Speak with our Security Engineering Team</h2>
            <p className="contact-sub">
              Have questions about integrating AgentShield AI into your cloud pipeline or evaluating our research architecture? Send us a message.
            </p>

            <div className="contact-meta-list">
              <div className="meta-row">
                <span className="meta-label">PROJECT:</span>
                <span className="meta-val">AgentShield AI — Team 13 (College Capstone 2026)</span>
              </div>
              <div className="meta-row">
                <span className="meta-label">DOMAIN:</span>
                <span className="meta-val">Cyber Security + Artificial Intelligence</span>
              </div>
              <div className="meta-row">
                <span className="meta-label">STATUS:</span>
                <span className="meta-val text-green">Production Ready & Evaluated</span>
              </div>
            </div>
          </div>

          <form className="contact-form" onSubmit={handleContactSubmit}>
            {contactSubmitted ? (
              <div className="contact-success-msg">
                <span className="msg-icon">✓</span>
                <h4>Message Received!</h4>
                <p>Thank you for reaching out. Our team will get back to you shortly.</p>
              </div>
            ) : (
              <>
                <div className="c-form-group">
                  <label className="c-label">Full Name</label>
                  <input
                    type="text"
                    required
                    value={contactForm.name}
                    onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                    className="c-input"
                  />
                </div>

                <div className="c-form-group">
                  <label className="c-label">Work Email</label>
                  <input
                    type="email"
                    required
                    value={contactForm.email}
                    onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                    className="c-input"
                  />
                </div>

                <div className="c-form-group">
                  <label className="c-label">Inquiry Type</label>
                  <select
                    value={contactForm.inquiryType}
                    onChange={(e) => setContactForm({ ...contactForm, inquiryType: e.target.value })}
                    className="c-input"
                  >
                    <option value="Demo Request">Live Product Demo Request</option>
                    <option value="Enterprise Sales">Enterprise Cloud Pricing</option>
                    <option value="Academic Review">Capstone / Academic Project Review</option>
                    <option value="Technical Question">Technical Architecture Question</option>
                  </select>
                </div>

                <div className="c-form-group">
                  <label className="c-label">Message</label>
                  <textarea
                    rows={4}
                    required
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    className="c-input"
                  ></textarea>
                </div>

                <button type="submit" className="btn-shimmer-gold w-full">
                  <span className="btn-shine"></span>
                  Send Message →
                </button>
              </>
            )}
          </form>
        </div>
      </section>

      {/* 6. 2ND CALL TO ACTION (ENDING) */}
      <section className="final-cta-section">
        <div className="final-cta-card">
          <div className="final-cta-glow"></div>
          <span className="section-eyebrow">START SECURING YOUR CLOUD</span>
          <h2 className="final-cta-title">
            Ship the Infrastructure You Don't Have to Double-Check.
          </h2>
          <p className="final-cta-sub">
            Join forward-thinking cloud teams using 8 autonomous agents to detect, prove,
            and patch IaC misconfigurations before a single resource is provisioned.
          </p>
          <div className="final-cta-buttons">
            <Link to="/signup" className="btn-shimmer-gold">
              <span className="btn-shine"></span>
              Get Started for Free →
            </Link>
            <Link to="/console" className="btn-dark-outline">
              Launch Live Console
            </Link>
          </div>
          <span className="final-cta-reassurance">
            Free forever tier • No credit card required • 2-minute setup with LocalStack
          </span>
        </div>
      </section>

      {/* 14. FOOTER WITH BRAND LOGO */}
      <footer className="sentinel-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-brand-header">
              <img src="/logo.png" alt="AgentShield AI Logo" className="footer-logo-img" />
              <span className="brand-title">AgentShield<span className="brand-accent">AI</span></span>
            </div>
            <p className="footer-tagline">Autonomous Multi-Agent Framework for Multi-Cloud IaC Security</p>
          </div>
          <div className="footer-links-group">
            <div className="footer-col">
              <span className="footer-col-title">Product</span>
              <a href="#pipeline">8 Agents</a>
              <a href="#demo">Live Demo</a>
              <a href="#diff-studio">Patch Studio</a>
              <a href="#pricing">Pricing</a>
            </div>
            <div className="footer-col">
              <span className="footer-col-title">Compliance</span>
              <a href="#compliance">SOC 2 Type II</a>
              <a href="#compliance">NIST SP 800-53</a>
              <a href="#compliance">PCI-DSS v4.0</a>
              <a href="#compliance">HIPAA Security</a>
            </div>
            <div className="footer-col">
              <span className="footer-col-title">Account</span>
              <Link to="/login">Sign In</Link>
              <Link to="/signup">Create Account</Link>
              <Link to="/console">Console</Link>
            </div>
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
