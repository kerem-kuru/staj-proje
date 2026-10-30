// Bir denetim raporunu (ValidationReport) hata/uyarı listesi olarak gösterir.
export function ReportView({ report }) {
  if (!report) return <p className="muted">Henüz denetim raporu yok.</p>

  return (
    <div className={`report ${report.is_valid ? 'report-ok' : 'report-fail'}`}>
      <p>
        <strong>{report.summary}</strong>{' '}
        <span className="muted">
          (revizyon {report.revision}, {new Date(report.created_at).toLocaleString('tr-TR')})
        </span>
      </p>
      {report.issues.length > 0 && (
        <ul className="issues">
          {report.issues.map((issue, index) => (
            <li key={`${issue.code}-${issue.field}-${index}`} className={`issue issue-${issue.severity}`}>
              <span className="issue-tag">{issue.severity === 'error' ? 'Hata' : 'Uyarı'}</span>
              {issue.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
