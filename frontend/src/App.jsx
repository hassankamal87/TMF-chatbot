import { useState, useEffect, useCallback } from 'react'
import ChatWindow from './components/ChatWindow'
import DocumentUpload from './components/DocumentUpload'
import SettingsPanel from './components/SettingsPanel'
import { getDocuments } from './services/api'

function Toast({ toast }) {
  if (!toast) return null
  return <div className={`toast ${toast.type}`}>{toast.message}</div>
}

export default function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [documents, setDocuments] = useState([])
  const [toast, setToast] = useState(null)

  // Load documents on mount
  useEffect(() => {
    getDocuments()
      .then(setDocuments)
      .catch(() => {})
  }, [])

  // Auto-dismiss toast after 3.5s
  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }, [])

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-logo">🤖</div>
        <h1>RAG Chatbot</h1>
        <nav className="header-tabs">
          <button
            id="tab-chat"
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button
            id="tab-settings"
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ Settings
          </button>
        </nav>
      </header>

      {/* Sidebar — always visible */}
      <aside className="sidebar">
        <DocumentUpload
          documents={documents}
          setDocuments={setDocuments}
          onToast={showToast}
        />
      </aside>

      {/* Main content */}
      <main className="content">
        {activeTab === 'chat' && <ChatWindow onToast={showToast} />}
        {activeTab === 'settings' && <SettingsPanel onToast={showToast} />}
      </main>

      <Toast toast={toast} />
    </div>
  )
}
