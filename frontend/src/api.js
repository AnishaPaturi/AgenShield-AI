// Thin fetch wrapper around the AgentShield AI FastAPI backend.
// Every function here maps 1:1 to a route in backend/src/agentshield/api/routers/.

function base() {
  return (localStorage.getItem('agentshield_api_base') || 'http://localhost:8000').replace(/\/$/, '')
}

export function getApiBase() {
  return base()
}

export function setApiBase(url) {
  localStorage.setItem('agentshield_api_base', url.trim())
}

async function asJson(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    throw new Error(detail)
  }
  return res.json()
}

export async function checkHealth() {
  const res = await fetch(`${base()}/health`)
  if (!res.ok) throw new Error('unreachable')
  return res.json()
}

export async function listWorkspaces() {
  const res = await fetch(`${base()}/api/workspaces`)
  return asJson(res)
}

export async function getWorkspace(id) {
  const res = await fetch(`${base()}/api/workspaces/${id}`)
  return asJson(res)
}

export async function deleteWorkspace(id) {
  const res = await fetch(`${base()}/api/workspaces/${id}`, { method: 'DELETE' })
  return asJson(res)
}

export async function scanFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${base()}/api/scan`, { method: 'POST', body: form })
  return asJson(res)
}

export function exportUrl(workspaceId, fmt) {
  return `${base()}/api/workspaces/${workspaceId}/export/${fmt}`
}

export async function decidePatch(workspaceId, patchId, decision) {
  const res = await fetch(`${base()}/api/workspaces/${workspaceId}/patches/${patchId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision }),
  })
  return asJson(res)
}

export async function listAuditQueue(status = null, priority = null) {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  if (priority) params.set('priority', priority)
  const qs = params.toString() ? `?${params.toString()}` : ''
  const res = await fetch(`${base()}/api/audit-queue${qs}`)
  return asJson(res)
}

export async function getAuditQueueStats() {
  const res = await fetch(`${base()}/api/audit-queue/stats`)
  return asJson(res)
}

export async function decideAuditItem(itemId, decision, reviewer = 'security_engineer', comment = null) {
  const res = await fetch(`${base()}/api/audit-queue/${itemId}/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision, reviewer, comment }),
  })
  return asJson(res)
}

