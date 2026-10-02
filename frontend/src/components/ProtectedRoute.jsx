import { useState, useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { getCurrentUser } from '../auth.js'

export default function ProtectedRoute({ children }) {
  const [user, setUser] = useState(getCurrentUser())
  const location = useLocation()

  useEffect(() => {
    const handleAuthChange = (e) => {
      setUser(e.detail || getCurrentUser())
    }
    window.addEventListener('auth_change', handleAuthChange)
    return () => window.removeEventListener('auth_change', handleAuthChange)
  }, [])

  if (!user) {
    // Save target location so user can be redirected after successful sign-in
    return <Navigate to="/sign-in" state={{ from: location }} replace />
  }

  return children
}
