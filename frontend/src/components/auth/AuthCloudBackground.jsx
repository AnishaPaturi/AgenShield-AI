import React, { useRef, useEffect, useState } from 'react'

export default function AuthCloudBackground() {
  const videoRef = useRef(null)
  const [videoLoaded, setVideoLoaded] = useState(false)

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(() => {
        // Autoplay fallback (video is muted)
      })
    }
  }, [])

  return (
    <div className="auth-cloud-video-wrapper" aria-hidden="true">
      <video
        ref={videoRef}
        className={`auth-cloud-video ${videoLoaded ? 'loaded' : ''}`}
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        onLoadedData={() => setVideoLoaded(true)}
      >
        <source src="/videos/cloud-background.mp4" type="video/mp4" />
        <source src="/videos/cloud.mp4" type="video/mp4" />
      </video>

      {/* Subtle deep navy & twilight ambient tint ensuring natural cloud depth & contrast */}
      <div className="auth-cloud-ambient-overlay" />
    </div>
  )
}
