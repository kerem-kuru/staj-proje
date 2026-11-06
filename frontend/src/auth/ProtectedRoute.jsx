import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './useAuth'

// Giriş yapılmamışsa ya da rol uymuyorsa giriş sayfasına yönlendirir.
export function ProtectedRoute({ roles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <p className="muted">Yükleniyor…</p>
  if (!user) return <Navigate to="/giris" replace state={{ from: location }} />
  if (roles && !roles.includes(user.role)) return <Navigate to="/giris" replace state={{ forbidden: true }} />
  return <Outlet />
}
