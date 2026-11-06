import { NavLink, Outlet } from 'react-router-dom'
import { ROLES } from '../auth/roles'
import { useAuth } from '../auth/useAuth'

const LINKS = {
  [ROLES.STUDENT]: [{ to: '/ogrenci', label: 'Belgelerim' }],
  [ROLES.ADMIN]: [
    { to: '/yonetim', label: 'Başvurular' },
    { to: '/yonetim/tamamlanan', label: 'Tamamlandı' },
    { to: '/yonetim/ogrenciler', label: 'Öğrenci Veri Seti' },
  ],
}

export function Layout() {
  const { user, logout } = useAuth()

  return (
    <>
      <header className="topbar">
        <strong className="brand">Staj Belge Denetimi</strong>
        <nav>
          {(LINKS[user?.role] ?? []).map((link) => (
            <NavLink key={link.to} to={link.to} end>
              {link.label}
            </NavLink>
          ))}
        </nav>
        {user && (
          <div className="user-box">
            <span className="muted">{user.email}</span>
            <button type="button" className="secondary" onClick={logout}>
              Çıkış
            </button>
          </div>
        )}
      </header>
      <main className="container">
        <Outlet />
      </main>
    </>
  )
}
