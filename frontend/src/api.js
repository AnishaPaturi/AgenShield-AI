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

export async function scanDrift(workspaceId) {
  const res = await fetch(`${base()}/api/workspaces/${workspaceId}/drift/scan`, {
    method: 'POST',
  })
  return asJson(res)
}

export async function getDrift(workspaceId) {
  const res = await fetch(`${base()}/api/workspaces/${workspaceId}/drift`)
  return asJson(res)
}

export async function getFeedbackStats() {
  const res = await fetch(`${base()}/api/feedback/stats`)
  return asJson(res)
}

export async function verifyEmailInDb(email) {
  const res = await fetch(`${base()}/api/auth/verify-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  return asJson(res)
}

export async function sendVerificationCodeApi(email) {
  const res = await fetch(`${base()}/api/auth/send-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  return asJson(res)
}

export async function verifyCodeApi(email, code) {
  const res = await fetch(`${base()}/api/auth/verify-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code }),
  })
  return asJson(res)
}

export async function registerUserInDb({ name, email, password = '', orgName = '', providers = 'email' }) {
  const res = await fetch(`${base()}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name,
      email,
      password,
      org_name: orgName,
      providers,
    }),
  })
  return asJson(res)
}

export async function updatePasswordInDb(email, newPassword, code = null) {
  const res = await fetch(`${base()}/api/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, new_password: newPassword, code }),
  })
  return asJson(res)
}


export async function getGitHubOAuthStatus() {
  try {
    const res = await fetch(`${base()}/api/auth/github/status`)
    return await asJson(res)
  } catch {
    return { configured: false }
  }
}

export function getGitHubLoginUrl(options = {}) {
  const params = new URLSearchParams()
  if (options.return_to) params.set('return_to', options.return_to)
  if (options.link_email) params.set('link_email', options.link_email)
  const qs = params.toString() ? `?${params.toString()}` : ''
  return `${base()}/api/auth/github/login${qs}`
}

export async function getGoogleOAuthStatus() {
  try {
    const res = await fetch(`${base()}/api/auth/google/status`)
    return await asJson(res)
  } catch {
    return { configured: false }
  }
}

export function getGoogleLoginUrl(options = {}) {
  const params = new URLSearchParams()
  if (options.return_to) params.set('return_to', options.return_to)
  if (options.link_email) params.set('link_email', options.link_email)
  const qs = params.toString() ? `?${params.toString()}` : ''
  return `${base()}/api/auth/google/login${qs}`
}

export async function unlinkProviderApi(email, provider) {
  const res = await fetch(`${base()}/api/auth/unlink-provider`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, provider }),
  })
  return asJson(res)
}

export async function exchangeOAuthCode(provider, code, redirectUri = null) {
  const res = await fetch(`${base()}/api/auth/${provider}/exchange`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, redirect_uri: redirectUri }),
  })
  return asJson(res)
}

export async function loginUserInDb(email, password) {
  const res = await fetch(`${base()}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  return asJson(res)
}

export async function getUserProfile(email) {
  const res = await fetch(`${base()}/api/auth/profile?email=${encodeURIComponent(email)}`)
  return asJson(res)
}

export async function updateUserProfile({ email, name, phone, org_name, avatar }) {
  const res = await fetch(`${base()}/api/auth/profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name, phone, org_name, avatar }),
  })
  return asJson(res)
}

export async function changeUserEmail({ current_email, new_email, password }) {
  const res = await fetch(`${base()}/api/auth/change-email`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_email, new_email, password }),
  })
  return asJson(res)
}

export async function changeUserPassword({ email, current_password, new_password }) {
  const res = await fetch(`${base()}/api/auth/change-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, current_password, new_password }),
  })
  return asJson(res)
}

export async function uploadAvatarApi({ email, avatar_data }) {
  const res = await fetch(`${base()}/api/auth/avatar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, avatar_data }),
  })
  return asJson(res)
}

export async function removeAvatarApi(email) {
  const res = await fetch(`${base()}/api/auth/avatar?email=${encodeURIComponent(email)}`, {
    method: 'DELETE',
  })
  return asJson(res)
}

export async function validatePatchApi(workspaceId, patchId) {
  const res = await fetch(`${base()}/api/workspaces/${workspaceId}/patches/${patchId}/validate`, {
    method: 'POST',
  })
  return asJson(res)
}

export async function validateAllPatchesApi(workspaceId) {
  const res = await fetch(`${base()}/api/workspaces/${workspaceId}/validate-patches`, {
    method: 'POST',
  })
  return asJson(res)
}
