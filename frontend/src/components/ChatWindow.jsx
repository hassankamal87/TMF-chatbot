import { useState, useRef, useEffect, useCallback } from 'react'
import { sendMessage } from '../services/api'

function TypingIndicator() {
  return (
    <div className="message-row assistant">
      <div className="typing-indicator">
        <div className="typing-dot" />
        <div className="typing-dot" />
        <div className="typing-dot" />
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">{message.content}</div>
      {!isUser && message.sources?.length > 0 && (
        <div className="sources">
          {message.sources.map((s, i) => (
            <div key={i} className="source-chip">
              📎 {s.document_name}
              <div className="source-tooltip">{s.chunk_preview}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function ChatWindow({ onToast }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = useCallback(async () => {
    const question = input.trim()
    if (!question || loading) return

    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const data = await sendMessage(question)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong. Check your LLM settings.'
      onToast(msg, 'error')
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `⚠️ ${msg}`, sources: [] },
      ])
    } finally {
      setLoading(false)
    }
  }, [input, loading, onToast])

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-window">
      <div className="messages-area">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-icon">🤖</div>
            <h2>RAG Chatbot</h2>
            <p>Upload documents in the sidebar, then ask me anything about them.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <textarea
          ref={textareaRef}
          id="chat-input"
          rows={1}
          placeholder="Ask a question about your documents… (Enter to send)"
          value={input}
          onChange={(e) => {
            setInput(e.target.value)
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px'
          }}
          onKeyDown={onKeyDown}
          disabled={loading}
        />
        <button
          id="send-btn"
          className="send-btn"
          onClick={handleSend}
          disabled={!input.trim() || loading}
          aria-label="Send message"
        >
          ➤
        </button>
      </div>
    </div>
  )
}
