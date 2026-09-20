import React, { useRef, useState } from 'react'

export default function NewScanView({ onScan, scanning, onNavigate }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [cloudTarget, setCloudTarget] = useState('AWS')
  const [scanMode, setScanMode] = useState('full')
  const inputRef = useRef(null)

  const handlePick = (f) => {
    if (!f) return
    setFile(f)
  }

  const handleStartScan = () => {
    if (!file) {
      inputRef.current?.click()
      return
    }
    if (onScan) {
      onScan(file, { cloud: cloudTarget, mode: scanMode })
    }
  }

  return (
    <div className="newscan-view">
      {/* Hero */}
      <div className="newscan-hero">
        <h2>Secure your infrastructure before it reaches production.</h2>
        <p>
          Analyze Terraform, CloudFormation, Kubernetes and Helm configurations using autonomous
          AI security agents with runtime LocalStack sandbox verification.
        </p>
      </div>

      {/* Huge Dropzone */}
      <div
        className={`huge-dropzone ${dragging ? 'drag-active' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          if (e.dataTransfer.files.length) handlePick(e.dataTransfer.files[0])
        }}
      >
        <div className="huge-dropzone-icon">⬆</div>
        <div className="huge-dropzone-title">DROP IaC FILES HERE</div>
        <div className="huge-dropzone-sub">or click to browse from your computer</div>

        <div className="iac-format-pills">
          <span className="iac-pill">Terraform (.tf)</span>
          <span className="iac-pill">CloudFormation (.yaml / .json)</span>
          <span className="iac-pill">Kubernetes (.yaml)</span>
          <span className="iac-pill">Helm (values.yaml / chart)</span>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".tf,.yaml,.yml,.json,.template,.tgz"
          onChange={(e) => handlePick(e.target.files[0])}
        />
      </div>

      {/* Selected File Notice */}
      {file && (
        <div className="filename" style={{ textAlign: 'center', margin: '0 auto', maxWidth: '480px' }}>
          Selected IaC Template: <b>{file.name}</b> ({(file.size / 1024).toFixed(1)} KB)
        </div>
      )}

      {/* Options: Cloud Target & Scan Mode */}
      <div className="newscan-options-card">
        <div>
          <div className="control-section-title">Cloud Target</div>
          <div className="cloud-target-pills">
            <button
              type="button"
              className={`cloud-target-btn ${cloudTarget === 'AWS' ? 'active' : ''}`}
              onClick={() => setCloudTarget('AWS')}
            >
              <span>☁</span> AWS
            </button>
            <button
              type="button"
              className={`cloud-target-btn ${cloudTarget === 'Azure' ? 'active' : ''}`}
              onClick={() => setCloudTarget('Azure')}
            >
              <span>☁</span> Azure
            </button>
            <button
              type="button"
              className={`cloud-target-btn ${cloudTarget === 'GCP' ? 'active' : ''}`}
              onClick={() => setCloudTarget('GCP')}
            >
              <span>☁</span> GCP
            </button>
          </div>
        </div>

        <div>
          <div className="control-section-title">Scan Mode</div>
          <div className="scan-mode-radio-group">
            <label className="scan-mode-option">
              <input
                type="radio"
                name="scanMode"
                value="quick"
                checked={scanMode === 'quick'}
                onChange={() => setScanMode('quick')}
              />
              <span className="scan-mode-title">Quick Scan</span>
              <span className="scan-mode-desc">— Static AST syntax & secret scanner validation (Fastest, ~300ms)</span>
            </label>

            <label className="scan-mode-option">
              <input
                type="radio"
                name="scanMode"
                value="full"
                checked={scanMode === 'full'}
                onChange={() => setScanMode('full')}
              />
              <span className="scan-mode-title">Full AgentShield Analysis (Recommended)</span>
              <span className="scan-mode-desc">
                — 8 coordinated agents: AST, Secrets, RAG, Dual-LLM Consensus, Diff Synthesis & LocalStack Sandbox
              </span>
            </label>

            <label className="scan-mode-option">
              <input
                type="radio"
                name="scanMode"
                value="compliance"
                checked={scanMode === 'compliance'}
                onChange={() => setScanMode('compliance')}
              />
              <span className="scan-mode-title">Compliance Audit</span>
              <span className="scan-mode-desc">— SOC 2, HIPAA, PCI-DSS, and NIST 800-53 benchmark enforcement</span>
            </label>
          </div>
        </div>

        {/* Start Security Analysis CTA */}
        <button
          className="btn-start-analysis"
          onClick={handleStartScan}
          disabled={scanning}
        >
          {scanning ? (
            <>
              <span className="spinner"></span>
              Orchestrating 8 AI Agents...
            </>
          ) : (
            'START SECURITY ANALYSIS →'
          )}
        </button>
      </div>
    </div>
  )
}
