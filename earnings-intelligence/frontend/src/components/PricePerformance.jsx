import React, { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend,
  CartesianGrid, ResponsiveContainer
} from 'recharts'

function mergeChartData(stock, etf) {
  const map = {}
  stock.forEach(d => { map[d.date] = { date: d.date, stock: d.normalized } })
  etf.forEach(d => { if (map[d.date]) map[d.date].etf = d.normalized })
  return Object.values(map).sort((a, b) => a.date.localeCompare(b.date))
}

function pct(n) {
  if (n == null) return '—'
  const cls = n > 0 ? 'positive' : n < 0 ? 'negative' : 'neutral'
  return <span className={cls}>{n > 0 ? '+' : ''}{n}%</span>
}

function fmt(n) {
  if (n == null) return '—'
  return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export default function PricePerformance({ data }) {
  const [tab, setTab] = useState('chart')

  if (!data) return <div className="loading">No price data</div>

  const { current_info, sector_etf, price_chart, earnings_reactions, ratings } = data
  const chartData = mergeChartData(price_chart?.stock || [], price_chart?.etf || [])
  // Use only every other data point to reduce chart density
  const sampledData = chartData.filter((_, i) => i % 2 === 0)

  return (
    <div className="card">
      <div className="card-title">Module 4 — Price Performance & Ratings</div>
      {current_info?.source === 'demo' && (
        <div className="demo-banner">Demo data</div>
      )}

      <div className="kpi-grid">
        <div className="kpi-box">
          <div className="kpi-label">Current Price</div>
          <div className="kpi-value">{fmt(current_info?.current_price)}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">52W High</div>
          <div className="kpi-value">{fmt(current_info?.week_52_high)}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">52W Low</div>
          <div className="kpi-value">{fmt(current_info?.week_52_low)}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Mean PT</div>
          <div className="kpi-value">{fmt(ratings?.consensus?.mean_price_target)}</div>
          <div className="kpi-sub">{ratings?.consensus?.pt_upside_pct != null ? `${ratings.consensus.pt_upside_pct}% upside` : ''}</div>
        </div>
        <div className="kpi-box">
          <div className="kpi-label">Consensus</div>
          <div className="kpi-value" style={{ fontSize: '14px' }}>
            <span className="positive">{ratings?.consensus?.buy}B</span>
            {' / '}
            <span className="neutral">{ratings?.consensus?.hold}H</span>
            {' / '}
            <span className="negative">{ratings?.consensus?.sell}S</span>
          </div>
        </div>
      </div>

      <div className="tab-bar">
        <button className={`tab ${tab === 'chart' ? 'active' : ''}`} onClick={() => setTab('chart')}>Price Chart (90d)</button>
        <button className={`tab ${tab === 'reactions' ? 'active' : ''}`} onClick={() => setTab('reactions')}>Post-Earnings Reactions</button>
        <button className={`tab ${tab === 'ratings' ? 'active' : ''}`} onClick={() => setTab('ratings')}>Rating Changes</button>
      </div>

      {tab === 'chart' && (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={sampledData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10 }}
              tickFormatter={d => d.slice(5)}
              interval={Math.floor(sampledData.length / 6)}
            />
            <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
            <Tooltip
              formatter={(v, name) => [`${v?.toFixed(1)}`, name === 'stock' ? data.ticker : sector_etf]}
            />
            <Legend formatter={v => v === 'stock' ? data.ticker : sector_etf} />
            <Line type="monotone" dataKey="stock" stroke="#0f3460" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="etf" stroke="#e94560" strokeWidth={1.5} dot={false} strokeDasharray="4 2" />
          </LineChart>
        </ResponsiveContainer>
      )}

      {tab === 'reactions' && (
        <table>
          <thead>
            <tr><th>Earnings Date</th><th>Prior Close</th><th>T+1</th><th>T+5</th><th>T+22</th></tr>
          </thead>
          <tbody>
            {(earnings_reactions || []).map((r, i) => (
              <tr key={i}>
                <td>{r.earnings_date}</td>
                <td>{r.prior_close ? fmt(r.prior_close) : '—'}</td>
                <td>{pct(r.t1)}</td>
                <td>{pct(r.t5)}</td>
                <td>{pct(r.t22)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {tab === 'ratings' && (
        <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
          <table>
            <thead>
              <tr><th>Date</th><th>Firm</th><th>From</th><th>To</th><th>Action</th></tr>
            </thead>
            <tbody>
              {(ratings?.changes || []).map((r, i) => (
                <tr key={i}>
                  <td>{r.date}</td>
                  <td>{r.firm}</td>
                  <td>{r.from_grade || '—'}</td>
                  <td>{r.to_grade || '—'}</td>
                  <td style={{ textTransform: 'capitalize' }}>{r.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
