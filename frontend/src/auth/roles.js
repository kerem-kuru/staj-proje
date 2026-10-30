export const ROLES = {
  STUDENT: 'ROLE_STUDENT',
  ADMIN: 'ROLE_ADMIN',
}

export function homePathFor(user) {
  if (!user) return '/giris'
  return user.role === ROLES.ADMIN ? '/yonetim' : '/ogrenci'
}
