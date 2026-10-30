import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { documentsApi } from '../../api/documents'
import { getErrorMessage } from '../../api/errors'
import { ErrorMessage } from '../../components/ErrorMessage'
import { ExtractedDataTable } from '../../components/ExtractedDataTable'
import { ReportView } from '../../components/ReportView'
import { StatusBadge } from '../../components/StatusBadge'

export function AdminDocumentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [note, setNote] = useState('')
  const [error, setError] = useState('')

  const load = useCallback(() => {
    documentsApi
      .get(id)
      .then((data) => {
        setDoc(data)
        setNote(data.admin_note)
      })
      .catch((err) => setError(getErrorMessage(err)))
  }, [id])

  useEffect(load, [load])

  async function run(action) {
    setError('')
    try {
      const updated = await action()
      if (updated) {
        setDoc(updated)
        setNote(updated.admin_note)
      }
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  async function handleDelete() {
    if (!window.confirm('Belge kalıcı olarak silinsin mi?')) return
    await run(async () => {
      await documentsApi.remove(id)
      navigate('/yonetim')
    })
  }

  if (!doc) return error ? <ErrorMessage message={error} /> : <p className="muted">Yükleniyor…</p>

  return (
    <>
      <Link to="/yonetim">← Belgeler</Link>
      <h1>
        {doc.student_number} – {doc.student_name} <StatusBadge status={doc.status} label={doc.status_display} />
      </h1>
      <ErrorMessage message={error} />

      <section className="card">
        <h2>İşlemler</h2>
        <label className="stack">
          Yönetici notu / geri çevirme gerekçesi
          <textarea rows={3} value={note} onChange={(e) => setNote(e.target.value)} />
        </label>
        <div className="actions">
          {doc.permissions.can_complete && (
            <button type="button" onClick={() => run(() => documentsApi.complete(id))}>
              Tamamlandı olarak işaretle
            </button>
          )}
          {doc.permissions.can_reject && (
            <button type="button" className="warning" onClick={() => run(() => documentsApi.reject(id, note))}>
              Geri çevir (Hatalı/Eksik)
            </button>
          )}
          <button type="button" className="secondary" onClick={() => run(() => documentsApi.updateNote(id, note))}>
            Notu kaydet
          </button>
          <button type="button" className="secondary" onClick={() => documentsApi.download(id, doc.original_filename)}>
            Dosyayı indir
          </button>
          <button type="button" className="danger" onClick={handleDelete}>
            Sil
          </button>
        </div>
      </section>

      <section className="card">
        <h2>Son denetim</h2>
        <ReportView report={doc.latest_report} />
      </section>

      <section className="card">
        <h2>Belgeden okunan bilgiler</h2>
        <ExtractedDataTable fields={doc.extracted_fields} />
      </section>

      <section className="card">
        <h2>Rapor geçmişi</h2>
        {doc.reports.map((report) => (
          <ReportView key={report.id} report={report} />
        ))}
      </section>
    </>
  )
}
