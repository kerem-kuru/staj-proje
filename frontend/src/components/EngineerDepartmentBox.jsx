import { useState } from 'react'
import { documentsApi } from '../api/documents'
import { getErrorMessage } from '../api/errors'
import { ErrorMessage } from './ErrorMessage'

// Mühendis sayısı 5'in altındaysa mühendisin mezun olduğu bölümü soran uyarı kutucuğu.
export function EngineerDepartmentBox({ doc, onSaved }) {
  const [department, setDepartment] = useState(doc.engineer_department)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    try {
      onSaved(await documentsApi.setEngineerDepartment(doc.id, department))
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  return (
    <form className="alert alert-warning stack" onSubmit={handleSubmit}>
      <label>
        Mühendis sayısı 5'in altında. Mühendisin mezun olduğu bölüm nedir?
        <input value={department} onChange={(e) => setDepartment(e.target.value)} required maxLength={150} />
      </label>
      <ErrorMessage message={error} />
      <button type="submit">Kaydet</button>
    </form>
  )
}
