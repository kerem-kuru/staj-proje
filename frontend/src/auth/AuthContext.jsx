import { useCallback, useEffect, useMemo, useState } from 'react'
import { authApi } from '../api/auth'
import { setSessionExpiredHandler } from '../api/client'
import { tokenStorage } from '../api/tokenStorage'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() => Boolean(tokenStorage.getAccess()))

  useEffect(() => {
    setSessionExpiredHandler(() => setUser(null))
    if (!tokenStorage.getAccess()) return
    authApi
      .me()
      .then(setUser)
      .catch(() => tokenStorage.clear())
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    tokenStorage.set(await authApi.login(email, password))
    const me = await authApi.me()
    setUser(me)
    return me
  }, [])

  // Token'lar sunucuda geçersiz kılınır; sunucuya ulaşılamasa da yerel oturum kapanır.
  const logout = useCallback(async () => {
    await authApi.logout().catch(() => {})
    tokenStorage.clear()
    setUser(null)
  }, [])

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
