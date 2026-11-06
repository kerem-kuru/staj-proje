import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../api/errors'
import { homePathFor } from '../auth/roles'
import { useAuth } from '../auth/useAuth'
import { ErrorMessage } from '../components/ErrorMessage'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const forbidden = location.state?.forbidden === true
  if (user && !forbidden) return <Navigate to={homePathFor(user)} replace />

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const me = await login(form.email, form.password)
      navigate(location.state?.from?.pathname ?? homePathFor(me), { replace: true })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  return (
    <div className="auth-card">
      <h1>Giriş</h1>
      {forbidden && <ErrorMessage message="Bu sayfaya erişim yetkiniz yok. Yetkili bir hesapla giriş yapın." />}
      <form onSubmit={handleSubmit} className="stack">
        <label>
          E-posta
          <input type="email" value={form.email} onChange={update('email')} required autoComplete="email" />
        </label>
        <label>
          Şifre
          <input
            type="password"
            value={form.password}
            onChange={update('password')}
            required
            autoComplete="current-password"
          />
        </label>
        <ErrorMessage message={error} />
        <button type="submit" disabled={busy}>
          {busy ? 'Giriş yapılıyor…' : 'Giriş yap'}
        </button>
      </form>
      <p className="muted">
        Hesabınız yok mu? <Link to="/kayit">Öğrenci kaydı</Link>
      </p>
    </div>
  )
}
