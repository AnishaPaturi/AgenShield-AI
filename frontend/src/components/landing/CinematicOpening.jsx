import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Shield, Volume2, VolumeX, Sparkles } from 'lucide-react'

export default function CinematicOpening({ theme }) {
  const videoRef = useRef(null)
  const [videoEnded, setVideoEnded] = useState(false)
  const [impactTriggered, setImpactTriggered] = useState(false)
  const [isMuted, setIsMuted] = useState(true)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => {
      // Trigger rock impact between 2.2s and 2.5s
      if (video.currentTime >= 2.2 && !impactTriggered) {
        setImpactTriggered(true)
      }
    }

    const handleEnded = () => {
      setVideoEnded(true)
      setImpactTriggered(true)
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('ended', handleEnded)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('ended', handleEnded)
    }
  }, [impactTriggered])

  return (
    <section
      className="cinematic-opening-container cinematic-scene-stage"
      id="cinematic-opening"
      aria-label="AgentShield AI Cinematic Opening"
    >
      {/* Background Cinematic Video playing ONCE */}
      <div className="opening-video-wrapper">
        <video
          ref={videoRef}
          className="opening-video"
          src="/videos/Agent%20Shield%20Hero%20Web.mp4"
          autoPlay
          muted={isMuted}
          playsInline
          loop={false}
          preload="auto"
        />

        {/* Cinematic Vignette & Atmospheric Gradients */}
        <div className="opening-vignette" />
        <div className={`opening-ambient-glow ${impactTriggered ? 'glow-impact' : ''}`} />

        {/* Dynamic Impact Shockwave radiating outward */}
        <AnimatePresence>
          {impactTriggered && (
            <motion.div
              className="opening-impact-shockwave"
              initial={{ scale: 0.15, opacity: 1, borderWidth: '3px' }}
              animate={{ scale: 3.6, opacity: 0, borderWidth: '1px' }}
              transition={{ duration: 1.8, ease: [0.16, 1, 0.3, 1] }}
            />
          )}
        </AnimatePresence>
      </div>

      {/* Floating Controls: Audio Toggle */}
      <div className="opening-top-controls">
        <button
          type="button"
          onClick={() => {
            if (videoRef.current) {
              videoRef.current.muted = !isMuted
              setIsMuted(!isMuted)
            }
          }}
          className="opening-control-pill"
          aria-label={isMuted ? 'Unmute video audio' : 'Mute video audio'}
        >
          {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
          <span>{isMuted ? 'SOUND OFF' : 'SOUND ON'}</span>
        </button>
      </div>

      {/* Center Cinematic Overlay & Rock Impact Split Title Reveal */}
      <div className="opening-content-layer">
        <AnimatePresence>
          {(impactTriggered || videoEnded) && (
            <motion.div
              className="opening-split-stage"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              {/* Subtle Floating/Breathing Wrapper around centered composition */}
              <motion.div
                className="opening-settled-composition"
                animate={{ y: [0, -6, 0] }}
                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
              >
                {/* Brand Eyebrow Badge (Settled at center top) */}
                <motion.div
                  className="opening-badge-wrapper"
                  initial={{ opacity: 0, y: -20, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                >
                  <div className="opening-badge">
                    <span className="opening-badge-beacon" />
                    <Shield size={13} className="opening-shield-icon" />
                    <span>AGENTSHIELD AI</span>
                    <span className="opening-badge-divider">•</span>
                    <span className="opening-badge-sub">AUTONOMOUS IAC DEFENSE</span>
                  </div>
                </motion.div>

                {/* Symmetrical Split Container: Title from LEFT, Description from RIGHT */}
                <div className="opening-split-container">
                  {/* Dominant Title entering from LEFT */}
                  <motion.div
                    className="split-title-left"
                    initial={{ x: -160, opacity: 0, filter: 'blur(8px)' }}
                    animate={{ x: 0, opacity: 1, filter: 'blur(0px)' }}
                    transition={{
                      type: 'spring',
                      damping: 24,
                      stiffness: 90,
                      mass: 1.1,
                      delay: 0.05,
                    }}
                  >
                    <h1 className="cinematic-dominant-headline">
                      <span className="headline-row">SECURITY</span>
                      <span className="headline-row">THAT THINKS</span>
                      <span className="headline-row highlight-row">IN PATHS.</span>
                    </h1>
                  </motion.div>

                  {/* Supporting Description & Pillars entering from RIGHT */}
                  <motion.div
                    className="split-desc-right"
                    initial={{ x: 160, opacity: 0, filter: 'blur(8px)' }}
                    animate={{ x: 0, opacity: 1, filter: 'blur(0px)' }}
                    transition={{
                      type: 'spring',
                      damping: 24,
                      stiffness: 90,
                      mass: 1.1,
                      delay: 0.05,
                    }}
                  >
                    <p className="opening-dominant-tagline">
                      Autonomous Multi-Cloud Security Intelligence for Infrastructure-as-Code.
                    </p>

                    <p className="opening-body-clarifier">
                      Moving beyond brittle static linters to topological exploit path synthesis,
                      multi-LLM logit consensus, and zero-regression containerized validation.
                    </p>

                    <div className="opening-pillars-cluster">
                      <div className="opening-pillar-chip">
                        <span className="chip-indicator" />
                        <span>Polyglot AST Parsing</span>
                      </div>
                      <div className="opening-pillar-chip">
                        <span className="chip-indicator" />
                        <span>Graph Attack Paths</span>
                      </div>
                      <div className="opening-pillar-chip">
                        <span className="chip-indicator" />
                        <span>Multi-LLM Consensus</span>
                      </div>
                      <div className="opening-pillar-chip">
                        <span className="chip-indicator" />
                        <span>Sandbox-Validated PRs</span>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Scroll Cue Prompt (Manual User Scroll Only) */}
        <motion.div
          className="opening-scroll-cue"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.8, duration: 1 }}
        >
          <span className="scroll-cue-text">SCROLL DOWN TO EXPLORE</span>
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ repeat: Infinity, duration: 1.8, ease: 'easeInOut' }}
          >
            <ChevronDown size={22} className="scroll-cue-arrow" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
