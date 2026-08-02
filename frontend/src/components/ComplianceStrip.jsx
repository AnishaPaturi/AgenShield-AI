const FRAMEWORKS = ['SOC 2', 'HIPAA', 'PCI-DSS', 'NIST 800-53', 'CIS Benchmarks', 'OWASP']

export default function ComplianceStrip() {
  return (
    <div className="compliance-strip">
      <span className="compliance-label">Findings map to</span>
      <div className="compliance-badges">
        {FRAMEWORKS.map((f) => (
          <span key={f} className="compliance-badge">{f}</span>
        ))}
      </div>
    </div>
  )
}
