import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

function readStoredUserInfo() {
  try {
    const value = JSON.parse(localStorage.getItem('userInfo') || '{}')
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {}
  } catch {
    localStorage.removeItem('userInfo')
    return {}
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(readStoredUserInfo())
  const isAdmin = computed(() => ['管理员', 'admin'].includes(userInfo.value.role))

  function setUserInfo(data) {
    token.value = data.token
    userInfo.value = data
    localStorage.setItem('token', data.token)
    localStorage.setItem('userInfo', JSON.stringify(data))
  }

  function clearUserInfo() {
    token.value = ''
    userInfo.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return { token, userInfo, isAdmin, setUserInfo, clearUserInfo }
})