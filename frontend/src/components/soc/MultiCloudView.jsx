import React, { useMemo } from 'react'

export default function MultiCloudView({ workspaces = [], onNavigate }) {
  const clouds = useMemo(() => {
    const cloudConfigs = [
      {
        name: 'Amazon Web Services',
        tag: 'AWS',
        icon: '☁️',
        color: '#F97316',
        services: ['S3 Buckets', 'IAM Roles', 'VPC & Security Groups', 'RDS PostgreSQL', 'EKS Clusters'],
      },
      {
        name: 'Microsoft Azure',
        tag: 'AZURE',
        icon: '☁️',
        color: '#38BDF8',
        services: ['Storage Accounts (Blob)', 'Network Security Groups', 'Azure RBAC', 'Key Vault', 'AKS'],
      },
      {
        name: 'Google Cloud Platform',
        tag: 'GCP',
        icon: '☁️',
        color: '#22C55E',
        services: ['Cloud Storage (GCS)', 'VPC Firewall Rules', 'IAM Service Accounts', 'Cloud SQL', 'GKE'],
      },
      {
        name: 'Kubernetes Cloud-Native',
        tag: 'K8S',
        icon: '☸️',
        color: '#818CF8',
        services: ['ConfigMaps & Secrets', 'RBAC Bindings', 'PodSecurityPolicies', 'NetworkPolicies', 'Ingress'],
      },
    ]

    return cloudConfigs.map((c) => {
      let scans = 0
      let crit = 0
      let high = 0
      let med = 0

      workspaces.forEach((ws) => {
        const provider = (ws.template?.cloud_provider || '').toUpperCase()
        const iac = (ws.template?.iac_type || '').toUpperCase()
        const isMatch =
          provider === c.tag ||
          (c.tag === 'K8S' && (iac === 'KUBERNETES' || iac === 'HELM'))

        if (isMatch) {
          scans += 1
          const findings = ws.report?.findings || []
          findings.forEach((f) => {
            if (f.severity === 'CRITICAL') crit += 1
            else if (f.severity === 'HIGH') high += 1
            else if (f.severity === 'MEDIUM') med += 1
          })
        }
      })

      return {
        ...c,
        scans,
        crit,
        high,
        med,
      }
    })
  }, [workspaces])

  return (
    <div className="multicloud-view">
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Multi-Cloud Infrastructure Defense</h2>
          <p className="scc-subtitle">
            Unified policy enforcement and cross-cloud risk visibility across AWS, Azure, GCP, and Kubernetes.
          </p>
        </div>
        <button
          className="btn-start-analysis"
          style={{ padding: '8px 18px', fontSize: '12.5px' }}
          onClick={() => onNavigate('new-scan')}
        >
          ⚡ Scan Cloud Template →
        </button>
      </div>

      {/* 4 Cloud Zones */}
      <div className="cloud-zones-grid">
        {clouds.map((c) => (
          <div key={c.tag} className="cloud-zone-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div className="cloud-zone-title">
                <span>{c.icon}</span>
                <span>{c.tag}</span>
              </div>
              <span style={{ fontFamily: 'JetBrains Mono', fontSize: '12px', color: '#CBD5E1' }}>
                {c.scans} scans
              </span>
            </div>

            <div style={{ fontSize: '12.5px', color: '#94A3B8' }}>{c.name}</div>

            {/* Severity Counters */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', background: 'rgba(18, 24, 33, 0.7)', padding: '12px', borderRadius: '8px' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '10px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>CRITICAL</div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: '#EF4444', fontFamily: 'JetBrains Mono' }}>
                  {c.crit}
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '10px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>HIGH</div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: '#F97316', fontFamily: 'JetBrains Mono' }}>
                  {c.high}
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '10px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>MEDIUM</div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: '#F59E0B', fontFamily: 'JetBrains Mono' }}>
                  {c.med}
                </div>
              </div>
            </div>

            {/* Monitored Services */}
            <div>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono', marginBottom: '6px' }}>
                MONITORED CLOUD PRIMITIVES
              </div>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {c.services.map((s) => (
                  <span
                    key={s}
                    style={{
                      fontSize: '11px',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      color: '#CBD5E1',
                    }}
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* IaC Coverage Grid */}
      <div className="scc-panel-card">
        <div className="scc-panel-head">
          <div className="scc-panel-title">
            <span>IaC Format Architecture &amp; Parser Coverage</span>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'Outfit' }}>Terraform (.tf)</div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
              Full AST resolution with loop unfolding (for_each, count), module traversal &amp; local variable propagation.
            </div>
            <div style={{ fontSize: '11px', color: '#D6A84F', marginTop: '8px', fontFamily: 'JetBrains Mono' }}>
              AWS · Azure · GCP · K8s
            </div>
          </div>

          <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'Outfit' }}>CloudFormation (.yaml / .json)</div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
              Intrinsic function evaluation (Fn::Sub, Fn::GetAtt, Ref) with cfn-lint static rule validation.
            </div>
            <div style={{ fontSize: '11px', color: '#D6A84F', marginTop: '8px', fontFamily: 'JetBrains Mono' }}>
              AWS Native Stacks
            </div>
          </div>

          <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'Outfit' }}>Kubernetes Manifests</div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
              PodSecurityStandards, RBAC privilege audits, network policies, and container capabilities checks.
            </div>
            <div style={{ fontSize: '11px', color: '#D6A84F', marginTop: '8px', fontFamily: 'JetBrains Mono' }}>
              EKS · AKS · GKE · Vanilla
            </div>
          </div>

          <div style={{ background: 'rgba(18, 24, 33, 0.7)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.06)' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'Outfit' }}>Helm Charts &amp; Values</div>
            <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
              Template dry-run rendering, values.yaml injection checks, and secret exposure interception.
            </div>
            <div style={{ fontSize: '11px', color: '#D6A84F', marginTop: '8px', fontFamily: 'JetBrains Mono' }}>
              Multi-Cloud Deployments
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
