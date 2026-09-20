import React, { useState, useMemo } from 'react'

export default function AttackPathView({ workspace, onNavigate }) {
  const findings = workspace?.report?.findings || []
  const attackGraph = workspace?.attack_graph || null

  // Build dynamic nodes from workspace attack graph or findings
  const nodeData = useMemo(() => {
    const nodes = {}

    // 1. From findings with attack_path
    findings.forEach((f) => {
      const resName = f.affected_resource || f.finding_id
      const paths = Array.isArray(f.attack_path) ? f.attack_path : []
      nodes[resName] = {
        id: resName,
        label: resName,
        type: f.severity === 'CRITICAL' ? 'Crown Jewel / Critical Risk' : 'Vulnerable Asset',
        resource: resName,
        exposure: paths.length > 0 ? paths.join(' → ') : 'Direct Misconfiguration',
        dependencies: `Associated with ${f.rule_id}`,
        blastRadius: f.blast_radius ? `${f.blast_radius} downstream assets` : 'Localized',
        chokePoint: f.requires_human_review ? 'Human Triage Required' : 'Auto-Patchable Choke Point',
        recommendedAction: f.remediation || f.remediation_hint || 'Apply recommended IaC configuration patch.',
        severity: f.severity,
      }
    })

    // 2. From attackGraph if available
    if (attackGraph && attackGraph.nodes) {
      Object.entries(attackGraph.nodes).forEach(([id, n]) => {
        if (!nodes[id]) {
          nodes[id] = {
            id,
            label: id,
            type: n.type || 'Infrastructure Node',
            resource: id,
            exposure: n.exposure || 'Internal Dependency',
            dependencies: (n.edges || []).join(', ') || 'No outbound dependencies',
            blastRadius: n.blast_radius ? `${n.blast_radius} assets` : 'Unknown',
            chokePoint: (attackGraph.choke_points || []).includes(id) ? '★ CHOKE POINT ★' : 'Standard Node',
            recommendedAction: 'Verify least-privilege resource boundaries.',
            severity: (attackGraph.choke_points || []).includes(id) ? 'HIGH' : 'MEDIUM',
          }
        }
      })
    }

    return nodes
  }, [findings, attackGraph])

  const nodeKeys = Object.keys(nodeData)
  const [selectedNode, setSelectedNode] = useState(nodeKeys[0] || null)

  const active = (selectedNode && nodeData[selectedNode]) || (nodeKeys.length > 0 ? nodeData[nodeKeys[0]] : null)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      <div className="scc-header-row">
        <div>
          <h2 className="scc-title">Attack Path Graph &amp; Blast Radius Visualization</h2>
          <p className="scc-subtitle">
            Graph-theoretical resource dependency traversal identifying choke points and privilege escalation paths.
          </p>
        </div>
        {nodeKeys.length > 0 && (
          <button
            className="btn-start-analysis"
            style={{ padding: '8px 18px', fontSize: '12.5px' }}
            onClick={() => onNavigate('remediation')}
          >
            ⚡ Remediate Primary Choke Point →
          </button>
        )}
      </div>

      {nodeKeys.length === 0 ? (
        <div className="scc-panel-card" style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
          <p style={{ fontSize: '16px', color: '#FFFFFF', marginBottom: '8px' }}>
            No Attack Path Data Available
          </p>
          <p style={{ fontSize: '13px', maxWidth: '480px', margin: '0 auto' }}>
            {workspace
              ? 'No exploitable attack paths were identified in the current workspace template.'
              : 'No workspace is currently selected. Run a scan on an IaC template to generate dynamic attack path and blast radius analysis.'}
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
        <div className="attack-map-view">
          {/* Left: Dynamic Cyber Attack Nodes */}
          <div className="attack-canvas-card">
            <div style={{ position: 'absolute', top: '16px', left: '20px', fontSize: '11px', color: '#64748B', fontFamily: 'JetBrains Mono' }}>
              CLICK ANY RESOURCE NODE TO INSPECT ({nodeKeys.length} NODES)
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '14px', marginTop: '36px', width: '100%' }}>
              {nodeKeys.map((k, idx) => {
                const node = nodeData[k]
                const isSelected = (selectedNode || nodeKeys[0]) === k
                const isCritical = node.severity === 'CRITICAL'
                const isWarning = node.severity === 'HIGH'

                return (
                  <React.Fragment key={k}>
                    <div
                      className={`attack-node ${isCritical ? 'critical' : isWarning ? 'warning' : ''} ${isSelected ? 'selected' : ''}`}
                      onClick={() => setSelectedNode(k)}
                      style={{ cursor: 'pointer', maxWidth: '340px', width: '90%' }}
                    >
                      <div style={{ fontSize: '10px', color: isCritical ? '#EF4444' : isWarning ? '#F97316' : '#38BDF8', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>
                        {node.type.toUpperCase()}
                      </div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: '#F8FAFC', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {node.label}
                      </div>
                    </div>
                    {idx < nodeKeys.length - 1 && (
                      <div style={{ color: isCritical ? '#EF4444' : '#F97316', fontSize: '14px' }}>▼</div>
                    )}
                  </React.Fragment>
                )
              })}
            </div>
          </div>

          {/* Right: Node Telemetry & Remediation Details */}
          {active && (
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
                <div className="inspector-section-label">NETWORK EXPOSURE / ATTACK ROUTE</div>
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
          )}
        </div>
      )}
    </div>
  )
}
