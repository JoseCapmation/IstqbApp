const KEY = 'istqb_username'

export const getUser = (): string | null => localStorage.getItem(KEY)
export const setUser = (username: string): void => localStorage.setItem(KEY, username)
export const clearUser = (): void => localStorage.removeItem(KEY)
