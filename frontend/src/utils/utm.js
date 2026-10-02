/**
 * UTM Parameter Tracking Utility
 * Lightweight, privacy-conscious parameter preservation.
 * Stores UTM parameters in sessionStorage without collecting personal data.
 */

const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
const STORAGE_KEY = 'agentshield_utm_params'

/**
 * Captures UTM parameters from current URL and persists to sessionStorage.
 */
export function captureUtmParams() {
  if (typeof window === 'undefined') return {}
  try {
    const params = new URLSearchParams(window.location.search)
    const utmData = {}
    let hasUtm = false

    UTM_KEYS.forEach((key) => {
      const val = params.get(key)
      if (val) {
        // Sanitize: alphanumeric, dashes, underscores, dots only (max 100 chars)
        const sanitized = val.replace(/[^a-zA-Z0-9_\-\.]/g, '').slice(0, 100)
        if (sanitized) {
          utmData[key] = sanitized
          hasUtm = true
        }
      }
    })

    if (hasUtm) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(utmData))
      return utmData
    }

    const stored = sessionStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

/**
 * Retrieves currently stored UTM parameters.
 */
export function getStoredUtmParams() {
  if (typeof window === 'undefined') return {}
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

/**
 * Appends captured UTM parameters to an internal target link.
 */
export function appendUtmParams(targetUrl) {
  const utm = getStoredUtmParams()
  if (!utm || Object.keys(utm).length === 0) return targetUrl

  try {
    const isRelative = !targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')
    const dummyBase = 'http://localhost'
    const parsed = new URL(targetUrl, dummyBase)

    Object.entries(utm).forEach(([k, v]) => {
      if (!parsed.searchParams.has(k)) {
        parsed.searchParams.set(k, v)
      }
    })

    if (isRelative) {
      return parsed.pathname + parsed.search + parsed.hash
    }
    return parsed.toString()
  } catch {
    return targetUrl
  }
}
