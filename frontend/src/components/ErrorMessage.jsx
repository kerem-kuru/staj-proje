export function ErrorMessage({ message }) {
  if (!message) return null
  return (
    <p className="alert alert-error" role="alert">
      {message}
    </p>
  )
}
