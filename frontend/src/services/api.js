import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const sendMessage = (question) =>
  api.post('/chat', { question }).then((r) => r.data)

export const uploadDocument = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/documents/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((r) => r.data)
}

export const getDocuments = () =>
  api.get('/documents').then((r) => r.data.documents)

export const deleteDocument = (id) =>
  api.delete(`/documents/${id}`).then((r) => r.data)

export const getSettings = () =>
  api.get('/settings').then((r) => r.data)

export const saveSettings = (payload) =>
  api.post('/settings', payload).then((r) => r.data)
