import React from 'react'

/**
 * AuthRobot
 * Standing AgentShield Security AI Robot visual component.
 * Completely static display of the AgentShield Security AI Robot asset.
 * All eyes, facial features, and body elements remain visually static.
 */
export default function AuthRobot() {
  return (
    <div className="auth-robot-container" aria-hidden="true">
      <div className="auth-robot-frame">
        {/* Base Stationary Robot Asset - 100% STATIC */}
        <img
          src="/videos/robot.png"
          alt="AgentShield Security AI Robot"
          className="auth-robot-img"
          loading="eager"
          draggable="false"
        />

        {/* Subtle Glass Highlight Sheen */}
        <div className="auth-robot-card-sheen" />
      </div>

      {/* Floating Status Badge */}
      <div className="auth-robot-status-pill">
        <span className="robot-status-dot" />
        <span className="robot-status-label">SHIELD BOT ACTIVE</span>
      </div>
    </div>
  )
}
