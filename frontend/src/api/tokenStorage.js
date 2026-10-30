const ACCESS_KEY = 'staj.access'
const REFRESH_KEY = 'staj.refresh'

export const tokenStorage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  setAccess: (access) => localStorage.setItem(ACCESS_KEY, access),
  set({ access, refresh }) {
    localStorage.setItem(ACCESS_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}
