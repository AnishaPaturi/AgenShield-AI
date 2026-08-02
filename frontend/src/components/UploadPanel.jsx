import { useRef, useState } from 'react'

export default function UploadPanel({ onScan, scanning }) {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  function pick(f) {
    if (!f) return
    setFile(f)
  }

  return (
    <>
      <div
        className={`upload-box ${dragging ? 'drag' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          if (e.dataTransfer.files.length) pick(e.dataTransfer.files[0])
        }}
      >
        <div className="icon">⇪</div>
        <div>Drop an IaC file<br />or click to browse</div>
        <div className="hint">.tf · .yaml · .yml · .json · .template</div>
        <input
          ref={inputRef}
          type="file"
          accept=".tf,.yaml,.yml,.json,.template"
          onChange={(e) => pick(e.target.files[0])}
        />
      </div>
      {file && <div className="filename">{file.name}</div>}
      <button
        className="primary"
        disabled={!file || scanning}
        onClick={() => onScan(file)}
      >
        {scanning ? (<><span className="spinner"></span>Scanning…</>) : 'Run scan'}
      </button>
    </>
  )
}
