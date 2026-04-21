import { useState, useCallback } from 'react'
import { uploadDocument, getDocuments, deleteDocument } from '../services/api'

export default function DocumentUpload({ documents, setDocuments, onToast }) {
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const handleFiles = useCallback(async (files) => {
    const file = files[0]
    if (!file) return
    setUploading(true)
    try {
      await uploadDocument(file)
      const docs = await getDocuments()
      setDocuments(docs)
      onToast(`"${file.name}" indexed successfully.`, 'success')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed.'
      onToast(msg, 'error')
    } finally {
      setUploading(false)
    }
  }, [setDocuments, onToast])

  const onInputChange = (e) => handleFiles(e.target.files)
  const onDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleDelete = async (id, name) => {
    try {
      await deleteDocument(id)
      setDocuments((prev) => prev.filter((d) => d.id !== id))
      onToast(`"${name}" removed.`, 'success')
    } catch {
      onToast('Failed to remove document.', 'error')
    }
  }

  const triggerInput = () => {
    if (!uploading) document.getElementById('file-input').click()
  }

  return (
    <div className="upload-section">
      <h2>Documents</h2>

      <div
        className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
        onClick={triggerInput}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && triggerInput()}
        aria-label="Upload document"
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf,.txt,.docx"
          onChange={onInputChange}
          disabled={uploading}
        />
        <div className="drop-zone-icon">📄</div>
        <p><span>Click to upload</span> or drag & drop</p>
        <p>PDF · TXT · DOCX</p>
      </div>

      {uploading && (
        <div className="upload-progress">
          <div className="spinner" />
          Indexing document…
        </div>
      )}

      <div className="doc-list">
        {documents.length === 0 && !uploading && (
          <p className="doc-list-empty">No documents yet.<br />Upload one to get started.</p>
        )}
        {documents.map((doc) => (
          <div key={doc.id} className="doc-item">
            <span className="doc-icon">📎</span>
            <div className="doc-info">
              <div className="doc-name" title={doc.name}>{doc.name}</div>
              <div className="doc-chunks">{doc.chunk_count} chunk{doc.chunk_count !== 1 ? 's' : ''}</div>
            </div>
            <button
              className="doc-delete"
              onClick={() => handleDelete(doc.id, doc.name)}
              title="Remove document"
              aria-label={`Remove ${doc.name}`}
            >✕</button>
          </div>
        ))}
      </div>
    </div>
  )
}
