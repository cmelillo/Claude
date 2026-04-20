import React, { useState } from 'react'

const PERIODS = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025']

export default function TopBar({ onSearch, loading, ticker, period }) {
  const [inputTicker, setInputTicker] = useState(ticker || 'NVDA')
  const [inputPeriod, setInputPeriod] = useState(period || 'Q4 2024')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputTicker.trim()) onSearch(inputTicker.trim().toUpperCase(), inputPeriod)
  }

  return (
    <header style={{
      background: '#0f3460',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      gap: '24px',
      height: '60px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
    }}>
      <div style={{ color: 'white', fontWeight: 800, fontSize: '17px', letterSpacing: '-0.02em', whiteSpace: 'nowrap' }}>
        Earnings Intelligence
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', flex: 1 }}>
        <input
          value={inputTicker}
          onChange={(e) => setInputTicker(e.target.value)}
          placeholder="Ticker (e.g. NVDA)"
          style={{
            padding: '7px 12px',
            borderRadius: '5px',
            border: '1px solid rgba(255,255,255,0.3)',
            background: 'rgba(255,255,255,0.1)',
            color: 'white',
            width: '130px',
            fontSize: '14px',
            fontWeight: '600',
          }}
        />
        <select
          value={inputPeriod}
          onChange={(e) => setInputPeriod(e.target.value)}
          style={{
            padding: '7px 10px',
            borderRadius: '5px',
            border: '1px solid rgba(255,255,255,0.3)',
            background: 'rgba(255,255,255,0.1)',
            color: 'white',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          {PERIODS.map(p => <option key={p} value={p} style={{ color: '#000' }}>{p}</option>)}
        </select>
        <button
          type="submit"
          className="btn-primary"
          disabled={loading}
          style={{ background: '#e94560', color: 'white' }}
        >
          {loading ? 'Loading…' : 'Run Report'}
        </button>
      </form>
    </header>
  )
}
