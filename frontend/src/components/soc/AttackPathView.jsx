import React, { useState } from 'react'

export default function AttackPathView({ onNavigate }) {
  const [selectedNode, setSelectedNode] = useState('database')

  const nodeData = {
    internet: {
      id: 'internet',
      label: 'PUBLIC INTERNET',
      type: 'Threat Origin',
      resource: '0.0.0.0/0 (Untrusted Inbound)',
      exposure: 'External Public Network',
      dependencies: 'All Internet-facing ingresses',
      blastRadius: 'Global reach',
      chokePoint: 'Perimeter WAF / Security Group',
      recommendedAction: 'Enforce Cloudflare / AWS WAF with rate limiting & geo-blocking.',
    },
    alb: {
      id: 'alb',
      label: 'Application Load Balancer',
      type: 'Ingress Proxy',
      resource: 'aws_lb.public_alb',
      exposure: 'Public IP: 54.182.90.12 (Port 80/443)',
      dependencies: 'Target Group -> Web EC2 cluster',
      blastRadius: '3 EC2 instances, 1 RDS subnet',
      chokePoint: 'ALB Security Group listener rules',
      recommendedAction: 'Drop plaintext HTTP port 80 listener; enforce HTTPS TLS 1.3 only.',
    },
    sg: {
      id: 'sg',
      label: 'Security Group (Overprivileged)',
      type: 'Choke Point ⚠',
      resource: 'aws_security_group.ingress_open',
      exposure: 'Port 5432 and 22 open to 0.0.0.0/0',
      dependencies: 'EC2 App Nodes, S3 VPC Endpoint, RDS Database',
      blastRadius: '7 resources',
      chokePoint: '★ PRIMARY CHOKE POINT ★',
      recommendedAction: 'Restrict inbound CIDR to VPC CIDR (10.0.0.0/16) and revoke public SSH.',
    },
    ec2: {
      id: 'ec2',
      label: 'App Workload EC2',
      type: 'Compute Node',
      resource: 'aws_instance.app_server',
      exposure: 'Contains attached IAM Role with S3 Full Access',
      dependencies: 'EBS Volume, IAM Instance Profile, CloudWatch Agent',
      blastRadius: '4 resources',
      chokePoint: 'IAM Role Policy',
      recommendedAction: 'Demote instance profile to least-privilege read-only S3 role.',
    },
    s3: {
      id: 's3',
      label: 'S3 Data Lake',
      type: 'Storage Bucket',
      resource: 'aws_s3_bucket.prod_customer_data',
      exposure: 'Public read ACL enabled; unencrypted at rest',
      dependencies: 'RDS Database dumps, Customer invoices, Analytics logs',
      blastRadius: '5,000,000+ customer records',
      chokePoint: 'S3 Public Access Block',
      recommendedAction: 'Apply aws_s3_bucket_public_access_block with block_public_acls = true.',
    },
    database: {
      id: 'database',
      label: 'PostgreSQL RDS (High Target)',
      type: 'Crown Jewel Database 🔴',
      resource: 'aws_db_instance.production',
      exposure: 'Directly reachable via overprivileged SG-0a81f',
      dependencies: '4 downstream resources (RDS Subnet, App EC2, KMS Key, IAM Role)',
      blastRadius: '7 resources (Full Data Exfiltration)',
      chokePoint: 'Security Group SG-0a81f',
      recommendedAction: 'Restrict inbound CIDR to internal backend subnet; enable IAM DB Auth.',
    },
  }

  const active = nodeData[selectedNode] || nodeData.database

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Attack Path Graph &amp; Blast Radius Visualization</h2>
          <p className="scc-subtitle">
            Graph-theoretical resource dependency traversal identifying choke points and privilege escalation paths.
          </p>
        </div>
        <button
          className="btn-start-analysis"
          style={{ padding: '8px 18px', fontSize: '12.5px' }}
          onClick={() => onNavigate('remediation')}
        >
          ⚡ Remediate Primary Choke Point →
        </button>
      </div>

      <div className="attack-map-view">
        {/* Left: Visual Miniature Cyber Attack Graph */}
        <div className="attack-canvas-card">
          <div style={{ position: 'absolute', top: '16px', left: '20px', fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
            CLICK ANY NODE TO INSPECT
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '18px', marginTop: '20px', width: '100%' }}>
            {/* INTERNET */}
            <div
              className={`attack-node ${selectedNode === 'internet' ? 'selected' : ''}`}
              onClick={() => setSelectedNode('internet')}
            >
              <div style={{ fontSize: '10px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>THREAT ORIGIN</div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#F8FAFC' }}>PUBLIC INTERNET</div>
            </div>
            <div style={{ color: '#EF4444', fontSize: '14px' }}>▼</div>

            {/* LOAD BALANCER */}
            <div
              className={`attack-node ${selectedNode === 'alb' ? 'selected' : ''}`}
              onClick={() => setSelectedNode('alb')}
            >
              <div style={{ fontSize: '10px', color: '#38BDF8', fontFamily: 'JetBrains Mono' }}>INGRESS PROXY</div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#F8FAFC' }}>Load Balancer (ALB)</div>
            </div>
            <div style={{ color: '#EF4444', fontSize: '14px' }}>▼</div>

            {/* SECURITY GROUP (CHOKE POINT) */}
            <div
              className={`attack-node warning ${selectedNode === 'sg' ? 'selected' : ''}`}
              onClick={() => setSelectedNode('sg')}
              style={{ background: 'rgba(249, 115, 22, 0.12)' }}
            >
              <div style={{ fontSize: '10px', color: '#F97316', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                ⚠ CHOKE POINT
              </div>
              <div style={{ fontSize: '13.5px', fontWeight: 700, color: '#FFFFFF' }}>Security Group (SG-0a81f)</div>
            </div>
            <div style={{ color: '#F97316', fontSize: '14px' }}>▼</div>

            {/* FORK: EC2 & S3 */}
            <div style={{ display: 'flex', gap: '32px', width: '100%', justifyContent: 'center' }}>
              <div
                className={`attack-node ${selectedNode === 'ec2' ? 'selected' : ''}`}
                onClick={() => setSelectedNode('ec2')}
              >
                <div style={{ fontSize: '10px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>COMPUTE</div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>EC2 App Instance</div>
              </div>

              <div
                className={`attack-node ${selectedNode === 's3' ? 'selected' : ''}`}
                onClick={() => setSelectedNode('s3')}
              >
                <div style={{ fontSize: '10px', color: '#F59E0B', fontFamily: 'JetBrains Mono' }}>DATA STORE</div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#FFFFFF' }}>S3 Customer Bucket</div>
              </div>
            </div>

            <div style={{ color: '#EF4444', fontSize: '14px', marginLeft: '160px' }}>▼</div>

            {/* DATABASE (CROWN JEWEL) */}
            <div
              className={`attack-node critical ${selectedNode === 'database' ? 'selected' : ''}`}
              onClick={() => setSelectedNode('database')}
              style={{ marginLeft: '160px' }}
            >
              <div style={{ fontSize: '10px', color: '#EF4444', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                🔴 TARGET CROWN JEWEL
              </div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF' }}>PostgreSQL RDS DB</div>
            </div>
          </div>
        </div>

        {/* Right: Node Telemetry & Remediation Details */}
        <div className="attack-inspector-card">
          <div className="scc-panel-head">
            <div className="scc-panel-title">
              <span className="flow-node-dot"></span>
              Node Exposure Inspector
            </div>
            <span style={{ fontSize: '11px', color: '#D6A84F', fontFamily: 'JetBrains Mono' }}>
              {active.type}
            </span>
          </div>

          <div>
            <div className="inspector-section-label">TARGET RESOURCE</div>
            <div className="inspector-section-val" style={{ fontFamily: 'JetBrains Mono', color: '#D6A84F' }}>
              {active.resource}
            </div>
          </div>

          <div>
            <div className="inspector-section-label">NETWORK EXPOSURE</div>
            <div className="inspector-section-val" style={{ color: '#FCA5A5' }}>
              {active.exposure}
            </div>
          </div>

          <div>
            <div className="inspector-section-label">DEPENDENCY GRAPH</div>
            <div className="inspector-section-val">
              {active.dependencies}
            </div>
          </div>

          <div>
            <div className="inspector-section-label">BLAST RADIUS IMPACT</div>
            <div className="inspector-section-val" style={{ color: '#EF4444', fontWeight: 700 }}>
              {active.blastRadius}
            </div>
          </div>

          <div>
            <div className="inspector-section-label">CHOKE POINT STATUS</div>
            <div className="inspector-section-val" style={{ color: '#F97316', fontWeight: 600 }}>
              {active.chokePoint}
            </div>
          </div>

          <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '14px' }}>
            <div className="inspector-section-label">RECOMMENDED REMEDIATION ACTION</div>
            <div className="inspector-section-val" style={{ color: '#86EFAC', lineHeight: '1.55' }}>
              {active.recommendedAction}
            </div>
          </div>

          <button
            className="btn-start-analysis"
            style={{ width: '100%', marginTop: '10px', fontSize: '13px' }}
            onClick={() => onNavigate('remediation')}
          >
            Deploy AI Auto-Patch →
          </button>
        </div>
      </div>
    </div>
  )
}
