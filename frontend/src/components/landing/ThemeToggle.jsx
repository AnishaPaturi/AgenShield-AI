import { Sun, Moon } from 'lucide-react'

export default function ThemeToggle({ theme, setTheme }) {
  const isLight = theme === 'light'
  const isDark = theme === 'dark'

  return (
    <div
      className="theme-switcher-pill theme-toggle"
      data-testid="landing-theme-toggle"
      role="radiogroup"
      aria-label="Theme Switcher: Dark or Light Mode"
    >
      {/* Sliding Active Highlight Indicator */}
      <div
        className={`theme-indicator-slide ${isDark ? 'position-dark' : 'position-light'}`}
        aria-hidden="true"
      />

      {/* Sun Button (Light Mode) */}
      <button
        type="button"
        role="radio"
        aria-checked={isLight}
        onClick={() => setTheme('light')}
        className={`theme-segment-btn ${isLight ? 'is-active' : ''}`}
        aria-label="Light Mode"
        title="Light Mode (☀)"
      >
        <Sun
          className="theme-segment-icon sun-icon"
          size={14}
          strokeWidth={2.3}
        />
        <span className="sr-only">Light Mode</span>
      </button>

      {/* Divider */}
      <div className="theme-segment-divider" aria-hidden="true" />

      {/* Moon Button (Dark Mode) */}
      <button
        type="button"
        role="radio"
        aria-checked={isDark}
        onClick={() => setTheme('dark')}
        className={`theme-segment-btn ${isDark ? 'is-active' : ''}`}
        aria-label="Dark Mode"
        title="Dark Mode (☾)"
      >
        <Moon
          className="theme-segment-icon moon-icon"
          size={14}
          strokeWidth={2.3}
        />
        <span className="sr-only">Dark Mode</span>
      </button>
    </div>
  )
}
