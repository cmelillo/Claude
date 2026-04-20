import React, { useState, useRef, useEffect } from 'react'
import { uploadResearch, fetchResearchDocs } from '../api/client'

export default function ResearchUpload({ ticker }) {
  const [docs, setDocs] = useState([])
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [status, setStatus] = useState(null)
  const inputRef = useRef()

  useEffect(() => {
    if (ticker) {
      fetchResearchDocs(ticker).then(d => setDocs(d.docs || [])).catch(() => {})
    }
  }, [ticker])

  const doUpload = async (file) => {
    if (!file || !file.name.endsWith('.pdf')) {
      setStatus({ error: 'Only PDF files are accepted.' })
      return
    }
    setUploading(true)
    setStatus(null)
    try {
      const result = await uploadResearch(ticker, file)
      setStatus({ ok: `Uploaded "${result.filename}" (${result.chars.toLocaleString()} chars extracted)` })
      const d = await fetchResearchDocs(ticker)
      setDocs(d.docs || [])
    } catch (e) {
      setStatus({ error: e.message })
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) doUpload(file)
  }

  return (
    <div className="card">
      <div className="card-title">Research Store — {ticker}</div>

      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={(e) => doUpload(e.target.files[0])}
        />
        {uploading ? '⏳ Uploading…' : 'Drop PDF here or click to upload analyst report'}
      </div>

      {status?.ok && <div style={{ color: '#155724', fontSize: '12px', marginTop: '8px' }}>✓ {status.ok}</div>}
      {status?.error && <div className="error-msg" style={{ marginTop: '8px' }}>{status.error}</div>}

      {docs.length > 0 && (
        <div style={{ marginTop: '14px' }}>
          <h3>Uploaded Reports</h3>
          <table>
            <thead><tr><th>Filename</th><th>Date</th><th>Preview</th></tr></thead>
            <tbody>
              {docs.map(d => (
                <tr key={d.id}>
                  <td>{d.filename}</td>
                  <td>{d.upload_date?.slice(0, 10)}</td>
                  <td style={{ fontSize: '11px', color: '#6b7a99', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {d.text_snippet}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
