import React, { useState } from 'react'
import { approveEvent } from '../api/client'

const TYPE_LABELS = { '8K': 'SEC 8-K', news: 'News', industry: 'Industry' }
const TYPE_CLASSES = { '8K': 'event-type-8k', news: 'event-type-news', industry: 'event-type-industry' }

export default function EventsTimeline({ events: initialEvents, ticker }) {
  const [events, setEvents] = useState(initialEvents || [])
  const [filter, setFilter] = useState('all')

  const handleAction = async (idx, status) => {
    const ev = events[idx]
    try {
      await approveEvent(ticker, ev, status)
      setEvents(prev => prev.map((e, i) => i === idx ? { ...e, status } : e))
    } catch {}
  }

  const filtered = filter === 'all' ? events : events.filter(e => e.type === filter)

  return (
    <div className="card">
      <div className="card-title">Module 2 — Events Timeline</div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        {['all', '8K', 'news', 'industry'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`btn-sm ${filter === f ? 'btn-primary' : ''}`}
            style={filter !== f ? { background: '#e9ecef', color: '#495057' } : {}}
          >
            {f === 'all' ? 'All' : TYPE_LABELS[f] || f}
            {' '}({f === 'all' ? events.length : events.filter(e => e.type === f).length})
          </button>
        ))}
      </div>

      <div style={{ maxHeight: '420px', overflowY: 'auto' }}>
        {filtered.length === 0 && <div className="loading">No events</div>}
        {filtered.map((ev, idx) => (
          <div key={idx} className="event-row">
            <span style={{ color: '#666', fontSize: '11px' }}>{ev.date}</span>
            <span className={TYPE_CLASSES[ev.type] || ''}>{TYPE_LABELS[ev.type] || ev.type}</span>
            <span>
              {ev.url ? (
                <a href={ev.url} target="_blank" rel="noreferrer" style={{ color: '#0f3460', textDecoration: 'none' }}>
                  {ev.title}
                </a>
              ) : ev.title}
              {ev.description && (
                <div style={{ color: '#6b7a99', fontSize: '11px', marginTop: '2px' }}>
                  {ev.description.slice(0, 120)}{ev.description.length > 120 ? '…' : ''}
                </div>
              )}
            </span>
            <span style={{ display: 'flex', gap: '4px', justifyContent: 'flex-end' }}>
              {ev.status === 'pending' ? (
                <>
                  <button className="btn-sm btn-approve" onClick={() => handleAction(idx, 'approved')}>✓</button>
                  <button className="btn-sm btn-dismiss" onClick={() => handleAction(idx, 'dismissed')}>✕</button>
                </>
              ) : (
                <span style={{ fontSize: '11px', color: ev.status === 'approved' ? '#155724' : '#721c24', fontWeight: '700' }}>
                  {ev.status}
                </span>
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
