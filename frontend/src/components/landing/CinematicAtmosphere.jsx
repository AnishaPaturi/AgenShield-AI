import { useEffect, useRef } from 'react'

export default function CinematicAtmosphere() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationFrameId
    let width = 0
    let height = 0
    let scrollY = window.scrollY

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    // Resize canvas with device pixel ratio
    const handleResize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2)
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width * dpr
      canvas.height = height * dpr
      ctx.scale(dpr, dpr)
    }

    handleResize()
    window.addEventListener('resize', handleResize, { passive: true })

    const handleScroll = () => {
      scrollY = window.scrollY
    }
    window.addEventListener('scroll', handleScroll, { passive: true })

    // Generate constellation nodes (28 nodes for clean, non-cluttered network)
    const nodeCount = 28
    const nodes = []
    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random(),
        y: Math.random(),
        vx: (Math.random() - 0.5) * 0.0003,
        vy: (Math.random() - 0.5) * 0.0003,
        radius: 1.2 + Math.random() * 1.6,
        baseAlpha: 0.15 + Math.random() * 0.35,
        phase: Math.random() * Math.PI * 2,
      })
    }

    // Traveling data packets along connections
    const packets = [
      { from: 0, to: 4, t: 0.1, speed: 0.002, color: '#38BDF8' },
      { from: 7, to: 12, t: 0.4, speed: 0.0018, color: '#818CF8' },
      { from: 15, to: 20, t: 0.7, speed: 0.0022, color: '#A78BFA' },
      { from: 3, to: 18, t: 0.2, speed: 0.0016, color: '#38BDF8' },
    ]

    let time = 0

    const render = () => {
      time += 0.008
      ctx.clearRect(0, 0, width, height)

      // 1. Soft atmospheric background gradients (Deep Navy / Black)
      const bgGrad = ctx.createLinearGradient(0, 0, 0, height)
      bgGrad.addColorStop(0, '#030712')
      bgGrad.addColorStop(0.5, '#050B1A')
      bgGrad.addColorStop(1, '#02050E')
      ctx.fillStyle = bgGrad
      ctx.fillRect(0, 0, width, height)

      // Parallax scroll factor
      const parallaxY = (scrollY * 0.04) % height

      // 2. Extremely soft ambient violet / electric blue light bleeds
      const orb1X = width * 0.25 + Math.sin(time * 0.3) * 60
      const orb1Y = (height * 0.35 + Math.cos(time * 0.2) * 50 - parallaxY + height) % height
      const grad1 = ctx.createRadialGradient(orb1X, orb1Y, 10, orb1X, orb1Y, width * 0.4)
      grad1.addColorStop(0, 'rgba(79, 70, 229, 0.08)')
      grad1.addColorStop(0.5, 'rgba(99, 102, 241, 0.03)')
      grad1.addColorStop(1, 'rgba(3, 7, 18, 0)')
      ctx.fillStyle = grad1
      ctx.fillRect(0, 0, width, height)

      const orb2X = width * 0.75 + Math.cos(time * 0.25) * 80
      const orb2Y = (height * 0.65 + Math.sin(time * 0.35) * 60 - parallaxY + height) % height
      const grad2 = ctx.createRadialGradient(orb2X, orb2Y, 10, orb2X, orb2Y, width * 0.45)
      grad2.addColorStop(0, 'rgba(56, 189, 248, 0.06)')
      grad2.addColorStop(0.5, 'rgba(129, 140, 248, 0.02)')
      grad2.addColorStop(1, 'rgba(3, 7, 18, 0)')
      ctx.fillStyle = grad2
      ctx.fillRect(0, 0, width, height)

      if (prefersReducedMotion) {
        return
      }

      // 3. Update & Draw Constellation Nodes & Faint Connection Lines
      for (let i = 0; i < nodeCount; i++) {
        const n = nodes[i]
        n.x += n.vx
        n.y += n.vy
        if (n.x < 0) n.x = 1
        if (n.x > 1) n.x = 0
        if (n.y < 0) n.y = 1
        if (n.y > 1) n.y = 0

        const px = n.x * width
        const py = ((n.y * height - parallaxY * 0.5) % height + height) % height
        const alpha = n.baseAlpha + Math.sin(time * 2 + n.phase) * 0.12

        ctx.beginPath()
        ctx.arc(px, py, n.radius, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(167, 139, 250, ${Math.max(0, alpha)})`
        ctx.fill()
      }

      // Draw subtle connection lines between nearby nodes
      ctx.lineWidth = 0.6
      for (let i = 0; i < nodeCount; i++) {
        const n1 = nodes[i]
        const p1x = n1.x * width
        const p1y = ((n1.y * height - parallaxY * 0.5) % height + height) % height

        for (let j = i + 1; j < nodeCount; j++) {
          const n2 = nodes[j]
          const p2x = n2.x * width
          const p2y = ((n2.y * height - parallaxY * 0.5) % height + height) % height

          const dx = p1x - p2x
          const dy = p1y - p2y
          const dist = Math.sqrt(dx * dx + dy * dy)
          const maxDist = width * 0.22

          if (dist < maxDist) {
            const lineAlpha = (1 - dist / maxDist) * 0.07
            ctx.strokeStyle = `rgba(129, 140, 248, ${lineAlpha})`
            ctx.beginPath()
            ctx.moveTo(p1x, p1y)
            ctx.lineTo(p2x, p2y)
            ctx.stroke()
          }
        }
      }

      // 4. Subtle Orbital Arcs
      const orbitCenterX = width * 0.5
      const orbitCenterY = ((height * 0.5 - parallaxY * 0.3) % height + height) % height
      ctx.save()
      ctx.beginPath()
      ctx.arc(orbitCenterX, orbitCenterY, Math.min(width, height) * 0.38, 0, Math.PI * 2)
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.025)'
      ctx.lineWidth = 1
      ctx.setLineDash([4, 18])
      ctx.stroke()
      ctx.restore()

      // 5. Tiny Traveling Data Packets along defined paths
      for (const pkt of packets) {
        pkt.t = (pkt.t + pkt.speed) % 1
        const nA = nodes[pkt.from % nodeCount]
        const nB = nodes[pkt.to % nodeCount]
        const ax = nA.x * width
        const ay = ((nA.y * height - parallaxY * 0.5) % height + height) % height
        const bx = nB.x * width
        const by = ((nB.y * height - parallaxY * 0.5) % height + height) % height

        const curX = ax + (bx - ax) * pkt.t
        const curY = ay + (by - ay) * pkt.t

        ctx.beginPath()
        ctx.arc(curX, curY, 2, 0, Math.PI * 2)
        ctx.fillStyle = pkt.color
        ctx.shadowColor = pkt.color
        ctx.shadowBlur = 6
        ctx.fill()
        ctx.shadowBlur = 0
      }

      animationFrameId = requestAnimationFrame(render)
    }

    render()

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  return (
    <div className="cinematic-atmosphere-layer" aria-hidden="true">
      <canvas ref={canvasRef} className="cinematic-atmosphere-canvas" />
      {/* Barely visible technical grid & noise texture */}
      <div className="cinematic-subtle-grid" />
      <div className="cinematic-subtle-vignette" />
    </div>
  )
}
