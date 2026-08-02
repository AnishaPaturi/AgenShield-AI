import { useEffect, useState } from 'react'

const SEV_COLOR = { CRITICAL: '#FF5C6C', HIGH: '#FF9955', MEDIUM: '#F0C94A', LOW: '#5B8DEF' }

function colorFor(score) {
  if (score >= 70) return SEV_COLOR.CRITICAL
  if (score >= 40) return SEV_COLOR.HIGH
  if (score >= 15) return SEV_COLOR.MEDIUM
  return SEV_COLOR.LOW
}

export default function RiskGauge({ score }) {
  const r = 54
  const c = 2 * Math.PI * r
  const pct = Math.max(0, Math.min(100, score)) / 100
  const [offset, setOffset] = useState(c) // start empty, animate to filled

  useEffect(() => {
    const frame = requestAnimationFrame(() => setOffset(c * (1 - pct)))
    return () => cancelAnimationFrame(frame)
  }, [pct, c])

  return (
    <div className="gauge-wrap">
      <svg width="132" height="132" viewBox="0 0 132 132">
        <circle className="gauge-track" cx="66" cy="66" r={r} />
        <circle
          className="gauge-fill"
          cx="66" cy="66" r={r}
          stroke={colorFor(score)}
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="gauge-center">
        <div className="num">{score}</div>
        <div className="lbl">risk / 100</div>
      </div>
    </div>
  )
}
