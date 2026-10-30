import { useCallback, useEffect, useState } from 'react'
import { getErrorMessage } from '../../api/errors'
import { studentsApi } from '../../api/students'
import { ErrorMessage } from '../../components/ErrorMessage'
import { FileUploadForm } from '../../components/FileUploadForm'

export function AdminStudents() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState({ results: [], count: 0 })
  const [importResult, setImportResult] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    studentsApi
      .list(query ? { q: query } : {})
      .then(setData)
      .catch((err) => setError(getErrorMessage(err)))
  }, [query])

  useEffect(load, [load])

  async function handleImport(file) {
    const result = await studentsApi.importCsv(file)
    setImportResult(result)
    load()
  }

  return (
    <>
      <h1>Öğrenci veri seti</h1>
      <section className="card">
        <h2>CSV içe aktar</h2>
        <p className="muted">
          Sütunlar: <code>ogrenci_no;ad;soyad;tc_kimlik_no;bolum;sinif;eposta</code> (ayırıcı ; veya ,). Var olan
          öğrenci numaraları güncellenir.
        </p>
        <FileUploadForm accept=".csv" buttonLabel="İçe aktar" onUpload={handleImport} />
        {importResult && (
          <div className="alert alert-info">
            {importResult.created} öğrenci eklendi, {importResult.updated} güncellendi.
            {importResult.errors.length > 0 && (
              <ul>
                {importResult.errors.map((message) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>

      <section className="card">
        <div className="toolbar">
          <input placeholder="Numara veya ad ara…" value={query} onChange={(e) => setQuery(e.target.value)} />
          <span className="muted">{data.count} öğrenci</span>
        </div>
        <ErrorMessage message={error} />
        <table className="table">
          <thead>
            <tr>
              <th>Numara</th>
              <th>Ad soyad</th>
              <th>Bölüm</th>
              <th>Sınıf</th>
              <th>Hesap</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((s) => (
              <tr key={s.id}>
                <td>{s.student_number}</td>
                <td>{s.full_name}</td>
                <td>{s.department}</td>
                <td>{s.class_year ?? '—'}</td>
                <td>{s.has_account ? 'Var' : 'Yok'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  )
}
