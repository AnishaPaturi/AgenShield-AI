import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import CookieBanner from './components/common/CookieBanner.jsx'

const Console = lazy(() => import('./pages/Console.jsx'))
const Auth = lazy(() => import('./pages/Auth.jsx'))
const Profile = lazy(() => import('./pages/Profile.jsx'))
const AuthCallback = lazy(() => import('./pages/AuthCallback.jsx'))
const Legal = lazy(() => import('./pages/Legal.jsx'))
const Architecture = lazy(() => import('./pages/Architecture.jsx'))
const Security = lazy(() => import('./pages/Security.jsx'))
const NotFound = lazy(() => import('./pages/NotFound.jsx'))

export default function App() {
  return (
    <BrowserRouter>
      <CookieBanner />
      <Suspense fallback={<div className="loading-fallback" style={{ minHeight: '100vh', background: '#06080C' }} />}>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/platform-architecture" element={<Navigate to="/architecture" replace />} />
          <Route path="/security" element={<Security />} />
          <Route path="/sign-in" element={<Auth initialMode="login" />} />
          <Route path="/login" element={<Auth initialMode="login" />} />
          <Route path="/sign-up" element={<Auth initialMode="signup" />} />
          <Route path="/signup" element={<Auth initialMode="signup" />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/auth/callback/google" element={<AuthCallback />} />
          <Route path="/auth/callback/github" element={<AuthCallback />} />
          <Route path="/privacy" element={<Legal initialTab="privacy" />} />
          <Route path="/terms" element={<Legal initialTab="terms" />} />

          {/* Protected Authenticated Routes */}
          <Route
            path="/home"
            element={
              <ProtectedRoute>
                <Console initialTab="dashboard" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Console initialTab="dashboard" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Console initialTab="research" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/agents"
            element={
              <ProtectedRoute>
                <Console initialTab="pipeline" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/agents/:id"
            element={
              <ProtectedRoute>
                <Console initialTab="pipeline" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects"
            element={
              <ProtectedRoute>
                <Console initialTab="workspaces" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <ProtectedRoute>
                <Console initialTab="workspaces" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/scan"
            element={
              <ProtectedRoute>
                <Console initialTab="new-scan" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/results/:id"
            element={
              <ProtectedRoute>
                <Console initialTab="findings" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/console"
            element={
              <ProtectedRoute>
                <Console />
              </ProtectedRoute>
            }
          />

          {/* Catch-all Route: Signal Not Found */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
