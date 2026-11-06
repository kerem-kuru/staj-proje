import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { documentsApi } from '../../api/documents'
import { getErrorMessage } from '../../api/errors'
import { EngineerDepartmentBox } from '../../components/EngineerDepartmentBox'
import { ErrorMessage } from '../../components/ErrorMessage'
import { ExtractedDataTable } from '../../components/ExtractedDataTable'
import { FileUploadForm } from '../../components/FileUploadForm'
import { InternshipPlanFields } from '../../components/InternshipPlanFields'
import { PlanSummary } from '../../components/PlanSummary'
import { ReportView } from '../../components/ReportView'
import { StatusBadge } from '../../components/StatusBadge'

function ReuploadForm({ doc, onDone }) {
  const [plan, setPlan] = useState({
    start: doc.plan_start ?? '',
    end: doc.plan_end ?? '',
    weekdays: doc.plan_weekdays,
  })

  return (
    <>
      <InternshipPlanFields plan={plan} onChange={setPlan} />
      <FileUploadForm
        buttonLabel="Yeniden yükle"
        onUpload={(file) => documentsApi.reupload(doc.id, file, plan).then(onDone)}
      />
    </>
  )
}

export function StudentDocumentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    documentsApi
      .get(id)
      .then(setDoc)
      .catch((err) => setError(getErrorMessage(err)))
  }, [id])

  useEffect(load, [load])

  async function handleDelete() {
    if (!window.confirm('Belge silinsin mi?')) return
    try {
      await documentsApi.remove(id)
      navigate('/ogrenci')
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  if (!doc) return error ? <ErrorMessage message={error} /> : <p className="muted">Yükleniyor…</p>

  return (
    <>
      <Link to="/ogrenci">← Belgelerim</Link>
      <h1>
        {doc.doc_type_display} #{doc.id} <StatusBadge status={doc.status} label={doc.status_display} />
      </h1>
      <ErrorMessage message={error} />
      {doc.admin_note && <p className="alert alert-info">Yönetici notu: {doc.admin_note}</p>}
      {doc.status === 'TAMAMLANDI' && (
        <p className="alert alert-info">Bu belge tamamlandı; artık değiştirilemez veya silinemez.</p>
      )}

      <section className="card">
        <h2>Denetim sonucu</h2>
        <ReportView report={doc.latest_report} />
        {doc.needs_engineer_department && doc.status !== 'TAMAMLANDI' && (
          <EngineerDepartmentBox doc={doc} onSaved={setDoc} />
        )}
      </section>

      <section className="card">
        <h2>Staj planı</h2>
        <PlanSummary doc={doc} />
      </section>

      {doc.permissions.can_reupload && (
        <section className="card">
          <h2>Düzeltilmiş belgeyi yükle</h2>
          <ReuploadForm doc={doc} onDone={setDoc} />
        </section>
      )}

      <section className="card">
        <h2>Belgeden okunan bilgiler</h2>
        <ExtractedDataTable fields={doc.extracted_fields} />
      </section>

      <div className="actions">
        <button type="button" className="secondary" onClick={() => documentsApi.download(id, doc.original_filename)}>
          Dosyayı indir
        </button>
        {doc.permissions.can_delete && (
          <button type="button" className="danger" onClick={handleDelete}>
            Belgeyi sil
          </button>
        )}
      </div>
    </>
  )
}
