import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('token') || '')

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password)
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    user.value = { id: res.data.user_id, role: res.data.role, displayName: res.data.display_name }
  }

  async function fetchUser() {
    const res = await getMe()
    user.value = res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, login, fetchUser, logout }
})
