import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="container">
      <h1>Sayfa bulunamadı</h1>
      <Link to="/">Ana sayfaya dön</Link>
    </div>
  )
}
