import { Link } from 'react-router-dom'
import { StatusBadge } from './StatusBadge'

export function DocumentTable({ documents, detailPath, showStudent = false }) {
  if (documents.length === 0) return <p className="muted">Belge bulunamadı.</p>

  return (
    <table className="table">
      <thead>
        <tr>
          <th>#</th>
          {showStudent && <th>Öğrenci</th>}
          <th>Dosya</th>
          <th>Statü</th>
          <th>Rev.</th>
          <th>Son rapor</th>
          <th>Güncellendi</th>
        </tr>
      </thead>
      <tbody>
        {documents.map((doc) => (
          <tr key={doc.id}>
            <td>
              <Link to={detailPath(doc.id)}>{doc.id}</Link>
            </td>
            {showStudent && (
              <td>
                {doc.student_number} – {doc.student_name}
              </td>
            )}
            <td>
              <Link to={detailPath(doc.id)}>{doc.original_filename}</Link>
            </td>
            <td>
              <StatusBadge status={doc.status} label={doc.status_display} />
            </td>
            <td>{doc.revision}</td>
            <td>{doc.latest_report?.summary ?? '—'}</td>
            <td>{new Date(doc.updated_at).toLocaleString('tr-TR')}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
