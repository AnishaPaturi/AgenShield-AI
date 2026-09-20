// Unified Authentication & User Session Management for AgentShield AI

const USERS_STORAGE_KEY = 'agentshield_users'
const SESSION_STORAGE_KEY = 'agentshield_current_user'

// Pre-seeded registered enterprise accounts
const INITIAL_USERS = [
  {
    id: 'usr-admin-001',
    name: 'Security Admin',
    email: 'admin@agentshield.ai',
    password: 'Password123!',
    orgName: 'AgentShield Enterprise',
    providers: ['email', 'google', 'github'],
    createdAt: '2026-01-01T00:00:00.000Z',
  },
  {
    id: 'usr-alex-002',
    name: 'Alex Henderson',
    email: 'alex@company.com',
    password: 'Password123!',
    orgName: 'Acme Cloud Infrastructure',
    providers: ['email', 'github'],
    createdAt: '2026-02-01T00:00:00.000Z',
  },
]

export function getRegisteredUsers() {
  try {
    const raw = localStorage.getItem(USERS_STORAGE_KEY)
    if (!raw) {
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(INITIAL_USERS))
      return INITIAL_USERS
    }
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed) || parsed.length === 0) {
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(INITIAL_USERS))
      return INITIAL_USERS
    }
    return parsed
  } catch {
    return INITIAL_USERS
  }
}

export function saveRegisteredUsers(users) {
  localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users))
}

export function getCurrentUser() {
  try {
    const raw = localStorage.getItem(SESSION_STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setCurrentUser(user) {
  if (!user) {
    localStorage.removeItem(SESSION_STORAGE_KEY)
  } else {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(user))
  }
}

export function logout() {
  localStorage.removeItem(SESSION_STORAGE_KEY)
}

export function loginWithCredentials(email, password) {
  const users = getRegisteredUsers()
  const cleanEmail = (email || '').trim().toLowerCase()

  if (!cleanEmail) {
    throw new Error('Please enter your email address.')
  }

  const user = users.find((u) => u.email.toLowerCase() === cleanEmail)
  if (!user) {
    throw new Error('No account found with this email address. Please sign up first.')
  }

  if (user.password !== password) {
    throw new Error('Incorrect password. Please verify your credentials.')
  }

  setCurrentUser(user)
  return user
}

export function registerWithCredentials({ name, email, password, orgName = '' }) {
  const users = getRegisteredUsers()
  const cleanEmail = (email || '').trim().toLowerCase()

  if (!name || !name.trim()) {
    throw new Error('Please enter your full name.')
  }
  if (!cleanEmail) {
    throw new Error('Please enter a valid email address.')
  }
  if (!password || password.length < 8) {
    throw new Error('Password must be at least 8 characters long.')
  }

  if (users.some((u) => u.email.toLowerCase() === cleanEmail)) {
    throw new Error('An account with this email address already exists. Please sign in instead.')
  }

  const newUser = {
    id: `usr-${Date.now()}`,
    name: name.trim(),
    email: cleanEmail,
    password,
    orgName: orgName.trim(),
    providers: ['email'],
    createdAt: new Date().toISOString(),
  }

  users.push(newUser)
  saveRegisteredUsers(users)
  setCurrentUser(newUser)
  return newUser
}

export function loginWithSSO(provider, email) {
  const users = getRegisteredUsers()
  const cleanEmail = (email || '').trim().toLowerCase()
  const providerLabel = provider === 'github' ? 'GitHub' : 'Google'

  if (!cleanEmail) {
    throw new Error(`Please specify your ${providerLabel} account email.`)
  }

  const user = users.find((u) => u.email.toLowerCase() === cleanEmail)
  if (!user) {
    throw new Error(`No account found for this ${providerLabel} account (${email}). Please sign up first.`)
  }

  // Ensure provider is recorded on user
  if (!user.providers) user.providers = ['email']
  if (!user.providers.includes(provider)) {
    user.providers.push(provider)
    saveRegisteredUsers(users)
  }

  setCurrentUser(user)
  return user
}

export function signupWithSSO(provider, email, name = '') {
  const users = getRegisteredUsers()
  const cleanEmail = (email || '').trim().toLowerCase()
  const providerLabel = provider === 'github' ? 'GitHub' : 'Google'

  if (!cleanEmail) {
    throw new Error(`Please specify your ${providerLabel} account email.`)
  }

  if (users.some((u) => u.email.toLowerCase() === cleanEmail)) {
    throw new Error('An account with this email already exists. Please sign in instead.')
  }

  const newUser = {
    id: `usr-${Date.now()}`,
    name: (name || '').trim() || `${providerLabel} User`,
    email: cleanEmail,
    password: '',
    orgName: '',
    providers: [provider],
    createdAt: new Date().toISOString(),
  }

  users.push(newUser)
  saveRegisteredUsers(users)
  setCurrentUser(newUser)
  return newUser
}
