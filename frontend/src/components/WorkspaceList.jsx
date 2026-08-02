export default function WorkspaceList({ workspaces, selectedId, onSelect }) {
  if (!workspaces.length) {
    return <div className="ws-empty">No scans yet.</div>
  }

  return (
    <div>
      {workspaces.map((ws) => (
        <div
          key={ws.workspace_id}
          className={`ws-item ${ws.workspace_id === selectedId ? 'active' : ''}`}
          onClick={() => onSelect(ws.workspace_id)}
        >
          <div className="name">{ws.file_path}</div>
          <div className="meta">
            <span>{ws.risk_score != null ? `risk ${ws.risk_score}` : ws.status}</span>
            <span>{ws.total_findings != null ? `${ws.total_findings} findings` : ''}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
