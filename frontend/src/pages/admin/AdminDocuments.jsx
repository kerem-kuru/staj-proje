import { useEffect, useState } from 'react'
import { documentsApi } from '../../api/documents'
import { getErrorMessage } from '../../api/errors'
import { DocumentTable } from '../../components/DocumentTable'
import { ErrorMessage } from '../../components/ErrorMessage'

const STATUS_FILTERS = [
  { value: '', label: 'Tümü' },
  { value: 'ONAYLANDI', label: 'Onaylandı' },
  { value: 'HATALI_EKSIK', label: 'Hatalı/Eksik' },
  { value: 'INCELENIYOR', label: 'İnceleniyor' },
  { value: 'YUKLENDI', label: 'Yüklendi' },
  { value: 'TAMAMLANDI', label: 'Tamamlandı' },
]

export function AdminDocuments() {
  const [status, setStatus] = useState('ONAYLANDI')
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ results: [], count: 0, next: null, previous: null })
  const [error, setError] = useState('')

  useEffect(() => {
    const params = { page, ...(status && { status }) }
    documentsApi
      .list(params)
      .then(setData)
      .catch((err) => setError(getErrorMessage(err)))
  }, [status, page])

  return (
    <>
      <h1>Belgeler</h1>
      <div className="toolbar">
        <label>
          Statü{' '}
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value)
              setPage(1)
            }}
          >
            {STATUS_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>
        </label>
        <span className="muted">{data.count} belge</span>
      </div>
      <ErrorMessage message={error} />
      <DocumentTable documents={data.results} detailPath={(id) => `/yonetim/belgeler/${id}`} showStudent />
      <div className="actions">
        <button type="button" className="secondary" disabled={!data.previous} onClick={() => setPage(page - 1)}>
          ← Önceki
        </button>
        <button type="button" className="secondary" disabled={!data.next} onClick={() => setPage(page + 1)}>
          Sonraki →
        </button>
      </div>
    </>
  )
}
