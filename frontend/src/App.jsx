import { Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { homePathFor, ROLES } from './auth/roles'
import { useAuth } from './auth/useAuth'
import { Layout } from './components/Layout'
import { AdminDocumentDetail } from './pages/admin/AdminDocumentDetail'
import { AdminDocuments } from './pages/admin/AdminDocuments'
import { AdminStudents } from './pages/admin/AdminStudents'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { RegisterPage } from './pages/RegisterPage'
import { StudentDashboard } from './pages/student/StudentDashboard'
import { StudentDocumentDetail } from './pages/student/StudentDocumentDetail'

function HomeRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <p className="muted">Yükleniyor…</p>
  return <Navigate to={homePathFor(user)} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route element={<Layout />}>
        <Route path="/giris" element={<LoginPage />} />
        <Route path="/kayit" element={<RegisterPage />} />

        <Route element={<ProtectedRoute roles={[ROLES.STUDENT]} />}>
          <Route path="/ogrenci" element={<StudentDashboard />} />
          <Route path="/ogrenci/belgeler/:id" element={<StudentDocumentDetail />} />
        </Route>

        <Route element={<ProtectedRoute roles={[ROLES.ADMIN]} />}>
          <Route path="/yonetim" element={<AdminDocuments />} />
          <Route path="/yonetim/belgeler/:id" element={<AdminDocumentDetail />} />
          <Route path="/yonetim/ogrenciler" element={<AdminStudents />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
