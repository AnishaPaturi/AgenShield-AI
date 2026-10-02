import React from 'react'

/**
 * AuthCinematicBackground
 * A dark, cinematic, static-first security atmosphere for AgentShield-AI authentication.
 *
 * Characteristics:
 * - Minimal, technical, sophisticated cybersecurity visual language
 * - Very subtle dark charcoal/midnight gradient
 * - Faint red security glow and subtle indigo atmospheric depth
 * - Faint geometric grid structure with smooth radial fade-out
 * - Subtle topological security lines and points of light
 * - Static-first with gentle, restrained ambient breathing
 * - Completely respects prefers-reduced-motion
 */
export default function AuthCinematicBackground() {
  return (
    <div className="auth-cinematic-bg-wrapper" aria-hidden="true">
      {/* 1. Deep Midnight Base Layer */}
      <div className="auth-bg-base-layer" />

      {/* 2. Soft Blurred Central Radial Atmosphere behind the Card */}
      <div className="auth-bg-glow-center" />
      <div className="auth-bg-glow-crimson" />

      {/* 3. Extremely Faint Geometric Security Grid (Radially Masked) */}
      <div className="auth-bg-grid-layer" />

      {/* 4. Architectural Topological Security Lines & Connected Nodes */}
      <svg
        className="auth-bg-network-svg"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient id="authNetGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--auth-accent, #E11D48)" stopOpacity="0.09" />
            <stop offset="50%" stopColor="#A78BFA" stopOpacity="0.05" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="authNetGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="rgba(56, 189, 248, 0.08)" />
            <stop offset="60%" stopColor="var(--auth-accent, #E11D48)" stopOpacity="0.04" />
            <stop offset="100%" stopColor="transparent" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Faint infrastructural network routes */}
        <path
          d="M -40,240 L 380,360 L 720,320 L 1080,480 L 1480,420"
          stroke="url(#authNetGrad1)"
          strokeWidth="1.2"
          fill="none"
          className="auth-net-path auth-net-path-1"
        />
        <path
          d="M 80,780 L 440,660 L 840,700 L 1280,560"
          stroke="url(#authNetGrad2)"
          strokeWidth="1"
          fill="none"
          className="auth-net-path auth-net-path-2"
        />
        <path
          d="M 240,120 L 500,220 L 920,160 L 1340,300"
          stroke="url(#authNetGrad1)"
          strokeWidth="0.8"
          strokeDasharray="4 6"
          fill="none"
          className="auth-net-path auth-net-path-3"
        />

        {/* Tiny points of light (Security Infrastructure Nodes) */}
        <circle cx="380" cy="360" r="2.5" fill="var(--auth-accent, #E11D48)" opacity="0.45" className="auth-net-node node-pulse-1" />
        <circle cx="720" cy="320" r="2" fill="#38BDF8" opacity="0.35" className="auth-net-node node-pulse-2" />
        <circle cx="1080" cy="480" r="2.5" fill="var(--auth-accent, #E11D48)" opacity="0.45" className="auth-net-node node-pulse-3" />
        <circle cx="440" cy="660" r="2" fill="#38BDF8" opacity="0.3" className="auth-net-node node-pulse-4" />
      </svg>

      {/* 5. Minimal Edge Vignette */}
      <div className="auth-bg-vignette" />
    </div>
  )
}
