import { api } from './client'

function asFormData(file) {
  const form = new FormData()
  form.append('file', file)
  return form
}

export const documentsApi = {
  list: (params = {}) => api.get('/documents/', { params }).then((r) => r.data),
  get: (id) => api.get(`/documents/${id}/`).then((r) => r.data),
  upload: (file) => api.post('/documents/', asFormData(file)).then((r) => r.data),
  reupload: (id, file) => api.post(`/documents/${id}/reupload/`, asFormData(file)).then((r) => r.data),
  remove: (id) => api.delete(`/documents/${id}/`),
  complete: (id) => api.post(`/documents/${id}/complete/`).then((r) => r.data),
  reject: (id, note) => api.post(`/documents/${id}/reject/`, { note }).then((r) => r.data),
  updateNote: (id, adminNote) => api.patch(`/documents/${id}/`, { admin_note: adminNote }).then((r) => r.data),

  async download(id, filename) {
    const response = await api.get(`/documents/${id}/download/`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const link = Object.assign(document.createElement('a'), { href: url, download: filename })
    link.click()
    URL.revokeObjectURL(url)
  },
}
