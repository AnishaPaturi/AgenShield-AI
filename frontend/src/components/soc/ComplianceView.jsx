import React from 'react'

export default function ComplianceView({ onNavigate }) {
  const frameworks = [
    { name: 'SOC 2 Type II', pct: 86, color: '#22C55E', controls: '43/50' },
    { name: 'HIPAA Security Rule', pct: 72, color: '#F59E0B', controls: '36/50' },
    { name: 'PCI-DSS v4.0', pct: 81, color: '#22C55E', controls: '48/59' },
    { name: 'NIST SP 800-53 Rev. 5', pct: 91, color: '#D6A84F', controls: '91/100' },
  ]

  const controls = [
    { id: 'NIST-AC-6', framework: 'NIST 800-53', title: 'Least Privilege Enforcement', status: 'PASSED', findings: 0 },
    { id: 'NIST-IA-2', framework: 'NIST 800-53', title: 'Identification and Authentication', status: 'WARNING', findings: 3 },
    { id: 'PCI-DSS-1.3', framework: 'PCI-DSS', title: 'Cardholder Perimeter Network Filtering', status: 'FAILED', findings: 5 },
    { id: 'SOC2-CC6.1', framework: 'SOC 2', title: 'Logical Access & Firewall Rules', status: 'WARNING', findings: 2 },
    { id: 'CIS-AWS-1.16', framework: 'CIS Benchmarks', title: 'IAM Policies Grant Least Privilege', status: 'PASSED', findings: 0 },
    { id: 'HIPAA-164.312', framework: 'HIPAA', title: 'Technical Safeguards / Data Encryption at Rest', status: 'PASSED', findings: 0 },
  ]

  return (
    <div className="compliance-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Regulatory Compliance &amp; Governance Center</h2>
          <p className="scc-subtitle">
            Automated policy alignment against SOC 2, HIPAA, PCI-DSS, and NIST SP 800-53 security controls.
          </p>
        </div>
        <button
          className="btn-start-analysis"
          style={{ padding: '8px 18px', fontSize: '12.5px' }}
          onClick={() => onNavigate('findings')}
        >
          View Non-Compliant Findings →
        </button>
      </div>

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
      <div className="scc-panel-card">
        <div className="scc-panel-head">
          <div className="scc-panel-title">
            <span>Regulatory Control Verification Matrix</span>
          </div>
          <span style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
            UPDATED REAL-TIME PER SCAN
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
                  {c.findings > 0 ? (
                    <span style={{ color: c.status === 'FAILED' ? '#EF4444' : '#F97316' }}>
                      {c.findings} finding(s)
                    </span>
                  ) : (
                    <span style={{ color: '#64748B' }}>0</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
