<template>
  <div class='login-page'>
    <el-card class='login-card'>
      <div class='login-brand'><el-icon><UserFilled /></el-icon></div>
      <p class='login-kicker'>创建新账号</p>
      <h1>注册账户</h1>
      <p class='login-subtitle'>注册用户默认为普通用户角色</p>
      <el-form ref='formRef' :model='form' :rules='rules' label-position='top' @submit.prevent='submit'>
        <el-form-item label='用户名' prop='user_name'>
          <el-input v-model='form.user_name' placeholder='请输入用户名' clearable />
        </el-form-item>
        <el-form-item label='密码' prop='password'>
          <el-input v-model='form.password' type='password' placeholder='至少 6 位' show-password />
        </el-form-item>
        <el-form-item label='确认密码' prop='confirmPassword'>
          <el-input v-model='form.confirmPassword' type='password' placeholder='再次输入密码' show-password />
        </el-form-item>
        <el-button type='primary' size='large' :loading='loading' class='login-button' @click='submit'>注册</el-button>
      </el-form>
      <div class='register-link'>已有账号？<el-link type='primary' @click='router.push("/login")'>返回登录</el-link></div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import { api } from '../api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ user_name: '', password: '', confirmPassword: '' })
const validateConfirm = (_rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}
const rules = {
  user_name: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度为 2 到 50 位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await api.register({ user_name: form.user_name, password: form.password })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>
