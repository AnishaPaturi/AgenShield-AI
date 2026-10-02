import { useState, useEffect, useCallback } from 'react'
import '../landing.css'

import ScrollProgressBar from '../components/common/ScrollProgressBar'
import BackToTop from '../components/common/BackToTop'
import FeedbackModal from '../components/common/FeedbackModal'
import Navbar from '../components/landing/Navbar'
import Hero from '../components/landing/Hero'
import ArchitecturePreview from '../components/landing/ArchitecturePreview'
import SecurityPreview from '../components/landing/SecurityPreview'
import ResearchSection from '../components/landing/ResearchSection'
import MetricsSection from '../components/landing/MetricsSection'
import FAQSection from '../components/landing/FAQSection'
import FinalCTA from '../components/landing/FinalCTA'
import Footer from '../components/landing/Footer'

import { captureUtmParams } from '../utils/utm'

export default function Landing() {
  const [feedbackOpen, setFeedbackOpen] = useState(false)
  const [introStage, setIntroStage] = useState(() => {
    if (typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches) {
      return 'settled'
    }
    return 'opening' // 'opening' | 'impact' | 'settled'
  })

  // Theme state: dark (default) | light
  const [theme, setTheme] = useState(() => {
    try {
      const saved = localStorage.getItem('agentshield-theme')
      if (saved === 'dark' || saved === 'light') return saved
    } catch {
      // fallback
    }
    return 'dark'
  })

  const handleImpact = useCallback(() => {
    setIntroStage('impact')
  }, [])

  const handleSettled = useCallback(() => {
    setIntroStage('settled')
  }, [])

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
    // Capture any incoming marketing/campaign UTM query parameters
    captureUtmParams()
  }, [])

  return (
    <div className={`agentshield-landing-root ${theme}`} data-theme={theme}>
      {/* Visual Reading / Scroll Progress Bar */}
      <ScrollProgressBar />

      {/* Fixed Global Navigation Bar - Enters from Left on Impact */}
      <Navbar
        theme={theme}
        setTheme={setTheme}
        activeRoute="home"
        introStage={introStage}
      />

      {/* Main Page Flow - Natural Vertical Scrolling */}
      <main className="landing-main-flow">
        {/* 1. Hero Section with Background Video and Cinematic Opening */}
        <Hero
          theme={theme}
          onImpact={handleImpact}
          onSettled={handleSettled}
        />

        {/* 2. Platform Architecture Preview & Entry Point */}
        <ArchitecturePreview />

        {/* 3. Contextual Topology Security Preview & Entry Point */}
        <SecurityPreview />

        {/* 4. Research & Engineering Foundations */}
        <ResearchSection />

        {/* 5. Verified Project Metrics & Evaluation */}
        <MetricsSection />

        {/* 6. Architectural Inquiries & FAQ */}
        <FAQSection />

        {/* 7. Final Call to Action */}
        <FinalCTA />
      </main>

      {/* 8. Comprehensive Footer */}
      <Footer onOpenFeedback={() => setFeedbackOpen(true)} />

      {/* Accessible Back to Top Floating Button */}
      <BackToTop />

      {/* In-App Security / Feedback Modal */}
      <FeedbackModal isOpen={feedbackOpen} onClose={() => setFeedbackOpen(false)} />
    </div>
  )
}
