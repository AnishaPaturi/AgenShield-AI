import { useState } from 'react'
import { getApiBase, setApiBase } from '../api.js'

export default function Header({ healthy, onApiBaseChange }) {
  const [value, setValue] = useState(getApiBase())

  function commit() {
    setApiBase(value)
    onApiBaseChange(value)
  }

  return (
    <header>
      <div className="brand">
        <div className="mark">AS</div>
        <div>
          <h1>AgentShield AI</h1>
          <div className="sub">console · member 4</div>
        </div>
      </div>
      <div className="api-cfg">
        <span className={`dot ${healthy === null ? '' : healthy ? 'up' : 'down'}`}></span>
        <label htmlFor="apiBase">API</label>
        <input
          id="apiBase"
          type="text"
          spellCheck={false}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => e.key === 'Enter' && commit()}
        />
      </div>
    </header>
  )
}
