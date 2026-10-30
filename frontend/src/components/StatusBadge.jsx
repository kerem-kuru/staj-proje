const CLASS_BY_STATUS = {
  YUKLENDI: 'badge-neutral',
  INCELENIYOR: 'badge-info',
  HATALI_EKSIK: 'badge-danger',
  ONAYLANDI: 'badge-success',
  TAMAMLANDI: 'badge-done',
}

export function StatusBadge({ status, label }) {
  return <span className={`badge ${CLASS_BY_STATUS[status] ?? 'badge-neutral'}`}>{label ?? status}</span>
}
