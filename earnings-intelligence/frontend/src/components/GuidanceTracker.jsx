import React from 'react'

export default function GuidanceTracker({ data }) {
  if (!data) return <div className="loading">No guidance data</div>

  const { summary, quarters } = data
  const styleClass = `tag-${(summary.guidance_style || 'unknown').replace('-', '-')}`

  return (
    <div className="card">
      <div className="card-title">Module 3 — Guidance Tracker</div>
      {data.source === 'demo' && (
        <div className="demo-banner">Demo data</div>
      )}

      <div className="kpi-grid">
        <div className="kpi-box">
          <div className="kpi-label">Beat Rate</div>
          <div className="kpi-value">{summary.beat_rate ?? '—'}{summary.beat_rate != null ? '%' : ''}</div>
          <div className="kpi-sub">{summary.beat_count}/{summary.quarters_analyzed} quarters</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Avg Beat</div>
          <div className="kpi-value" style={{ fontSize: '18px' }}>
            {summary.avg_beat_magnitude_pct != null
              ? <span className={summary.avg_beat_magnitude_pct >= 0 ? 'positive' : 'negative'}>
                  {summary.avg_beat_magnitude_pct > 0 ? '+' : ''}{summary.avg_beat_magnitude_pct}%
                </span>
              : '—'}
          </div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Guidance Style</div>
          <div className={`kpi-value ${styleClass}`} style={{ fontSize: '16px', textTransform: 'capitalize' }}>
            {summary.guidance_style || '—'}
          </div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>EPS Actual</th>
            <th>EPS Estimate</th>
            <th>Beat %</th>
            <th>Rev Guided</th>
          </tr>
        </thead>
        <tbody>
          {(quarters || []).map((q, i) => (
            <tr key={i}>
              <td>{q.date}</td>
              <td>{q.eps_actual ?? '—'}</td>
              <td>{q.eps_estimate ?? '—'}</td>
              <td>
                {q.eps_beat_pct != null ? (
                  <span className={q.eps_beat_pct > 0 ? 'positive' : 'negative'}>
                    {q.eps_beat_pct > 0 ? '+' : ''}{q.eps_beat_pct}%
                  </span>
                ) : '—'}
              </td>
              <td>
                {q.revenue_guided_low != null
                  ? `$${(q.revenue_guided_low / 1e9).toFixed(1)}B – $${(q.revenue_guided_high / 1e9).toFixed(1)}B`
                  : <span style={{ color: '#aaa' }}>N/A</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
