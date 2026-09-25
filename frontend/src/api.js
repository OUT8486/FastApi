import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({ baseURL: '/api', timeout: 10000 })

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  (response) => {
    const result = response.data
    if (result.code !== 200) {
      ElMessage.error(result.message || '请求失败')
      if (result.code === 401) redirectToLogin()
      return Promise.reject(new Error(result.message || '请求失败'))
    }
    return result
  },
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message || '网络错误'
    if (status === 401) redirectToLogin()
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

function redirectToLogin() {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  if (window.location.pathname !== '/login') window.location.href = '/login'
}

export const api = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/users/register', data),
  logout: () => request.post('/auth/logout'),
  dashboard: () => request.get('/dashboard/stats'),
  getList: (resource) => request.get(`/${resource}`),
  getPage: (resource, page, size) => request.get(`/${resource}/page`, { params: { page, size } }),
  getById: (resource, id) => request.get(`/${resource}/${id}`),
  create: (resource, data) => request.post(`/${resource}`, data),
  update: (resource, id, data) => request.put(`/${resource}/${id}`, data),
  remove: (resource, id) => request.delete(`/${resource}/${id}`),
}
