import { useState, useEffect } from 'react'
import { getSettings, saveSettings } from '../services/api'

export default function SettingsPanel({ onToast }) {
  const [form, setForm] = useState({ llm_base_url: '', llm_token: '', llm_model: '' })
  const [status, setStatus] = useState(null)   // { type: 'success'|'error', msg }
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSettings()
      .then((data) => setForm(data))
      .catch(() => onToast('Could not load settings.', 'error'))
      .finally(() => setLoading(false))
  }, [onToast])

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setStatus(null)
    try {
      await saveSettings(form)
      setStatus({ type: 'success', msg: '✓ Settings saved — changes take effect immediately.' })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to save settings.'
      setStatus({ type: 'error', msg: `✕ ${msg}` })
    } finally {
      setSaving(false)
    }
  }

  if (loading) return null

  return (
    <div className="settings-panel">
      <h2>LLM Settings</h2>
      <p className="subtitle">
        Changes are applied instantly — no restart required.
      </p>

      <form className="settings-card" onSubmit={handleSave}>
        <div className="form-group">
          <label htmlFor="llm_base_url">API Base URL</label>
          <input
            id="llm_base_url"
            name="llm_base_url"
            type="url"
            placeholder="https://api.openai.com/v1"
            value={form.llm_base_url}
            onChange={handleChange}
            required
          />
          <span className="form-hint">
            Works with OpenAI, Azure, Ollama, LM Studio, Groq, or any OpenAI-compatible endpoint.
          </span>
        </div>

        <div className="form-group">
          <label htmlFor="llm_token">API Token</label>
          <input
            id="llm_token"
            name="llm_token"
            type="password"
            placeholder="sk-… (leave blank for local models)"
            value={form.llm_token}
            onChange={handleChange}
            autoComplete="new-password"
          />
          <span className="form-hint">Token is stored locally on the server only.</span>
        </div>

        <div className="form-group">
          <label htmlFor="llm_model">Model Name</label>
          <input
            id="llm_model"
            name="llm_model"
            type="text"
            placeholder="gpt-4o-mini"
            value={form.llm_model}
            onChange={handleChange}
            required
          />
          <span className="form-hint">
            e.g. gpt-4o-mini, gpt-4o, mistral, llama3, gemma2
          </span>
        </div>

        <button id="save-settings-btn" className="save-btn" type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save Settings'}
        </button>

        {status && (
          <div className={`settings-status ${status.type}`}>
            {status.msg}
          </div>
        )}
      </form>
    </div>
  )
}
