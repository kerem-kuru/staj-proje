// Backend tüm hataları {detail, errors} biçiminde döndürür (config/exceptions.py).
export function getErrorMessage(error, fallback = 'Bir hata oluştu. Lütfen tekrar deneyin.') {
  const data = error?.response?.data
  if (!data) return error?.response ? fallback : 'Sunucuya ulaşılamadı.'
  if (data.errors) {
    const messages = Object.values(data.errors).flat().filter(Boolean)
    if (messages.length) return messages.join(' ')
  }
  return data.detail || fallback
}
