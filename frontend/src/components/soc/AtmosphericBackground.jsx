import React from 'react'

/**
 * AtmosphericBackground
 * Living atmospheric gradient fields for the Security Command Center (Homepage).
 * Restrained, slow-moving blurred gradient aurora forms.
 *
 * Dark mode: Deep midnight base with translucent lavender/violet, cyan, and soft pink fields.
 * Light mode: Sakura Light with translucent blush pink, dusty rose, and sage green fields.
 *
 * Strictly isolated to SecurityCommandCenter ONLY.
 * Respects prefers-reduced-motion.
 */
export default function AtmosphericBackground() {
  return (
    <div className="atmospheric-bg-container" aria-hidden="true">
      <div className="atmospheric-field atmospheric-field-1" />
      <div className="atmospheric-field atmospheric-field-2" />
      <div className="atmospheric-field atmospheric-field-3" />
      <div className="atmospheric-field atmospheric-field-4" />
      <div className="atmospheric-field atmospheric-field-5" />
    </div>
  )
}
