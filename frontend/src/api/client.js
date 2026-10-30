import axios from 'axios'
import { tokenStorage } from './tokenStorage'

const baseURL = import.meta.env.VITE_API_URL ?? '/api'

export const api = axios.create({ baseURL })

// Her isteğe erişim token'ını ekler.
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const NO_RETRY_URLS = ['/auth/login/', '/auth/refresh/', '/auth/register/']
let refreshPromise = null
let onSessionExpired = () => {}

export function setSessionExpiredHandler(handler) {
  onSessionExpired = handler
}

function refreshAccessToken(refresh) {
  // Aynı anda 401 alan istekler tek bir yenileme isteğini paylaşır.
  refreshPromise ??= axios
    .post(`${baseURL}/auth/refresh/`, { refresh })
    .then((response) => response.data.access)
    .finally(() => {
      refreshPromise = null
    })
  return refreshPromise
}

// 401 gelirse token'ı bir kez yenileyip isteği tekrarlar; olmazsa oturumu kapatır.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    const refresh = tokenStorage.getRefresh()
    const shouldRetry =
      error.response?.status === 401 &&
      refresh &&
      original &&
      !original._retry &&
      !NO_RETRY_URLS.includes(original.url)

    if (!shouldRetry) return Promise.reject(error)

    original._retry = true
    try {
      const access = await refreshAccessToken(refresh)
      tokenStorage.setAccess(access)
      original.headers.Authorization = `Bearer ${access}`
      return api(original)
    } catch (refreshError) {
      tokenStorage.clear()
      onSessionExpired()
      return Promise.reject(refreshError)
    }
  },
)
