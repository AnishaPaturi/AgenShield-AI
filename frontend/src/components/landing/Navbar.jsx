import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, ArrowRight, Menu, X, ExternalLink } from 'lucide-react'
import GithubIcon from './GithubIcon'
import ThemeToggle from './ThemeToggle'
import { getCurrentUser } from '../../auth.js'

export default function Navbar({ theme, setTheme, activeRoute, introStage = 'settled' }) {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [user, setUser] = useState(null)
  const location = useLocation()

  useEffect(() => {
    setUser(getCurrentUser())
    const handleAuth = () => setUser(getCurrentUser())
    window.addEventListener('auth_change', handleAuth)
    return () => window.removeEventListener('auth_change', handleAuth)
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 25) {
        setScrolled(true)
      } else {
        setScrolled(false)
      }
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    { label: 'Platform', to: '/', type: 'home' },
    { label: 'Platform Architecture', to: '/architecture', type: 'route' },
    { label: 'Security', to: '/security', type: 'route' },
    { label: 'Research', to: '/#research', hash: '#research', type: 'hash' },
  ]

  const handleNavClick = (e, link) => {
    setMobileMenuOpen(false)
    if (link.type === 'home') {
      if (location.pathname === '/') {
        e.preventDefault()
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    } else if (link.type === 'hash') {
      if (location.pathname === '/') {
        e.preventDefault()
        const target = document.querySelector(link.hash)
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }
    }
  }

  return (
    <header className={`navbar-wrapper ${scrolled ? 'navbar-scrolled' : 'navbar-top'} ${introStage === 'opening' ? 'navbar-intro-hidden' : ''}`}>
      <div className="navbar-container">
        {/* Extreme Left Anchor: Brand / Logo entering from LEFT on impact */}
        <motion.div
          className="navbar-brand-motion"
          initial={introStage === 'settled' ? false : { x: -80, opacity: 0 }}
          animate={introStage === 'opening' ? { x: -80, opacity: 0 } : { x: 0, opacity: 1 }}
          transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
        >
          <Link
            to="/"
            className="navbar-brand"
            onClick={(e) => {
              if (location.pathname === '/') {
                e.preventDefault()
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }
            }}
            aria-label="AgentShield AI Home"
          >
            <div className="brand-icon-shield">
              <Shield className="brand-shield-svg" size={19} strokeWidth={2.4} />
              <div className="brand-dot-pulse" />
            </div>
            <div className="brand-text">
              <span className="brand-name">AgentShield</span>
              <span className="brand-badge">AI</span>
            </div>
          </Link>
        </motion.div>

        {/* Center: Desktop Nav Links */}
        <motion.nav
          className="navbar-links"
          initial={introStage === 'settled' ? false : { opacity: 0, y: -8 }}
          animate={introStage === 'opening' ? { opacity: 0, y: -8 } : { opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          aria-label="Main Navigation"
        >
          {navLinks.map((link) => {
            const isActive =
              link.type === 'route'
                ? location.pathname === link.to || activeRoute === link.to.replace('/', '')
                : link.type === 'home'
                ? location.pathname === '/' && !activeRoute
                : false

            return (
              <Link
                key={link.label}
                to={link.to}
                onClick={(e) => handleNavClick(e, link)}
                className={`nav-link-item ${isActive ? 'active' : ''}`}
              >
                <span>{link.label}</span>
                <span className="nav-link-indicator" />
              </Link>
            )
          })}
        </motion.nav>

        {/* Extreme Right Anchor: GitHub + Get Started / Console */}
        <motion.div
          className="navbar-actions"
          initial={introStage === 'settled' ? false : { opacity: 0, y: -8 }}
          animate={introStage === 'opening' ? { opacity: 0, y: -8 } : { opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        >
          {/* GitHub Link */}
          <a
            href="https://github.com/AnishaPaturi/AgenShield-AI"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-github-link"
            aria-label="View on GitHub"
            title="GitHub Repository"
          >
            <GithubIcon size={16} />
            <span className="github-text">GitHub</span>
          </a>

          {/* Theme Switcher Pill (Dual-Theme: Dark ☾ / Sakura Light ☀) */}
          {setTheme && <ThemeToggle theme={theme} setTheme={setTheme} />}

          {user ? (
            <Link to="/dashboard" className="nav-launch-btn">
              <span>Console</span>
              <ArrowRight size={14} className="launch-arrow" strokeWidth={2.2} />
            </Link>
          ) : (
            <>
              <Link to="/sign-in" className="nav-github-link" style={{ textDecoration: 'none' }}>
                <span>Sign In</span>
              </Link>
              <Link to="/sign-up" className="nav-launch-btn">
                <span>Get Started</span>
                <ArrowRight size={14} className="launch-arrow" strokeWidth={2.2} />
              </Link>
            </>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label={mobileMenuOpen ? 'Close Menu' : 'Open Menu'}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </motion.div>
      </div>

      {/* Mobile Drawer Menu */}
      <div className={`mobile-nav-drawer ${mobileMenuOpen ? 'open' : ''}`}>
        <div className="mobile-drawer-content">
          <nav className="mobile-drawer-links">
            {navLinks.map((link) => {
              const isActive =
                link.type === 'route'
                  ? location.pathname === link.to || activeRoute === link.to.replace('/', '')
                  : link.type === 'home'
                  ? location.pathname === '/' && !activeRoute
                  : false

              return (
                <Link
                  key={link.label}
                  to={link.to}
                  onClick={(e) => handleNavClick(e, link)}
                  className={`mobile-drawer-item ${isActive ? 'active' : ''}`}
                >
                  {link.label}
                </Link>
              )
            })}
          </nav>

          <div className="mobile-drawer-footer">
            {setTheme && (
              <div className="mobile-theme-row">
                <span className="mobile-theme-label">Appearance</span>
                <ThemeToggle theme={theme} setTheme={setTheme} />
              </div>
            )}

            <a
              href="https://github.com/AnishaPaturi/AgenShield-AI"
              target="_blank"
              rel="noopener noreferrer"
              className="mobile-github-row"
            >
              <GithubIcon size={18} />
              <span>GitHub Repository</span>
              <ExternalLink size={14} className="external-icon" />
            </a>

            {user ? (
              <Link
                to="/dashboard"
                className="mobile-launch-btn"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span>Console Dashboard</span>
                <ArrowRight size={16} />
              </Link>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
                <Link
                  to="/sign-in"
                  className="mobile-signin-btn"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <span>Sign In</span>
                </Link>
                <Link
                  to="/sign-up"
                  className="mobile-launch-btn"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <span>Get Started</span>
                  <ArrowRight size={16} />
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
