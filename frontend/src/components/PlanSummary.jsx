import { WEEKDAYS } from './internshipPlan'

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('tr-TR') : '—'
}

export function PlanSummary({ doc }) {
  return (
    <table className="kv">
      <tbody>
        <tr>
          <th>Seçilen tarih aralığı</th>
          <td>
            {formatDate(doc.plan_start)} – {formatDate(doc.plan_end)}
          </td>
        </tr>
        <tr>
          <th>Seçilen günler</th>
          <td>{doc.plan_weekdays.map((day) => WEEKDAYS[day]).join(', ') || '—'}</td>
        </tr>
        {doc.needs_engineer_department && (
          <tr>
            <th>Mühendisin mezun olduğu bölüm</th>
            <td>{doc.engineer_department || '—'}</td>
          </tr>
        )}
      </tbody>
    </table>
  )
}
