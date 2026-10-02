import React, { useState, useEffect } from 'react'

export default function ScrollProgressBar() {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let ticking = false
    const calculateProgress = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const docEl = document.documentElement
          const scrollTop = window.scrollY || docEl.scrollTop
          const scrollHeight = docEl.scrollHeight - docEl.clientHeight
          if (scrollHeight > 0) {
            const pct = Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100))
            setProgress(pct)
          } else {
            setProgress(0)
          }
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('scroll', calculateProgress, { passive: true })
    window.addEventListener('resize', calculateProgress, { passive: true })
    calculateProgress()

    return () => {
      window.removeEventListener('scroll', calculateProgress)
      window.removeEventListener('resize', calculateProgress)
    }
  }, [])

  if (progress <= 0) return null

  return (
    <div
      className="scroll-progress-bar-container"
      role="progressbar"
      aria-valuenow={Math.round(progress)}
      aria-valuemin="0"
      aria-valuemax="100"
      aria-label="Page scroll progress"
    >
      <div
        className="scroll-progress-bar-fill"
        style={{ width: `${progress}%` }}
      />
    </div>
  )
}
