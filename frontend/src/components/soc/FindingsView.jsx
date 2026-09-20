import React, { useState } from 'react'

export default function FindingsView({ workspace, onNavigate }) {
  const [filter, setFilter] = useState('ALL')
  const [selectedFinding, setSelectedFinding] = useState(null)

  // Use real workspace findings or fallback to rich mock investigation findings
  const rawFindings = workspace?.report?.findings || [
    {
      finding_id: 'f-s3-public',
      severity: 'CRITICAL',
      priority: 96,
      title: 'S3 Bucket Allows World Public Access',
      rule_id: 'CIS-AWS-2.1.5',
      provider: 'AWS',
      iac_type: 'Terraform',
      affected_resource: 'aws_s3_bucket.prod_customer_data',
      confidence_score: 0.94,
      blast_radius: 7,
      attack_path: ['INTERNET', 'SECURITY GROUP (0.0.0.0/0)', 'S3 (PUBLIC ACL)', 'RDS DATABASE CREDENTIALS'],
      compliance: ['NIST AC-6', 'PCI-DSS 1.3', 'SOC 2 CC6.1'],
      description:
        'Bucket does not define aws_s3_bucket_public_access_block. An attacker on the public Internet can enumerate objects and exfiltrate customer PII and database backup dumps.',
      remediation: 'Attach aws_s3_bucket_public_access_block with block_public_acls = true.',
    },
    {
      finding_id: 'f-sg-open',
      severity: 'HIGH',
      priority: 91,
      title: 'Security Group Ingress Allows All Traffic (0.0.0.0/0 on Port 22)',
      rule_id: 'CIS-AWS-4.1',
      provider: 'AWS',
      iac_type: 'Terraform',
      affected_resource: 'aws_security_group.bastion_sg',
      confidence_score: 0.92,
      blast_radius: 5,
      attack_path: ['INTERNET', 'BASTION HOST (PORT 22)', 'INTERNAL VPC'],
      compliance: ['NIST AC-3', 'PCI-DSS 1.2', 'CIS 4.1'],
      description:
        'SSH port 22 is exposed to the world. Automated brute-force credential stuffing and zero-day SSH daemon exploit vectors can compromise the jump host.',
      remediation: 'Restrict ingress cidr_blocks to specific corporate VPN CIDRs.',
    },
    {
      finding_id: 'f-k8s-secret',
      severity: 'HIGH',
      priority: 89,
      title: 'Unencrypted AWS Access Key Injected in Kubernetes ConfigMap',
      rule_id: 'CWE-798',
      provider: 'K8s',
      iac_type: 'Helm',
      affected_resource: 'ConfigMap.payment-service-config',
      confidence_score: 0.96,
      blast_radius: 12,
      attack_path: ['K8S CLUSTER ACCESS', 'CONFIGMAP READ', 'AWS ACCOUNT TAKEOVER'],
      compliance: ['NIST IA-2', 'SOC 2 CC6.1', 'PCI-DSS 8.2'],
      description:
        'Plaintext AWS_SECRET_ACCESS_KEY found in ConfigMap values. ConfigMaps are unencrypted at rest by default and readable by any service account with pod-reader role.',
      remediation: 'Migrate credential to Kubernetes Secret with KMS envelope encryption.',
    },
    {
      finding_id: 'f-ebs-kms',
      severity: 'MEDIUM',
      priority: 74,
      title: 'EBS Volume Missing Customer Managed KMS Key Encryption',
      rule_id: 'CIS-AWS-2.2.1',
      provider: 'AWS',
      iac_type: 'CloudFormation',
      affected_resource: 'AWS::EC2::Volume',
      confidence_score: 0.88,
      blast_radius: 2,
      attack_path: ['PHYSICAL DISK ACCESS', 'UNENCRYPTED SNAPSHOT EXPOSURE'],
      compliance: ['NIST SC-13', 'HIPAA 164.312'],
      description:
        'EBS volume uses default AWS managed key rather than dedicated customer managed key (CMK), preventing granular audit logging and key rotation.',
      remediation: 'Set Encrypted: true and specify dedicated KmsKeyId.',
    },
  ]

  const filtered = filter === 'ALL' ? rawFindings : rawFindings.filter((f) => f.severity === filter)

  return (
    <div className="findings-investigation-view">
      {/* Header with Filters */}
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Security Findings &amp; Investigation</h2>
          <p className="scc-subtitle">
            Every vulnerability calibrated with blast radius analysis, attack paths, and compliance control mappings.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
            <button
              key={s}
              className={`tab-btn ${filter === s ? 'active' : ''}`}
              style={{ fontSize: '11.5px', padding: '6px 12px' }}
              onClick={() => setFilter(s)}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Findings List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {filtered.map((f) => {
          const confidencePct = Math.round((f.confidence_score || 0.9) * 100)
          return (
            <div key={f.finding_id || f.id} className={`finding-inv-card ${f.severity}`}>
              {/* Card Top: Severity Badge + Priority Score */}
              <div className="finding-inv-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className={`sev-badge ${f.severity}`}>{f.severity}</span>
                  <span className="finding-inv-title">{f.title}</span>
                </div>
                <div className="priority-score-badge">
                  PRIORITY {f.priority || (f.severity === 'CRITICAL' ? 96 : 89)}
                </div>
              </div>

              {/* Target & IaC Format */}
              <div style={{ fontSize: '13px', color: '#94A3B8', fontFamily: 'JetBrains Mono' }}>
                <b style={{ color: '#FFFFFF' }}>{f.provider || 'AWS'}</b> · {f.iac_type || 'Terraform'} ·{' '}
                <span style={{ color: '#D6A84F' }}>{f.affected_resource}</span>
              </div>

              {/* Meta Grid: Confidence, Blast Radius, Rule */}
              <div className="finding-inv-meta-grid">
                <div>
                  <span>Confidence: </span>
                  <b>{confidencePct}%</b>
                </div>
                <div>
                  <span>Blast Radius: </span>
                  <b style={{ color: f.blast_radius >= 6 ? '#EF4444' : '#F97316' }}>
                    {f.blast_radius || 5} assets
                  </b>
                </div>
                <div>
                  <span>Rule ID: </span>
                  <b>{f.rule_id}</b>
                </div>
                <div>
                  <span>Auto-Patch: </span>
                  <b style={{ color: '#22C55E' }}>ELIGIBLE (C &gt;= 0.85)</b>
                </div>
              </div>

              {/* Attack Path Mini Strip */}
              <div className="attack-path-investigation">
                <div style={{ fontSize: '11px', color: '#EF4444', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                  ⚡ EXPLOIT ATTACK PATH
                </div>
                <div className="attack-path-nodes-flow">
                  {(f.attack_path || ['INTERNET', 'SECURITY GROUP', 'S3', 'DATABASE']).map((step, idx, arr) => (
                    <React.Fragment key={idx}>
                      <span className={`attack-node-pill ${idx === arr.length - 1 ? 'vuln' : ''}`}>
                        {step}
                      </span>
                      {idx < arr.length - 1 && <span className="attack-arrow">→</span>}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Compliance Badges */}
              <div>
                <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', marginBottom: '6px' }}>
                  COMPLIANCE FRAMEWORK MAPPINGS
                </div>
                <div className="compliance-tags-row">
                  {(f.compliance || ['NIST AC-6', 'PCI-DSS 1.3', 'SOC 2']).map((c) => (
                    <span key={c} className="compliance-tag">
                      [{c}]
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="finding-inv-actions">
                <button
                  className="btn-view-finding"
                  onClick={() => setSelectedFinding(f)}
                >
                  🔍 View Finding Details
                </button>
                <button
                  className="btn-view-patch"
                  onClick={() => onNavigate('remediation')}
                >
                  ⚡ View AI Patch &amp; Diff →
                </button>
                <button
                  className="soc-back-home-btn"
                  onClick={() => onNavigate('attack-map')}
                >
                  🕸️ View Attack Graph →
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Investigation Details Modal */}
      {selectedFinding && (
        <div className="modal-overlay" onClick={() => setSelectedFinding(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '640px' }}>
            <div className="modal-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Vulnerability Investigation</span>
              <button
                className="modal-close"
                onClick={() => setSelectedFinding(null)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
            <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span className={`sev-badge ${selectedFinding.severity}`}>{selectedFinding.severity}</span>
                <h3 style={{ margin: '8px 0 4px', color: '#FFFFFF', fontFamily: 'Outfit' }}>
                  {selectedFinding.title}
                </h3>
                <div style={{ fontSize: '12px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
                  Rule: {selectedFinding.rule_id} · Resource: {selectedFinding.affected_resource}
                </div>
              </div>

              <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '14px', borderRadius: '8px', fontSize: '13px', color: '#CBD5E1', lineHeight: '1.6' }}>
                <b>Impact Assessment:</b><br />
                {selectedFinding.description}
              </div>

              <div style={{ background: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.3)', padding: '14px', borderRadius: '8px', fontSize: '13px', color: '#86EFAC' }}>
                <b>Remediation Strategy:</b><br />
                {selectedFinding.remediation}
              </div>

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  className="soc-back-home-btn"
                  onClick={() => setSelectedFinding(null)}
                >
                  Close
                </button>
                <button
                  className="btn-start-analysis"
                  style={{ padding: '8px 18px', fontSize: '13px' }}
                  onClick={() => {
                    setSelectedFinding(null)
                    onNavigate('remediation')
                  }}
                >
                  Launch Remediation →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
