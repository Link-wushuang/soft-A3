import api from './index'

export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password })

export const register = (username: string, password: string, role: string) =>
  api.post('/auth/register', { username, password, role })

export const getMe = () => api.get('/auth/me')
