import React, { useState, useCallback } from 'react'
import TopBar from './components/TopBar'
import EarningsSummary from './components/EarningsSummary'
import EventsTimeline from './components/EventsTimeline'
import GuidanceTracker from './components/GuidanceTracker'
import PricePerformance from './components/PricePerformance'
import AISynthesis from './components/AISynthesis'
import ResearchUpload from './components/ResearchUpload'
import { fetchReport, downloadPDF } from './api/client'

export default function App() {
  const [ticker, setTicker] = useState('NVDA')
  const [period, setPeriod] = useState('Q4 2024')
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pdfLoading, setPdfLoading] = useState(false)

  const runReport = useCallback(async (t, p) => {
    setTicker(t)
    setPeriod(p)
    setLoading(true)
    setError(null)
    setReport(null)
    try {
      const data = await fetchReport(t, p)
      setReport(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const handlePDF = async () => {
    setPdfLoading(true)
    try {
      await downloadPDF(ticker, period)
    } catch (e) {
      alert('PDF generation failed: ' + e.message)
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <TopBar onSearch={runReport} loading={loading} ticker={ticker} period={period} />

      <main style={{ flex: 1, padding: '20px 24px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        {!report && !loading && (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: '#6b7a99',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
            <h2 style={{ fontSize: '20px', color: '#0f3460', marginBottom: '8px' }}>Earnings Intelligence</h2>
            <p style={{ marginBottom: '24px' }}>
              Enter a ticker and earnings period above, then click <strong>Run Report</strong> to generate a full 5-module earnings analysis.
            </p>
            <button
              className="btn-primary"
              style={{ fontSize: '14px', padding: '10px 24px' }}
              onClick={() => runReport('NVDA', 'Q4 2024')}
            >
              Try NVDA Q4 2024 (Demo)
            </button>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: 'center', padding: '60px', color: '#6b7a99' }}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>⏳</div>
            <p>Fetching data for <strong>{ticker}</strong> — assembling all 5 modules…</p>
          </div>
        )}

        {error && (
          <div className="error-msg" style={{ margin: '20px 0' }}>
            Error: {error}
          </div>
        )}

        {report && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h2 style={{ fontSize: '22px', marginBottom: '2px' }}>{ticker} — {period}</h2>
                <div style={{ fontSize: '12px', color: '#6b7a99' }}>
                  Generated {new Date(report.generated_at).toLocaleString()}
                </div>
              </div>
              <button
                className="btn-primary"
                onClick={handlePDF}
                disabled={pdfLoading}
                style={{ fontSize: '13px' }}
              >
                {pdfLoading ? 'Generating…' : '⬇ Download PDF'}
              </button>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(600px, 1fr))',
              gap: '0',
            }}>
              <div>
                <EarningsSummary data={report.earnings_summary} />
                <GuidanceTracker data={report.guidance_tracker} />
                <ResearchUpload ticker={ticker} />
              </div>
              <div>
                <PricePerformance data={report.price_performance} />
                <EventsTimeline events={report.events_timeline} ticker={ticker} />
              </div>
            </div>

            <AISynthesis ticker={ticker} period={period} />
          </>
        )}
      </main>

      <footer style={{
        background: '#0f3460',
        color: 'rgba(255,255,255,0.5)',
        textAlign: 'center',
        padding: '10px',
        fontSize: '11px',
      }}>
        Earnings Intelligence · Public data sources · Demo mode active in restricted environments
      </footer>
    </div>
  )
}
