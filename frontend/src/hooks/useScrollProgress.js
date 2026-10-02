import { useState, useEffect } from 'react'

/**
 * Custom hook to track bi-directional scroll progress through an element.
 * Returns progress from 0 (just entering bottom of viewport) to 1 (scrolled past top of viewport),
 * as well as inView status.
 * Reversible: scrolling back up reduces progress accordingly.
 */
export function useScrollProgress(ref, options = {}) {
  const { startOffset = 0.15, endOffset = 0.85 } = options
  const [progress, setProgress] = useState(0)
  const [isInView, setIsInView] = useState(false)

  useEffect(() => {
    let animationFrameId = null

    const handleScroll = () => {
      if (!ref.current) return

      const rect = ref.current.getBoundingClientRect()
      const windowHeight = window.innerHeight || 800

      // In-view check
      const visible = rect.bottom > 0 && rect.top < windowHeight
      setIsInView(visible)

      if (visible) {
        // Calculate progress within focus zone
        // 0 when rect.top is near windowHeight * (1 - startOffset)
        // 1 when rect.bottom is near windowHeight * (1 - endOffset)
        const totalDistance = rect.height + windowHeight * (endOffset - startOffset)
        const currentDistance = windowHeight * (1 - startOffset) - rect.top
        const calculated = Math.min(1, Math.max(0, currentDistance / Math.max(totalDistance, 1)))
        
        setProgress((prev) => {
          // Avoid micro-jitter
          if (Math.abs(prev - calculated) > 0.005) {
            return Number(calculated.toFixed(3))
          }
          return prev
        })
      } else if (rect.top >= windowHeight) {
        setProgress(0)
      } else if (rect.bottom <= 0) {
        setProgress(1)
      }
    }

    const onScroll = () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId)
      animationFrameId = requestAnimationFrame(handleScroll)
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll, { passive: true })
    // Initial evaluation
    handleScroll()

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId)
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [ref, startOffset, endOffset])

  return { progress, isInView }
}

export default useScrollProgress
