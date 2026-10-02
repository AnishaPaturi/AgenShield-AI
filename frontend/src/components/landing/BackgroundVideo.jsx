import { useRef, useEffect, useState } from 'react'

export default function BackgroundVideo({ theme, scrollProgress = 0 }) {
  const videoRef = useRef(null)
  const [videoLoaded, setVideoLoaded] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)

  useEffect(() => {
    // Check user preference for reduced motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)

    const handler = (e) => setReducedMotion(e.matches)
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

  useEffect(() => {
    if (videoRef.current) {
      // Ensure autoplay succeeds reliably
      videoRef.current.play().catch(() => {
        // Autoplay may require mute (already set on element)
      })
    }
  }, [])

  // Calculate subtle parallax transform based on scroll progress (0 to 1)
  // Clamp progress to hero section
  const clampedProgress = Math.min(Math.max(scrollProgress, 0), 1)
  const translateY = reducedMotion ? 0 : clampedProgress * -40 // Moves gently upward
  const scale = reducedMotion ? 1 : 1 + clampedProgress * 0.06 // Scales gently from 1.0 to 1.06
  const opacity = 1 - clampedProgress * 0.45 // Very gradual fade down to 0.55 so it transitions seamlessly

  return (
    <div
      className="hero-video-wrapper"
      style={{
        transform: `translate3d(0, ${translateY}px, 0) scale(${scale})`,
        opacity: opacity,
      }}
    >
      {/* Background Video Element */}
      <video
        ref={videoRef}
        className={`hero-bg-video ${videoLoaded ? 'loaded' : ''}`}
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        onLoadedData={() => setVideoLoaded(true)}
      >
        <source src="/videos/agentshield-hero.mp4" type="video/mp4" />
        <source src="/videos/agentshield-hero-web.mp4" type="video/mp4" />
      </video>

      {/* Dynamic Gradient & Lighting Treatment Overlay */}
      <div className={`hero-theme-overlay ${theme}`} />

      {/* Subtle Atmospheric Grid & Vignette */}
      <div className="hero-atmospheric-vignette" />
      <div className="hero-subtle-mesh" />
    </div>
  )
}
