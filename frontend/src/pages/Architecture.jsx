import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'framer-motion'
import {
  Layers,
  ArrowRight,
  Shield,
  Cpu,
  FileCode2,
  Terminal,
  Activity,
  CheckCircle2,
  Lock,
  Network,
  Sparkles,
  ExternalLink,
} from 'lucide-react'

import '../landing.css'
import ScrollProgressBar from '../components/common/ScrollProgressBar'
import BackToTop from '../components/common/BackToTop'
import FeedbackModal from '../components/common/FeedbackModal'
import Navbar from '../components/landing/Navbar'
import FeatureSection from '../components/landing/FeatureSection'
import HowItWorks from '../components/landing/HowItWorks'
import MultiCloudSection from '../components/landing/MultiCloudSection'
import Footer from '../components/landing/Footer'

export default function Architecture() {
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const prefersReduced = useReducedMotion()

  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('agentshield-theme')
      if (saved === 'dark' || saved === 'light') return saved
    } catch {
      // fallback
    }
    return 'dark'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.body.setAttribute('data-theme', theme)
    document.documentElement.className = theme
    document.body.className = theme
    try {
      localStorage.setItem('agentshield-theme', theme)
    } catch {
      // fallback
    }
  }, [theme])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  return (
    <div className={`agentshield-landing-root ${theme}`} data-theme={theme}>
      {/* Visual Reading / Scroll Progress Bar */}
      <ScrollProgressBar />

      {/* Global Navigation Bar */}
      <Navbar theme={theme} setTheme={setTheme} activeRoute="architecture" />

      {/* Main Page Content */}
      <main className="landing-main-flow">
        {/* Dedicated Architecture Page Hero */}
        <section className="dedicated-hero-section" aria-label="Architecture Introduction">
          <div className="section-container">
            <div className="dedicated-hero-content text-center">
              <motion.div
                className="section-eyebrow-wrapper"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <span className="section-eyebrow">
                  <span className="eyebrow-accent-dot" />
                  DEEP DIVE: PLATFORM ARCHITECTURE
                </span>
              </motion.div>

              <motion.h1
                className="dedicated-hero-heading"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                AUTONOMOUS 6-AGENT
                <br />
                <span className="heading-gradient">VERIFICATION ENGINE.</span>
              </motion.h1>

              <motion.p
                className="dedicated-hero-subheading"
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                A rigorous, multi-stage architecture designed for enterprise Infrastructure-as-Code.
                AgentShield-AI combines polyglot AST parsing, dual-model consensus voting,
                exploit-graph modeling, and containerized LocalStack sandboxes into a single
                autonomous verification pipeline.
              </motion.p>

              {/* Architecture Quick-Jump Navigation Tabs */}
              <motion.div
                className="dedicated-jump-nav"
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                <a href="#features" className="jump-nav-pill">
                  <span className="jump-nav-num">01</span>
                  <span>Core Capabilities</span>
                </a>
                <a href="#how-it-works" className="jump-nav-pill">
                  <span className="jump-nav-num">02</span>
                  <span>Autonomous Pipeline</span>
                </a>
                <a href="#integrations" className="jump-nav-pill">
                  <span className="jump-nav-num">03</span>
                  <span>Multi-Cloud Reality</span>
                </a>
              </motion.div>
            </div>
          </div>
        </section>

        {/* 1. Core Architectural Capabilities Bento Grid */}
        <FeatureSection />

        {/* 2. Autonomous Verification Pipeline (6 Connected Stages) */}
        <HowItWorks />

        {/* 3. Multi-Cloud Ecosystem Integration (AWS, Azure, GCP) */}
        <MultiCloudSection />

        {/* 4. Cross-Platform Bridge Section to Security & Console */}
        <section className="architecture-bridge-section" aria-label="Explore Related Capabilities">
          <div className="section-container">
            <div className="bridge-cards-grid">
              <div className="bridge-card bridge-card-security">
                <div className="bridge-card-icon-box">
                  <Shield size={24} />
                </div>
                <span className="bridge-card-tag">TOPOLOGICAL REASONING</span>
                <h3 className="bridge-card-title">Explore Security Intelligence</h3>
                <p className="bridge-card-desc">
                  Learn how AgentShield models full multi-hop exploit paths, calculates downstream
                  blast radius, and prioritizes remediation via topological choke points.
                </p>
                <Link to="/security" className="bridge-card-cta">
                  <span>Explore Security Page</span>
                  <ArrowRight size={15} />
                </Link>
              </div>

              <div className="bridge-card bridge-card-console">
                <div className="bridge-card-icon-box console-icon-box">
                  <Terminal size={24} />
                </div>
                <span className="bridge-card-tag">INTERACTIVE SOC</span>
                <h3 className="bridge-card-title">Launch AgentShield Console</h3>
                <p className="bridge-card-desc">
                  Experience real-time IaC scans, inspect attack path graphs, review consensus telemetry,
                  and approve auto-synthesized unified diff patches.
                </p>
                <Link to="/dashboard" className="bridge-card-cta console-cta">
                  <span>Open Security Dashboard</span>
                  <ArrowRight size={15} />
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Comprehensive Footer */}
      <Footer onOpenFeedback={() => setFeedbackOpen(true)} />

      {/* Accessible Back to Top Floating Button */}
      <BackToTop />

      {/* In-App Security / Feedback Modal */}
      <FeedbackModal isOpen={feedbackOpen} onClose={() => setFeedbackOpen(false)} />
    </div>
  )
}
