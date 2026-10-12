export const storage = {
  get(key: string) {
    try {
      return localStorage.getItem(key) ?? ""
    } catch {
      return ""
    }
  },
  set(key: string, value: string) {
    try {
      localStorage.setItem(key, value)
    } catch {
      return
    }
  },
}
