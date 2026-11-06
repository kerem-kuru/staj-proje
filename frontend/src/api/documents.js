import { api } from './client'

function asFormData(file, plan) {
  const form = new FormData()
  form.append('file', file)
  form.append('plan_start', plan.start)
  form.append('plan_end', plan.end)
  plan.weekdays.forEach((day) => form.append('plan_weekdays', day))
  return form
}

export const documentsApi = {
  list: (params = {}) => api.get('/documents/', { params }).then((r) => r.data),
  get: (id) => api.get(`/documents/${id}/`).then((r) => r.data),
  upload: (file, plan) => api.post('/documents/', asFormData(file, plan)).then((r) => r.data),
  reupload: (id, file, plan) => api.post(`/documents/${id}/reupload/`, asFormData(file, plan)).then((r) => r.data),
  setEngineerDepartment: (id, department) =>
    api.post(`/documents/${id}/engineer-department/`, { engineer_department: department }).then((r) => r.data),
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
