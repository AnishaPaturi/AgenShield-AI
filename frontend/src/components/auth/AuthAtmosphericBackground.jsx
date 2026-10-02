import React from 'react'

/**
 * AuthAtmosphericBackground
 * Living atmospheric gradient fields for the Authentication portal.
 *
 * Dark mode (Crystal Lavender / Dreamy Aurora):
 * - Base: #060812 (Deep midnight base)
 * - Field 1: Large lavender/violet illumination entering upper-left
 * - Field 2: Soft cyan/blue illumination drifting from lower-right
 * - Field 3: Deep violet atmospheric glow behind & around the card
 * - Field 4: Dreamy pink highlight moving slowly across the side
 * - Field 5: Central luminous crystal aura breathing behind the glass card
 *
 * Light mode (Sakura Light):
 * - Base: #FAF7F4 (Warm ivory base)
 * - Large soft blush pink, warm dusty rose, delicate sage green, and cream glass illumination
 *
 * Visible, organic, slow, and elegant movement.
 * Completely respects prefers-reduced-motion.
 */
export default function AuthAtmosphericBackground() {
  return (
    <div className="auth-atmospheric-container" aria-hidden="true">
      {/* Primary Atmospheric Light Fields */}
      <div className="auth-atmospheric-field auth-field-1" />
      <div className="auth-atmospheric-field auth-field-2" />
      <div className="auth-atmospheric-field auth-field-3" />
      <div className="auth-atmospheric-field auth-field-4" />
      <div className="auth-atmospheric-field auth-field-5" />
    </div>
  )
}
