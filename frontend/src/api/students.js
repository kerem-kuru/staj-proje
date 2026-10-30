import { api } from './client'

export const studentsApi = {
  list: (params = {}) => api.get('/students/', { params }).then((r) => r.data),
  me: () => api.get('/students/me/').then((r) => r.data),
  importCsv(file) {
    const form = new FormData()
    form.append('file', file)
    return api.post('/students/import/', form).then((r) => r.data)
  },
}
