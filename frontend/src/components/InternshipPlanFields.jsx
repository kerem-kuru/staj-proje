import { WEEKDAYS } from './internshipPlan'

// Öğrencinin staj yapacağı tarih aralığı ve haftalık günler; sistem belgeyle bu seçimi karşılaştırır.
export function InternshipPlanFields({ plan, onChange }) {
  function toggle(day) {
    const weekdays = plan.weekdays.includes(day)
      ? plan.weekdays.filter((selected) => selected !== day)
      : [...plan.weekdays, day].sort()
    onChange({ ...plan, weekdays })
  }

  return (
    <fieldset className="plan-fields">
      <legend>Staj planı</legend>
      <div className="toolbar">
        <label>
          Başlangıç{' '}
          <input type="date" value={plan.start} onChange={(e) => onChange({ ...plan, start: e.target.value })} />
        </label>
        <label>
          Bitiş <input type="date" value={plan.end} onChange={(e) => onChange({ ...plan, end: e.target.value })} />
        </label>
      </div>
      <div className="weekdays">
        {WEEKDAYS.map((name, day) => (
          <label key={name}>
            <input type="checkbox" checked={plan.weekdays.includes(day)} onChange={() => toggle(day)} /> {name}
          </label>
        ))}
      </div>
    </fieldset>
  )
}
