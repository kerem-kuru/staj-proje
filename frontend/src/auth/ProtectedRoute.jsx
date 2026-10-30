import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { homePathFor } from './roles'
import { useAuth } from './useAuth'

// Giriş yapılmamışsa girişe, rol uymuyorsa kullanıcının kendi ana sayfasına yönlendirir.
export function ProtectedRoute({ roles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <p className="muted">Yükleniyor…</p>
  if (!user) return <Navigate to="/giris" replace state={{ from: location }} />
  if (roles && !roles.includes(user.role)) return <Navigate to={homePathFor(user)} replace />
  return <Outlet />
}
