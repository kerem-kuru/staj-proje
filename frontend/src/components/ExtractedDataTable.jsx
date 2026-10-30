// Alan etiketleri ve sırası backend'den gelir (readers/ek16.py).
function format(field) {
  if (field.unparsed) return `“${field.unparsed}” (anlaşılamadı)`
  const { value } = field
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'boolean') return value ? 'Evet' : 'Hayır'
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return new Date(value).toLocaleDateString('tr-TR')
  return String(value)
}

export function ExtractedDataTable({ fields }) {
  if (!fields?.length) return <p className="muted">Belgeden okunan bilgi yok.</p>

  return (
    <table className="kv">
      <tbody>
        {fields.map((field) => (
          <tr key={field.name}>
            <th>{field.label}</th>
            <td>{format(field)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
