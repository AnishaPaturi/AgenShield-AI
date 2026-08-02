import { useState } from 'react'

function DiffLine({ line }) {
  if (line.startsWith('+') && !line.startsWith('+++')) {
    return <span className="add">{line}{'\n'}</span>
  }
  if (line.startsWith('-') && !line.startsWith('---')) {
    return <span className="del">{line}{'\n'}</span>
  }
  return <>{line}{'\n'}</>
}

export default function FindingCard({ finding, patch, onDecide }) {
  const [open, setOpen] = useState(false)
  const compliance = (finding.compliance_mappings || [])
    .map((m) => `${m.framework}:${m.control_id}`)
    .join(', ')

  return (
    <div className={`finding ${finding.severity}`}>
      <div className="f-top">
        <span className={`sev-badge ${finding.severity}`}>{finding.severity}</span>
        <span className="f-title">{finding.title}</span>
        <span className="f-rule">{finding.rule_id}</span>
      </div>
      <div className="f-desc">{finding.description}</div>
      <div className="f-meta">
        <span>resource: <b>{finding.affected_resource}</b></span>
        <span>confidence: <b>{finding.confidence_score}</b></span>
        {compliance && <span>compliance: <b>{compliance}</b></span>}
      </div>

      {patch && (
        <>
          <div className="patch-toggle" onClick={() => setOpen((o) => !o)}>
            <span>{open ? '▾' : '▸'}</span> view suggested patch
          </div>
          {open && (
            <div className="patch-body">
              <pre className="diff">
                {(patch.unified_diff || '(no diff generated)')
                  .split('\n')
                  .map((line, i) => <DiffLine key={i} line={line} />)}
              </pre>
              <div className="patch-actions">
                <span className={`status-tag ${patch.remediation_status}`}>{patch.remediation_status}</span>
                <button className="ghost accept" onClick={() => onDecide(patch.patch_id, 'accept')}>
                  ✓ Accept patch
                </button>
                <button className="ghost reject" onClick={() => onDecide(patch.patch_id, 'reject')}>
                  ✕ Reject
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
