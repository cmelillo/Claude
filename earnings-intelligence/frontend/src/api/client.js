const BASE = '/api'

export async function fetchReport(ticker, period) {
  const res = await fetch(`${BASE}/report/${ticker}?period=${encodeURIComponent(period)}`)
  if (!res.ok) throw new Error(`Report fetch failed: ${res.status}`)
  return res.json()
}

export async function fetchPrice(ticker) {
  const res = await fetch(`${BASE}/price/${ticker}`)
  if (!res.ok) throw new Error(`Price fetch failed: ${res.status}`)
  return res.json()
}

export async function fetchFilings(ticker) {
  const res = await fetch(`${BASE}/filings/${ticker}`)
  if (!res.ok) throw new Error(`Filings fetch failed: ${res.status}`)
  return res.json()
}

export async function fetchEvents(ticker) {
  const res = await fetch(`${BASE}/events/${ticker}`)
  if (!res.ok) throw new Error(`Events fetch failed: ${res.status}`)
  return res.json()
}

export async function fetchRatings(ticker) {
  const res = await fetch(`${BASE}/ratings/${ticker}`)
  if (!res.ok) throw new Error(`Ratings fetch failed: ${res.status}`)
  return res.json()
}

export async function approveEvent(ticker, event, status = 'approved') {
  const res = await fetch(`${BASE}/events/${ticker}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event, status }),
  })
  if (!res.ok) throw new Error(`Approve failed: ${res.status}`)
  return res.json()
}

export async function uploadResearch(ticker, file) {
  const fd = new FormData()
  fd.append('ticker', ticker)
  fd.append('file', file)
  const res = await fetch(`${BASE}/research/upload`, { method: 'POST', body: fd })
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
  return res.json()
}

export async function fetchResearchDocs(ticker) {
  const res = await fetch(`${BASE}/research/${ticker}`)
  if (!res.ok) throw new Error(`Research fetch failed: ${res.status}`)
  return res.json()
}

export function streamSynthesis(ticker, period, onChunk, onDone, onError) {
  const url = `${BASE}/report/${ticker}/stream?period=${encodeURIComponent(period)}`
  const es = new EventSource(url)
  es.onmessage = (e) => {
    if (e.data === '[DONE]') {
      es.close()
      onDone?.()
      return
    }
    try {
      const parsed = JSON.parse(e.data)
      if (parsed.error) {
        es.close()
        onError?.(parsed.error)
      } else {
        onChunk?.(parsed.chunk)
      }
    } catch {}
  }
  es.onerror = () => {
    es.close()
    onError?.('Stream connection lost')
  }
  return es
}

export async function downloadPDF(ticker, period) {
  const res = await fetch(`${BASE}/report/${ticker}/pdf?period=${encodeURIComponent(period)}`)
  if (!res.ok) throw new Error('PDF generation failed')
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${ticker}_${period.replace(/ /g, '_')}_report.pdf`
  a.click()
  URL.revokeObjectURL(url)
}
