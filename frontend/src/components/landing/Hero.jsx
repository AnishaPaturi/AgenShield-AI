import { useState, useRef, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import { ArrowRight, Cpu } from 'lucide-react'

// Track across soft navigation so the intro plays once per session
let sessionIntroCompleted = false

export default function Hero({ theme, onImpact, onSettled }) {
  const prefersReduced = useReducedMotion()
  const videoRef = useRef(null)
  const [scrollProgress, setScrollProgress] = useState(0)

  // Keep callback references stable to prevent re-triggering effects
  const onImpactRef = useRef(onImpact)
  const onSettledRef = useRef(onSettled)
  useEffect(() => {
    onImpactRef.current = onImpact
    onSettledRef.current = onSettled
  })

  // Track whether the intro has finished / settled
  const hasFinishedIntroRef = useRef(sessionIntroCompleted || Boolean(prefersReduced))
  const impactTriggeredRef = useRef(sessionIntroCompleted || Boolean(prefersReduced))

  // Cinematic opening sequence stages:
  // 'blank'         -> Empty dark screen
  // 'a-mark'        -> Standalone "A" logo appears FIRST
  // 'brand-name'    -> Full website name "AgentShield AI" appears AFTER the "A"
  // 'cleared'       -> Screen clears back to empty dark cinematic state (pause)
  // 'video-playing' -> Cinematic video starts and plays once
  // 'impact'        -> Rocks hit translucent screen -> Video stops!
  // 'settled'       -> Permanent settled state (Title left, Matter right)
  const [stage, setStage] = useState(() => {
    if (sessionIntroCompleted || prefersReduced) return 'settled'
    return 'blank'
  })
  const [impactTriggered, setImpactTriggered] = useState(() => sessionIntroCompleted || Boolean(prefersReduced))
  const [showShockwave, setShowShockwave] = useState(false)
  const [videoLoaded, setVideoLoaded] = useState(true)

  // Ensure persistent video plays reliably and seamlessly across renders
  useEffect(() => {
    const video = videoRef.current
    if (video) {
      video.defaultMuted = true
      video.muted = true
      if (sessionIntroCompleted || prefersReduced) {
        video.play().catch(() => {})
      }
    }
  }, [prefersReduced])

  // Track natural scroll parallax
  useEffect(() => {
    const handleScroll = () => {
      const heroHeight = window.innerHeight || 800
      setScrollProgress(window.scrollY / heroHeight)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Trigger Rock Impact -> UI entrance trigger ONLY -> Video CONTINUES playing naturally
  const triggerRockImpact = useCallback(() => {
    if (impactTriggeredRef.current) return
    impactTriggeredRef.current = true
    hasFinishedIntroRef.current = true
    sessionIntroCompleted = true

    // CRITICAL: DO NOT PAUSE THE VIDEO!
    // Video must continue playing naturally behind the hero content.
    if (videoRef.current && videoRef.current.paused) {
      videoRef.current.play().catch(() => {})
    }

    setImpactTriggered(true)
    setShowShockwave(true)
    setStage('impact')
    onImpactRef.current?.()

    setTimeout(() => {
      setShowShockwave(false)
      setStage('settled')
      onSettledRef.current?.()
    }, 1000)
  }, [])

  // Immediate skip function for accessibility or quick exploration
  const skipOpening = useCallback(() => {
    if (impactTriggeredRef.current) return
    impactTriggeredRef.current = true
    hasFinishedIntroRef.current = true
    sessionIntroCompleted = true

    // CRITICAL: DO NOT PAUSE THE VIDEO
    if (videoRef.current && videoRef.current.paused) {
      videoRef.current.play().catch(() => {})
    }

    setStage('settled')
    setImpactTriggered(true)
    setShowShockwave(false)
    onImpactRef.current?.()
    onSettledRef.current?.()
  }, [])

  // Escape key listener for skipping intro
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && stage !== 'settled') {
        skipOpening()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [stage, skipOpening])

  // Choreographed Opening Sequence Timeline - Runs EXACTLY ONCE
  useEffect(() => {
    if (prefersReduced || sessionIntroCompleted || hasFinishedIntroRef.current) {
      if (videoRef.current && videoRef.current.paused) {
        videoRef.current.play().catch(() => {})
      }
      onImpactRef.current?.()
      onSettledRef.current?.()
      return
    }

    // Step 0: Empty dark screen (0 - 350ms)
    // Step 1: Standalone "A" mark appears (350ms)
    const t0 = setTimeout(() => {
      setStage('a-mark')
    }, 350)

    // Step 2: "AgentShield AI" website name appears after the "A" (1500ms)
    const t1 = setTimeout(() => {
      setStage('brand-name')
    }, 1500)

    // Step 3: Screen clears back to empty dark cinematic state (2700ms)
    const t2 = setTimeout(() => {
      setStage('cleared')
    }, 2700)

    // Step 4: Cinematic video starts playing (3200ms)
    const t3 = setTimeout(() => {
      setStage('video-playing')
      if (videoRef.current) {
        try {
          videoRef.current.currentTime = 0
          videoRef.current.play().catch(() => {})
        } catch {
          // ignore
        }
      }
    }, 3200)

    // Step 5: Fallback safety timer for rock impact (3200ms + 2300ms = 5500ms)
    // Triggers if video timeUpdate doesn't catch the 2.2s point
    const t4 = setTimeout(() => {
      if (!impactTriggeredRef.current) {
        triggerRockImpact()
      }
    }, 5500)

    return () => {
      clearTimeout(t0)
      clearTimeout(t1)
      clearTimeout(t2)
      clearTimeout(t3)
      clearTimeout(t4)
    }
  }, [prefersReduced, triggerRockImpact])

  // Exact Rock Impact Sync: Video currentTime >= 2.2s (Rocks hit translucent surface)
  const handleVideoTimeUpdate = () => {
    if (impactTriggeredRef.current) return
    if (stage === 'video-playing' && videoRef.current) {
      if (videoRef.current.currentTime >= 2.2) {
        triggerRockImpact()
      }
    }
  }

  // Handle video ending safely before impact or loop seamlessly
  const handleVideoEnded = () => {
    if (!impactTriggeredRef.current) {
      triggerRockImpact()
    }
    if (videoRef.current) {
      videoRef.current.currentTime = 0
      videoRef.current.play().catch(() => {})
    }
  }

  // Parallax transform calculations based on user scroll
  const clampedProgress = Math.min(Math.max(scrollProgress, 0), 1)
  const translateY = prefersReduced ? 0 : clampedProgress * -40
  const scale = prefersReduced ? 1 : 1 + clampedProgress * 0.06
  const videoOpacity = 1 - clampedProgress * 0.45

  return (
    <section className="hero-section" id="hero" aria-label="Hero Section">
      {/* 1. Cinematic Background Video with Parallax and Layered Lighting */}
      <div
        className="hero-video-wrapper"
        style={{
          transform: `translate3d(0, ${translateY}px, 0) scale(${scale})`,
          opacity: videoOpacity,
        }}
      >
        <video
          ref={videoRef}
          className={`hero-bg-video ${videoLoaded ? 'loaded' : ''}`}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          onLoadedData={() => setVideoLoaded(true)}
          onCanPlay={() => setVideoLoaded(true)}
          onTimeUpdate={handleVideoTimeUpdate}
          onEnded={handleVideoEnded}
        >
          <source src="/videos/agentshield-hero.mp4" type="video/mp4" />
          <source src="/videos/agentshield-hero-web.mp4" type="video/mp4" />
        </video>

        {/* Dynamic Dark Theme Overlay & Atmosphere */}
        <div className={`hero-theme-overlay ${theme}`} />
        <div className="hero-atmospheric-vignette" />
        <div className="hero-subtle-mesh" />
      </div>

      {/* 2. Rock Impact Shockwave & Translucent Glass Transition */}
      <AnimatePresence>
        {showShockwave && (
          <>
            <motion.div
              className="hero-impact-flash"
              initial={{ opacity: 0.8 }}
              animate={{ opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.85, ease: 'easeOut' }}
            />
            <motion.div
              className="hero-impact-shockwave"
              initial={{ scale: 0.2, opacity: 1 }}
              animate={{ scale: 3.6, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
            />
          </>
        )}
      </AnimatePresence>

      {/* 3. Fullscreen Cinematic Opening Overlay (A -> AgentShield AI -> Cleared) */}
      <AnimatePresence>
        {!impactTriggered && stage !== 'video-playing' && stage !== 'impact' && stage !== 'settled' && (
          <motion.div
            className={`hero-intro-overlay ${stage === 'cleared' ? 'cleared' : ''}`}
            initial={{ opacity: 1 }}
            animate={{ opacity: stage === 'cleared' ? 0 : 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            onClick={skipOpening}
            aria-hidden={stage === 'cleared'}
            style={{ pointerEvents: stage === 'cleared' ? 'none' : 'auto' }}
          >
            <div className="intro-center-stage">
              {/* STEP 1: Standalone "A" Logo Appears FIRST */}
              <motion.div
                className="intro-a-mark-container"
                initial={{ opacity: 0, scale: 0.92, filter: 'blur(6px)' }}
                animate={
                  stage === 'a-mark' || stage === 'brand-name'
                    ? { opacity: 1, scale: 1, filter: 'blur(0px)' }
                    : { opacity: 0, scale: 0.94, filter: 'blur(6px)' }
                }
                transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
              >
                <div className="intro-a-glow" />
                <img
                  src="/logo.png"
                  alt="AgentShield A Mark"
                  className="intro-a-logo"
                />
              </motion.div>

              {/* STEP 2: "AgentShield AI" Website Name Appears AFTER the A */}
              <motion.div
                className="intro-brand-name-container"
                initial={{ opacity: 0, y: 14, filter: 'blur(4px)' }}
                animate={
                  stage === 'brand-name'
                    ? { opacity: 1, y: 0, filter: 'blur(0px)' }
                    : { opacity: 0, y: -8, filter: 'blur(4px)' }
                }
                transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
              >
                <div className="intro-brand-text">
                  <span className="intro-name">AgentShield</span>
                  <span className="intro-badge">AI</span>
                </div>
                <div className="intro-tagline">
                  AUTONOMOUS MULTI-CLOUD SECURITY
                </div>
              </motion.div>
            </div>

            {/* Skip Option for immediate interaction */}
            <button
              type="button"
              className="intro-skip-button"
              onClick={(e) => {
                e.stopPropagation()
                skipOpening()
              }}
              aria-label="Skip cinematic introduction"
            >
              <span>Skip Intro</span>
              <span className="skip-pill">ESC</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 4. Main Hero Composition (Revealed on Rock Impact) */}
      <div className="hero-content-container">
        <div className="hero-split-grid">
          {/* LEFT COLUMN: TITLE & CTAs (Enters from LEFT on Impact) */}
          <motion.div
            className="hero-split-left"
            initial={prefersReduced || sessionIntroCompleted ? false : { x: -140, opacity: 0, filter: 'blur(8px)' }}
            animate={
              impactTriggered
                ? { x: 0, opacity: 1, filter: 'blur(0px)' }
                : { x: -140, opacity: 0, filter: 'blur(8px)' }
            }
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            style={{ pointerEvents: impactTriggered ? 'auto' : 'none' }}
          >
            {/* Eyebrow Tag */}
            <div className="hero-eyebrow-wrapper">
              <span className="hero-eyebrow-tag">
                <span className="eyebrow-accent-dot" />
                AUTONOMOUS MULTI-CLOUD SECURITY
              </span>
            </div>

            {/* Monumental Headline */}
            <h1 className="hero-headline">
              <span className="headline-line">SECURITY</span>
              <span className="headline-line headline-accent">THAT THINKS</span>
              <span className="headline-line">IN PATHS.</span>
            </h1>

            {/* Supporting Description Directly Under Title */}
            <p className="hero-description">
              An AI agent that autonomously analyzes Infrastructure-as-Code, identifies vulnerabilities and attack paths, evaluates risk, and assists with validated remediation across multi-cloud environments.
            </p>

            {/* Supporting Metadata / Feature Indicators */}
            <div className="hero-meta-strip">
              <div className="hero-meta-item">
                <span className="hero-meta-dot" />
                <span>Shift-Left IaC Security</span>
              </div>
              <span className="hero-meta-divider">•</span>
              <div className="hero-meta-item">
                <span className="hero-meta-dot" />
                <span>Attack Path Graph Traversal</span>
              </div>
              <span className="hero-meta-divider">•</span>
              <div className="hero-meta-item">
                <span className="hero-meta-dot" />
                <span>Deterministic Patches</span>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="hero-cta-group">
              <a
                href="#architecture-preview"
                className="hero-primary-btn"
                id="hero-cta-btn"
              >
                <span>Explore AgentShield</span>
                <ArrowRight size={16} className="btn-arrow" />
              </a>

              <Link to="/architecture" className="hero-secondary-btn">
                <span>View Architecture</span>
              </Link>
            </div>
          </motion.div>

          {/* RIGHT COLUMN: SECONDARY COMPACT TECHNICAL PANEL (Enters from RIGHT on Impact) */}
          <motion.div
            className="hero-split-right"
            initial={prefersReduced || sessionIntroCompleted ? false : { x: 140, opacity: 0, filter: 'blur(8px)' }}
            animate={
              impactTriggered
                ? { x: 0, opacity: 1, filter: 'blur(0px)' }
                : { x: 140, opacity: 0, filter: 'blur(8px)' }
            }
            transition={{ duration: 0.9, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
            style={{ pointerEvents: impactTriggered ? 'auto' : 'none' }}
          >
            <div className="hero-matter-glass-card">
              <div className="hero-panel-heading-row">
                <span className="hero-panel-label">CAPABILITIES &amp; RUNTIME SPEC</span>
                <span className="hero-panel-sub-tag">NON-LINEAR DAG</span>
              </div>

              {/* 4 Architectural Capability Chips */}
              <div className="hero-capability-chips">
                <div className="capability-chip">
                  <span className="chip-indicator" />
                  <span>Polyglot AST Parsing</span>
                </div>
                <div className="capability-chip">
                  <span className="chip-indicator" />
                  <span>Graph Attack Paths</span>
                </div>
                <div className="capability-chip">
                  <span className="chip-indicator" />
                  <span>Multi-LLM Consensus</span>
                </div>
                <div className="capability-chip">
                  <span className="chip-indicator" />
                  <span>Sandbox-Validated PRs</span>
                </div>
              </div>

              {/* Live System Status Strip */}
              <div className="hero-system-status">
                <div className="status-indicator-badge">
                  <span className="status-beacon">
                    <span className="beacon-ping" />
                    <span className="beacon-core" />
                  </span>
                  <span className="status-label">SECURITY ENGINE ACTIVE</span>
                  <span className="status-divider" />
                  <span className="status-sub">420+ TESTS</span>
                </div>
                <div className="hero-side-pill">
                  <Cpu size={13} className="hero-side-icon" />
                  <span>6-AGENT LANGGRAPH DAG</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* 5. Natural Scroll Prompt */}
      <motion.div
        className="hero-scroll-indicator"
        initial={{ opacity: 0 }}
        animate={{ opacity: impactTriggered ? 0.6 : 0 }}
        transition={{ delay: 0.6, duration: 0.8 }}
        style={{ opacity: Math.max(0, 0.7 - scrollProgress * 2) }}
      >
        <span className="scroll-text">SCROLL TO INSPECT</span>
        <div className="scroll-chevron-line" />
      </motion.div>
    </section>
  )
}
