import { useEffect, useState } from 'react'

// Phase cycle: idle -> scanning -> flagged -> patched -> (hold) -> idle
const DURATIONS = { idle: 900, scanning: 1600, flagged: 1400, patched: 2200 }
const ORDER = ['idle', 'scanning', 'flagged', 'patched']

const LINES = [
  { code: 'resource "aws_s3_bucket" "data" {', kind: 'plain' },
  { code: '  bucket = "prod-app-data"', kind: 'plain' },
  { code: '  acl    = "public-read"', patched: '  acl    = "private"', kind: 'finding' },
  { code: '}', kind: 'plain' },
  { code: '', kind: 'blank' },
  { code: 'resource "aws_db_instance" "primary" {', kind: 'plain' },
  { code: '  engine              = "postgres"', kind: 'plain' },
  { code: '  publicly_accessible = true', patched: '  publicly_accessible = false', kind: 'finding' },
  { code: '}', kind: 'plain' },
]

export default function ScanDemo() {
  const reduceMotion = typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

  const [phase, setPhase] = useState(reduceMotion ? 'patched' : 'idle')

  useEffect(() => {
    if (reduceMotion) return
    const idx = ORDER.indexOf(phase)
    const next = ORDER[(idx + 1) % ORDER.length]
    const t = setTimeout(() => setPhase(next), DURATIONS[phase])
    return () => clearTimeout(t)
  }, [phase, reduceMotion])

  const isPatched = phase === 'patched'
  const isFlagged = phase === 'flagged' || isPatched
  const isScanning = phase === 'scanning'

  const statusLabel = {
    idle: 'watching for changes',
    scanning: 'parsing · hybrid AST scan',
    flagged: '2 findings · analyzing',
    patched: '2 patches applied',
  }[phase]

  const statusColor = isPatched ? 'var(--ok)' : (phase === 'flagged' ? 'var(--crit)' : 'var(--muted)')

  return (
    <div className="scandemo" aria-hidden="true">
      <div className="scandemo-bar">
        <span className="scandemo-dots"><i /><i /><i /></span>
        <span className="scandemo-file">main.tf</span>
        <span className="scandemo-status" style={{ color: statusColor }}>
          <span className="scandemo-status-dot" style={{ background: statusColor }} />
          {statusLabel}
        </span>
      </div>
      <div className={`scandemo-body ${isScanning ? 'is-scanning' : ''}`}>
        {isScanning && <div className="scandemo-beam" />}
        <pre>
          {LINES.map((line, i) => {
            const flaggedNow = line.kind === 'finding' && isFlagged
            const text = flaggedNow && isPatched ? line.patched : line.code
            const cls = line.kind === 'finding'
              ? (isPatched ? 'ln patched' : isFlagged ? 'ln flagged' : 'ln')
              : 'ln'
            return (
              <div key={i} className={cls}>
                <span className="gutter">{String(i + 1).padStart(2, '0')}</span>
                <span className="code">{text || '\u00A0'}</span>
                {flaggedNow && !isPatched && <span className="tag crit">CKV_AWS_20</span>}
                {flaggedNow && isPatched && <span className="tag ok">patched</span>}
              </div>
            )
          })}
        </pre>
      </div>
    </div>
  )
}
