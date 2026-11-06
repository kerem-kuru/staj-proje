import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { documentsApi } from '../../api/documents'
import { getErrorMessage } from '../../api/errors'
import { DocumentTable } from '../../components/DocumentTable'
import { ErrorMessage } from '../../components/ErrorMessage'
import { FileUploadForm } from '../../components/FileUploadForm'
import { EMPTY_PLAN } from '../../components/internshipPlan'
import { InternshipPlanFields } from '../../components/InternshipPlanFields'

export function StudentDashboard() {
  const navigate = useNavigate()
  const [documents, setDocuments] = useState([])
  const [plan, setPlan] = useState(EMPTY_PLAN)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    documentsApi
      .list()
      .then((data) => setDocuments(data.results))
      .catch((err) => setError(getErrorMessage(err)))
  }, [])

  useEffect(load, [load])

  async function handleUpload(file) {
    const document = await documentsApi.upload(file, plan)
    navigate(`/ogrenci/belgeler/${document.id}`)
  }

  return (
    <>
      <h1>Belgelerim</h1>
      <section className="card">
        <h2>Ek-16 yükle</h2>
        <p className="muted">
          Staj yapacağınız günleri seçip Ek-16 belgenizi yükleyin (Word, PDF, JPEG veya PNG). Sistem belgeyi denetleyip
          eksikleri raporlar.
        </p>
        <InternshipPlanFields plan={plan} onChange={setPlan} />
        <FileUploadForm onUpload={handleUpload} />
      </section>
      <section className="card">
        <h2>Yüklenen belgeler</h2>
        <ErrorMessage message={error} />
        <DocumentTable documents={documents} detailPath={(id) => `/ogrenci/belgeler/${id}`} />
      </section>
    </>
  )
}
