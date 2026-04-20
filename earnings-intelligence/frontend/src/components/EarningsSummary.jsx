import React from 'react'

function fmt(n, prefix = '') {
  if (n == null) return '—'
  if (Math.abs(n) >= 1e9) return prefix + (n / 1e9).toFixed(2) + 'B'
  if (Math.abs(n) >= 1e6) return prefix + (n / 1e6).toFixed(1) + 'M'
  return prefix + n.toLocaleString()
}

function pct(n) {
  if (n == null) return '—'
  const cls = n > 0 ? 'positive' : n < 0 ? 'negative' : 'neutral'
  return <span className={cls}>{n > 0 ? '+' : ''}{n}%</span>
}

function BadgeEl({ badge }) {
  const map = { Beat: 'beat', Miss: 'miss', 'In Line': 'inline', 'N/A': 'na' }
  return <span className={`badge badge-${map[badge] || 'na'}`}>{badge}</span>
}

export default function EarningsSummary({ data }) {
  if (!data) return <div className="loading">No earnings data</div>

  const { eps, revenue, margins, guidance } = data

  return (
    <div className="card">
      <div className="card-title">Module 1 — Earnings Summary</div>
      {data.source === 'demo' && (
        <div className="demo-banner">Demo data — connect to live data sources in production</div>
      )}

      <div className="kpi-grid">
        <div className="kpi-box">
          <div className="kpi-label">EPS Actual</div>
          <div className="kpi-value">{eps?.actual ?? '—'}</div>
          <div className="kpi-sub">Est: {eps?.estimate ?? '—'}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">EPS Surprise</div>
          <div className="kpi-value" style={{ fontSize: '16px' }}>
            {eps?.surprise_pct != null ? pct(eps.surprise_pct) : '—'}
          </div>
          <div className="kpi-sub"><BadgeEl badge={eps?.badge || 'N/A'} /></div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Revenue</div>
          <div className="kpi-value">{fmt(revenue?.actual, '$')}</div>
          <div className="kpi-sub">Est: {fmt(revenue?.estimate, '$')}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Revenue YoY</div>
          <div className="kpi-value" style={{ fontSize: '18px' }}>{pct(revenue?.yoy_pct)}</div>
          <div className="kpi-sub">QoQ: {pct(revenue?.qoq_pct)}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Gross Margin</div>
          <div className="kpi-value">{margins?.gross_margin_pct ?? '—'}{margins?.gross_margin_pct != null ? '%' : ''}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Op. Margin</div>
          <div className="kpi-value">{margins?.operating_margin_pct ?? '—'}{margins?.operating_margin_pct != null ? '%' : ''}</div>
        </div>
      </div>

      {guidance && (guidance.next_quarter_revenue_low || guidance.next_quarter_revenue_high) && (
        <div style={{ marginTop: '12px' }}>
          <h3>Guidance — Next Quarter</h3>
          <div style={{ display: 'flex', gap: '16px', fontSize: '13px' }}>
            <span>Revenue: {fmt(guidance.next_quarter_revenue_low, '$')} – {fmt(guidance.next_quarter_revenue_high, '$')}</span>
            {guidance.next_quarter_eps_low && (
              <span>EPS: {guidance.next_quarter_eps_low} – {guidance.next_quarter_eps_high}</span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
