import { useState } from 'react'
import { getErrorMessage } from '../api/errors'
import { ErrorMessage } from './ErrorMessage'

export function FileUploadForm({ onUpload, accept = '.pdf,.jpg,.jpeg,.png', buttonLabel = 'Yükle' }) {
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    if (!file) {
      setError('Lütfen bir dosya seçin.')
      return
    }
    setBusy(true)
    setError('')
    try {
      await onUpload(file)
      setFile(null)
      event.target.reset()
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <input type="file" accept={accept} onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
      <button type="submit" disabled={busy}>
        {busy ? 'Yükleniyor…' : buttonLabel}
      </button>
      <ErrorMessage message={error} />
    </form>
  )
}
