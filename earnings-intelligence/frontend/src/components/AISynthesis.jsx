import React, { useState, useRef } from 'react'
import { streamSynthesis } from '../api/client'

export default function AISynthesis({ ticker, period }) {
  const [text, setText] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState(null)
  const esRef = useRef(null)

  const start = () => {
    if (streaming) return
    setText('')
    setDone(false)
    setError(null)
    setStreaming(true)

    esRef.current = streamSynthesis(
      ticker,
      period,
      (chunk) => setText(prev => prev + chunk),
      () => { setStreaming(false); setDone(true) },
      (err) => { setStreaming(false); setError(err) },
    )
  }

  const stop = () => {
    esRef.current?.close()
    setStreaming(false)
  }

  return (
    <div className="card">
      <div className="card-title">Module 5 — AI Synthesis</div>

      <div style={{ marginBottom: '12px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        <button
          className="btn-primary"
          onClick={start}
          disabled={streaming}
          style={{ minWidth: '140px' }}
        >
          {streaming ? 'Streaming…' : done ? 'Regenerate' : 'Generate Synthesis'}
        </button>
        {streaming && (
          <button onClick={stop} style={{ background: '#f8d7da', color: '#721c24', padding: '9px 16px', borderRadius: '5px' }}>
            Stop
          </button>
        )}
        <span style={{ fontSize: '11px', color: '#6b7a99' }}>
          Uses claude-sonnet-4-6 · Powered by Anthropic
        </span>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {(text || streaming) && (
        <div className={`synthesis-text ${streaming && !done ? 'stream-cursor' : ''}`}>
          {text || <span style={{ color: '#aaa' }}>Waiting for response…</span>}
        </div>
      )}

      {!text && !streaming && !error && (
        <div style={{ color: '#6b7a99', fontSize: '13px', padding: '12px 0' }}>
          Click "Generate Synthesis" to produce an AI-powered analysis of all 4 prior modules for {ticker} {period}.
        </div>
      )}
    </div>
  )
}
