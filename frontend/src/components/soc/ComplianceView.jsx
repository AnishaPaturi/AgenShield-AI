import React, { useMemo } from 'react'

export default function ComplianceView({ workspace, onNavigate }) {
  const findings = workspace?.report?.findings || []

  const { frameworks, controls } = useMemo(() => {
    const fwMap = {
      'SOC 2': { name: 'SOC 2 Type II', violations: 0, total: 50 },
      'HIPAA': { name: 'HIPAA Security Rule', violations: 0, total: 50 },
      'PCI-DSS': { name: 'PCI-DSS v4.0', violations: 0, total: 50 },
      'NIST': { name: 'NIST SP 800-53', violations: 0, total: 50 },
      'CIS': { name: 'CIS Benchmarks', violations: 0, total: 50 },
    }

    const ctrlMap = {}

    findings.forEach((f) => {
      const list = Array.isArray(f.compliance_mappings)
        ? f.compliance_mappings
        : Array.isArray(f.compliance)
        ? f.compliance
        : []

      list.forEach((entry) => {
        const str = typeof entry === 'string' ? entry : `${entry.framework || ''} ${entry.control_id || ''}`
        const upper = str.toUpperCase()

        for (const [key, obj] of Object.entries(fwMap)) {
          if (upper.includes(key)) {
            obj.violations += 1
          }
        }

        if (!ctrlMap[str]) {
          ctrlMap[str] = {
            id: str,
            framework: str.split(' ')[0] || 'SECURITY',
            title: f.title || 'Security Control Enforcement',
            status: f.severity === 'CRITICAL' ? 'FAILED' : 'WARNING',
            findings: 0,
          }
        }
        ctrlMap[str].findings += 1
      })
    })

    const fwList = Object.entries(fwMap).map(([k, v]) => {
      const satisfied = Math.max(0, v.total - v.violations)
      const pct = Math.round((satisfied / v.total) * 100)
      const color = pct >= 85 ? '#22C55E' : pct >= 70 ? '#F59E0B' : '#EF4444'
      return {
        name: v.name,
        pct,
        color,
        controls: `${satisfied}/${v.total}`,
      }
    })

    return {
      frameworks: fwList,
      controls: Object.values(ctrlMap),
    }
  }, [findings])

  return (
    <div className="compliance-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Regulatory Compliance &amp; Governance Center</h2>
          <p className="scc-subtitle">
            Automated policy alignment against SOC 2, HIPAA, PCI-DSS, CIS, and NIST SP 800-53 security controls.
          </p>
        </div>
        {findings.length > 0 && (
          <button
            className="btn-start-analysis"
            style={{ padding: '8px 18px', fontSize: '12.5px' }}
            onClick={() => onNavigate('findings')}
          >
            View Non-Compliant Findings →
          </button>
        )}
      </div>

      {!workspace || findings.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Compliance Data Available
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            {workspace
              ? 'No compliance violations were detected in the current workspace.'
              : 'No workspace is currently selected. Run a scan on an IaC template to evaluate regulatory compliance.'}
          </p>
          <button
            className="btn-start-analysis"
            style={{ marginTop: '20px', padding: '8px 20px', fontSize: '13px' }}
            onClick={() => onNavigate('new-scan')}
          >
            ⚡ Run New Scan
          </button>
        </div>
      ) : (
        <>
          {/* Compliance Posture Meters */}
          <div className="compliance-meters-grid">
            {frameworks.map((f) => (
              <div key={f.name} className="compliance-meter-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontFamily: 'Outfit', fontSize: '14.5px', fontWeight: 700, color: '#FFFFFF' }}>
                    {f.name}
                  </span>
                  <span style={{ fontFamily: 'JetBrains Mono', fontSize: '15px', fontWeight: 700, color: f.color }}>
                    {f.pct}%
                  </span>
                </div>

                <div className="risk-dist-bar-track" style={{ height: '8px', margin: '8px 0' }}>
                  <div
                    className="risk-dist-bar-fill"
                    style={{ width: `${f.pct}%`, background: f.color, boxShadow: `0 0 8px ${f.color}` }}
                  ></div>
                </div>

                <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
                  {f.controls} Controls Satisfied
                </div>
              </div>
            ))}
          </div>

          {/* Controls Audit Table */}
          {controls.length > 0 && (
            <div className="scc-panel-card">
              <div className="scc-panel-head">
                <div className="scc-panel-title">
                  <span>Regulatory Control Verification Matrix</span>
                </div>
                <span style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
                  EVALUATED FROM WORKSPACE FINDINGS
                </span>
              </div>

              <table className="scc-findings-table">
                <thead>
                  <tr>
                    <th>CONTROL ID</th>
                    <th>FRAMEWORK</th>
                    <th>SECURITY CONTROL TITLE</th>
                    <th>STATUS</th>
                    <th>FINDINGS</th>
                  </tr>
                </thead>
                <tbody>
                  {controls.map((c) => (
                    <tr key={c.id}>
                      <td style={{ fontFamily: 'JetBrains Mono', fontWeight: 700, color: '#D6A84F' }}>{c.id}</td>
                      <td style={{ fontFamily: 'JetBrains Mono', fontSize: '12px' }}>{c.framework}</td>
                      <td style={{ color: '#FFFFFF', fontWeight: 500 }}>{c.title}</td>
                      <td>
                        <span
                          style={{
                            fontFamily: 'JetBrains Mono',
                            fontSize: '11px',
                            fontWeight: 700,
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background:
                              c.status === 'PASSED'
                                ? 'rgba(34, 197, 94, 0.15)'
                                : c.status === 'WARNING'
                                ? 'rgba(249, 115, 22, 0.15)'
                                : 'rgba(239, 68, 68, 0.15)',
                            color:
                              c.status === 'PASSED'
                                ? '#22C55E'
                                : c.status === 'WARNING'
                                ? '#F97316'
                                : '#EF4444',
                          }}
                        >
                          {c.status === 'PASSED' ? '✓ PASSED' : c.status === 'WARNING' ? '⚠ WARNING' : '✕ FAILED'}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                        <span style={{ color: c.status === 'FAILED' ? '#EF4444' : '#F97316' }}>
                          {c.findings} finding(s)
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
