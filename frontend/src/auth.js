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
  {
    id: 'usr-support-003',
    name: 'AgentShield AI Admin',
    email: 'agentsheildai@gmail.com',
    password: 'Password123!',
    orgName: 'AgentShield Security',
    providers: ['email', 'google', 'github'],
    createdAt: '2026-03-01T00:00:00.000Z',
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
    // Ensure pre-seeded accounts exist in list
    for (const initUser of INITIAL_USERS) {
      if (!parsed.some((u) => u.email.toLowerCase() === initUser.email.toLowerCase())) {
        parsed.push(initUser)
      }
    }
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(parsed))
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

export async function loginWithCredentials(email, password) {
  const cleanEmail = (email || '').trim().toLowerCase()

  if (!cleanEmail) {
    throw new Error('Please enter your email address.')
  }
  if (!password) {
    throw new Error('Please enter your password.')
  }

  // 1. Attempt backend SQLite database authentication
  try {
    const { loginUserInDb } = await import('./api.js')
    const resp = await loginUserInDb(cleanEmail, password)
    if (resp && resp.user) {
      setCurrentUser(resp.user)
      // Sync locally for offline resilience
      const users = getRegisteredUsers()
      const existingIdx = users.findIndex((u) => u.email.toLowerCase() === cleanEmail)
      if (existingIdx >= 0) {
        users[existingIdx] = { ...users[existingIdx], ...resp.user, password }
      } else {
        users.push({ ...resp.user, password })
      }
      saveRegisteredUsers(users)
      return resp.user
    }
  } catch (err) {
    // If backend rejected with explicit auth error, throw it directly
    const msg = err.message || ''
    if (msg.includes('Incorrect password') || msg.includes('No account found') || msg.includes('401')) {
      throw new Error(msg.replace(/^401:\s*/, ''))
    }
    // If network connection error, continue to local storage fallback
  }

  // 2. Local storage fallback
  const users = getRegisteredUsers()
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

export async function registerWithCredentials({ name, email, password, orgName = '' }) {
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

  // Sync with backend SQLite database
  try {
    const { registerUserInDb } = await import('./api.js')
    await registerUserInDb({
      name: newUser.name,
      email: newUser.email,
      password: newUser.password,
      orgName: newUser.orgName,
      providers: 'email',
    })
  } catch {
    // Local storage acts as immediate fallback
  }

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

export async function signupWithSSO(provider, email, name = '') {
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

  // Sync with backend SQLite database
  try {
    const { registerUserInDb } = await import('./api.js')
    await registerUserInDb({
      name: newUser.name,
      email: newUser.email,
      password: '',
      orgName: '',
      providers: provider,
    })
  } catch {
    // Local storage acts as immediate fallback
  }

  return newUser
}

export async function updateUserPassword(email, newPassword, code = null) {
  const users = getRegisteredUsers()
  const cleanEmail = (email || '').trim().toLowerCase()

  if (!cleanEmail) {
    throw new Error('Please enter a valid email address.')
  }
  if (!newPassword || newPassword.length < 8) {
    throw new Error('Password must be at least 8 characters long.')
  }

  let user = users.find((u) => u.email.toLowerCase() === cleanEmail)
  if (!user) {
    // Auto-provision local user record
    const namePart = cleanEmail.split('@')[0].replace(/[._-]/g, ' ')
    user = {
      id: `usr-${Date.now()}`,
      name: namePart.charAt(0).toUpperCase() + namePart.slice(1) || 'AgentShield User',
      email: cleanEmail,
      password: newPassword,
      orgName: 'AgentShield Security',
      providers: ['email'],
      createdAt: new Date().toISOString(),
    }
    users.push(user)
  } else {
    user.password = newPassword
  }
  saveRegisteredUsers(users)

  // Sync to backend SQLite database
  try {
    const { updatePasswordInDb } = await import('./api.js')
    await updatePasswordInDb(cleanEmail, newPassword, code)
  } catch {
    // Local database updated
  }

  return user
}

export async function updateUserProfileData(email, { name, orgName, phone, avatar }) {
  const cleanEmail = (email || '').trim().toLowerCase()
  if (!cleanEmail) throw new Error('Email is required.')

  let updatedUser = null
  const users = getRegisteredUsers()
  const idx = users.findIndex((u) => u.email.toLowerCase() === cleanEmail)
  if (idx >= 0) {
    if (name !== undefined) users[idx].name = name
    if (orgName !== undefined) users[idx].orgName = orgName
    if (phone !== undefined) users[idx].phone = phone
    if (avatar !== undefined) users[idx].avatar = avatar
    updatedUser = { ...users[idx] }
    saveRegisteredUsers(users)
  }

  const cur = getCurrentUser()
  if (cur && cur.email.toLowerCase() === cleanEmail) {
    const nextCur = { ...cur }
    if (name !== undefined) nextCur.name = name
    if (orgName !== undefined) nextCur.orgName = orgName
    if (phone !== undefined) nextCur.phone = phone
    if (avatar !== undefined) nextCur.avatar = avatar
    setCurrentUser(nextCur)
    updatedUser = nextCur
  }

  // Sync to backend SQLite database
  try {
    const { updateUserProfile } = await import('./api.js')
    const res = await updateUserProfile({
      email: cleanEmail,
      name,
      org_name: orgName,
      phone,
      avatar,
    })
    if (res && res.user) {
      updatedUser = { ...updatedUser, ...res.user }
      setCurrentUser(updatedUser)
    }
  } catch (err) {
    // If backend reports explicit validation error, propagate it
    if (err.message && !err.message.includes('Failed to fetch')) {
      throw err
    }
  }

  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth_change', { detail: updatedUser }))
  }
  return updatedUser
}

export async function changeUserEmailAddress(currentEmail, newEmail, password) {
  const cleanCurrent = (currentEmail || '').trim().toLowerCase()
  const cleanNew = (newEmail || '').trim().toLowerCase()
  if (!cleanCurrent || !cleanNew) throw new Error('Both current and new email are required.')
  if (!password) throw new Error('Password is required to change email.')
  if (cleanCurrent === cleanNew) throw new Error('New email must be different from current email.')

  // Sync to backend first
  try {
    const { changeUserEmail } = await import('./api.js')
    await changeUserEmail({
      current_email: cleanCurrent,
      new_email: cleanNew,
      password,
    })
  } catch (err) {
    if (err.message && !err.message.includes('Failed to fetch')) {
      throw err
    }
  }

  const users = getRegisteredUsers()
  const user = users.find((u) => u.email.toLowerCase() === cleanCurrent)
  if (user) {
    user.email = cleanNew
    saveRegisteredUsers(users)
  }

  const cur = getCurrentUser()
  let updatedUser = cur
  if (cur && cur.email.toLowerCase() === cleanCurrent) {
    updatedUser = { ...cur, email: cleanNew }
    setCurrentUser(updatedUser)
  }

  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth_change', { detail: updatedUser }))
  }
  return updatedUser
}

export async function changeUserAccountPassword(email, currentPassword, newPassword) {
  const cleanEmail = (email || '').trim().toLowerCase()
  if (!cleanEmail) throw new Error('Email is required.')
  if (!currentPassword) throw new Error('Current password is required.')
  if (!newPassword || newPassword.length < 8) {
    throw new Error('New password must be at least 8 characters long.')
  }

  // Sync to backend SQLite database
  try {
    const { changeUserPassword } = await import('./api.js')
    await changeUserPassword({
      email: cleanEmail,
      current_password: currentPassword,
      new_password: newPassword,
    })
  } catch (err) {
    if (err.message && !err.message.includes('Failed to fetch')) {
      throw err
    }
  }

  const users = getRegisteredUsers()
  const user = users.find((u) => u.email.toLowerCase() === cleanEmail)
  if (user) {
    user.password = newPassword
    saveRegisteredUsers(users)
  }
  return true
}

export async function uploadUserAvatar(email, avatarBase64) {
  const cleanEmail = (email || '').trim().toLowerCase()
  if (!cleanEmail) throw new Error('Email is required.')

  try {
    const { uploadAvatarApi } = await import('./api.js')
    await uploadAvatarApi({ email: cleanEmail, avatar_data: avatarBase64 })
  } catch (err) {
    if (err.message && !err.message.includes('Failed to fetch')) {
      throw err
    }
  }

  return updateUserProfileData(cleanEmail, { avatar: avatarBase64 })
}

export async function removeUserAvatar(email) {
  const cleanEmail = (email || '').trim().toLowerCase()
  if (!cleanEmail) throw new Error('Email is required.')

  try {
    const { removeAvatarApi } = await import('./api.js')
    await removeAvatarApi(cleanEmail)
  } catch (err) {
    if (err.message && !err.message.includes('Failed to fetch')) {
      throw err
    }
  }

  return updateUserProfileData(cleanEmail, { avatar: null })
}

export async function unlinkAccountProvider(email, provider) {
  const cleanEmail = (email || '').trim().toLowerCase()
  const cleanProvider = (provider || '').trim().toLowerCase()
  if (!cleanEmail) throw new Error('Email is required.')
  if (!cleanProvider) throw new Error('Provider is required.')

  const { unlinkProviderApi } = await import('./api.js')
  const res = await unlinkProviderApi(cleanEmail, cleanProvider)
  const updatedUser = res.user || res

  // Sync to local registered users list
  const users = getRegisteredUsers()
  const idx = users.findIndex((u) => u.email.toLowerCase() === cleanEmail)
  if (idx >= 0) {
    users[idx] = { ...users[idx], ...updatedUser }
    saveRegisteredUsers(users)
  }

  // Update current session
  const cur = getCurrentUser()
  if (cur && cur.email.toLowerCase() === cleanEmail) {
    const nextCur = { ...cur, ...updatedUser }
    setCurrentUser(nextCur)
  }

  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth_change', { detail: updatedUser }))
  }

  return updatedUser
}

