import { useEffect } from 'react'

export default function Toast({ message, isError, onDone }) {
  useEffect(() => {
    if (!message) return
    const t = setTimeout(onDone, 3200)
    return () => clearTimeout(t)
  }, [message, onDone])

  return (
    <div className={`toast ${message ? 'show' : ''} ${isError ? 'err' : ''}`}>
      {message}
    </div>
  )
}
