import RiskGauge from './RiskGauge.jsx'
import FindingCard from './FindingCard.jsx'
import { exportUrl } from '../api.js'

const SEV_ORDER = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL']
const EXPORT_FORMATS = ['json', 'markdown', 'html', 'sarif', 'pdf']

export default function ReportView({ workspace, onDecide }) {
  const report = workspace.report
  const s = report ? report.summary : {
    risk_score: 0, total_vulnerabilities: 0,
    critical_count: 0, high_count: 0, medium_count: 0, low_count: 0,
  }

  const patchesByFinding = {}
  ;(workspace.patches || []).forEach((p) => { patchesByFinding[p.finding_id] = p })

  const findings = report
    ? [...report.findings].sort((a, b) => SEV_ORDER.indexOf(a.severity) - SEV_ORDER.indexOf(b.severity))
    : []

  return (
    <>
      <div className="report-head">
        <div>
          <h2>{workspace.template.file_path}</h2>
          <div className="path">
            <span className="pill terraform">{workspace.template.iac_type}</span>
            <span className="pill aws">{workspace.template.cloud_provider}</span>
            &nbsp;· workspace {workspace.workspace_id.slice(0, 8)}
          </div>
        </div>
        <div className="export-row">
          {EXPORT_FORMATS.map((fmt) => (
            <a
              key={fmt}
              className="ghost"
              href={exportUrl(workspace.workspace_id, fmt)}
              target="_blank"
              rel="noreferrer"
            >
              ↓ {fmt}
            </a>
          ))}
        </div>
      </div>

      <div className="gauge-card">
        <RiskGauge score={s.risk_score} />
        <div className="gauge-stats">
          <div className="gstat TOTAL"><div className="n">{s.total_vulnerabilities}</div><div className="l">total</div></div>
          <div className="gstat CRITICAL"><div className="n">{s.critical_count}</div><div className="l">critical</div></div>
          <div className="gstat HIGH"><div className="n">{s.high_count}</div><div className="l">high</div></div>
          <div className="gstat MEDIUM"><div className="n">{s.medium_count}</div><div className="l">medium</div></div>
          <div className="gstat LOW"><div className="n">{s.low_count}</div><div className="l">low</div></div>
        </div>
      </div>

      <div className="findings-head">
        <h3>Findings ({findings.length})</h3>
      </div>
      <div>
        {findings.length === 0 ? (
          <div className="ws-empty">No findings for this template.</div>
        ) : (
          findings.map((f) => (
            <FindingCard
              key={f.finding_id}
              finding={f}
              patch={patchesByFinding[f.finding_id]}
              onDecide={onDecide}
            />
          ))
        )}
      </div>
    </>
  )
}
