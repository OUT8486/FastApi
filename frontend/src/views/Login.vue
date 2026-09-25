<template>
  <div class='login-page'>
    <div class='login-orb orb-one'></div>
    <div class='login-orb orb-two'></div>
    <el-card class='login-card'>
      <div class='login-brand'><el-icon><FirstAidKit /></el-icon></div>
      <p class='login-kicker'>康宁药房 · PHARMACY ADMIN</p>
      <h1>欢迎回来</h1>
      <p class='login-subtitle'>登录后管理药品、库存与订单</p>
      <el-form ref='formRef' :model='form' :rules='rules' label-position='top' @submit.prevent='submit'>
        <el-form-item label='用户名' prop='username'>
          <el-input v-model='form.username' placeholder='请输入用户名' clearable />
        </el-form-item>
        <el-form-item label='密码' prop='password'>
          <el-input v-model='form.password' type='password' placeholder='请输入密码' show-password @keyup.enter='submit' />
        </el-form-item>
        <el-button type='primary' size='large' :loading='loading' class='login-button' @click='submit'>登录</el-button>
      </el-form>
      <div class='register-link'>还没有账号？<el-link type='primary' @click='router.push("/register")'>立即注册</el-link></div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { FirstAidKit } from '@element-plus/icons-vue'
import { api } from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const result = await api.login(form)
    userStore.setUserInfo(result.data)
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>
