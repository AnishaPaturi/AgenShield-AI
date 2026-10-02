import React from 'react'

export function SkeletonLine({ width = '100%', height = '14px', style = {}, className = '' }) {
  return (
    <div
      className={`skeleton-shimmer skeleton-line ${className}`}
      style={{ width, height, ...style }}
      aria-hidden="true"
    />
  )
}

export function SkeletonCard({ height = '160px', className = '' }) {
  return (
    <div className={`skeleton-shimmer skeleton-card ${className}`} style={{ height }} aria-hidden="true">
      <div className="skeleton-header">
        <SkeletonLine width="40%" height="18px" />
        <SkeletonLine width="20%" height="18px" />
      </div>
      <div className="skeleton-body" style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <SkeletonLine width="90%" height="12px" />
        <SkeletonLine width="75%" height="12px" />
        <SkeletonLine width="60%" height="12px" />
      </div>
    </div>
  )
}

export function SkeletonRow({ cols = 4, className = '' }) {
  return (
    <div className={`skeleton-shimmer skeleton-row ${className}`} aria-hidden="true" style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${cols}, 1fr)`,
      gap: '16px',
      padding: '12px 16px',
      background: 'var(--surface-glass, rgba(20, 26, 45, 0.4))',
      borderRadius: '6px',
      border: '1px solid var(--border-subtle, rgba(255, 255, 255, 0.05))'
    }}>
      {Array.from({ length: cols }).map((_, i) => (
        <SkeletonLine key={i} width={i === 0 ? '70%' : '50%'} height="14px" />
      ))}
    </div>
  )
}

export default function SkeletonLoader({ type = 'card', count = 3, ...props }) {
  return (
    <div className="skeleton-group" role="status" aria-label="Loading content...">
      <span className="sr-only">Loading content, please wait...</span>
      {Array.from({ length: count }).map((_, i) => (
        <React.Fragment key={i}>
          {type === 'card' && <SkeletonCard {...props} />}
          {type === 'line' && <SkeletonLine {...props} />}
          {type === 'row' && <SkeletonRow {...props} />}
        </React.Fragment>
      ))}
    </div>
  )
}
