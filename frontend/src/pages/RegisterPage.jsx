import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { getErrorMessage } from '../api/errors'
import { useAuth } from '../auth/useAuth'
import { ErrorMessage } from '../components/ErrorMessage'

const EMPTY = { student_number: '', first_name: '', last_name: '', email: '', password: '' }

export function RegisterPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await authApi.register(form)
      await login(form.email, form.password)
      navigate('/ogrenci', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  return (
    <div className="auth-card">
      <h1>Öğrenci kaydı</h1>
      <p className="muted">Kayıt için öğrenci numaranızın okulun öğrenci listesinde bulunması gerekir.</p>
      <form onSubmit={handleSubmit} className="stack">
        <label>
          Öğrenci numarası
          <input value={form.student_number} onChange={update('student_number')} required />
        </label>
        <div className="row">
          <label>
            Ad
            <input value={form.first_name} onChange={update('first_name')} required />
          </label>
          <label>
            Soyad
            <input value={form.last_name} onChange={update('last_name')} required />
          </label>
        </div>
        <label>
          E-posta
          <input type="email" value={form.email} onChange={update('email')} required autoComplete="email" />
        </label>
        <label>
          Şifre (en az 8 karakter)
          <input
            type="password"
            value={form.password}
            onChange={update('password')}
            required
            minLength={8}
            autoComplete="new-password"
          />
        </label>
        <ErrorMessage message={error} />
        <button type="submit" disabled={busy}>
          {busy ? 'Kaydediliyor…' : 'Kayıt ol'}
        </button>
      </form>
      <p className="muted">
        Zaten hesabınız var mı? <Link to="/giris">Giriş yap</Link>
      </p>
    </div>
  )
}
