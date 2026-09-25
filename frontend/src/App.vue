<template>
  <div v-if='showShell' class='app-shell'>
    <aside class='sidebar'>
      <div class='brand' @click='router.push("/")'><el-icon><FirstAidKit /></el-icon><strong>康宁药房</strong></div>
      <el-menu :default-active='activeMenu' router class='side-menu'>
        <el-menu-item index='/'><el-icon><Odometer /></el-icon><span>工作台</span></el-menu-item>
        <el-menu-item v-for='item in resourceList' :key='item.key' :index='menuPath(item)'><el-icon><Grid /></el-icon><span>{{ item.title }}</span></el-menu-item>
      </el-menu>
    </aside>
    <section class='workspace'>
      <header class='topbar'>
        <div><h2>{{ route.meta.title || "药店管理系统" }}</h2><small>{{ currentDate }}</small></div>
        <el-dropdown>
          <span class='user-chip'>{{ userStore.userInfo.user_name || "用户" }}<el-icon><ArrowDown /></el-icon></span>
          <template #dropdown><el-dropdown-menu><el-dropdown-item @click='handleLogout'>退出登录</el-dropdown-item></el-dropdown-menu></template>
        </el-dropdown>
      </header>
      <main class='main-area'><router-view /></main>
    </section>
  </div>
  <router-view v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, FirstAidKit, Grid, Odometer } from '@element-plus/icons-vue'
import { api } from './api'
import { resourceList } from './config/resources'
import { useUserStore } from './stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const showShell = computed(() => Boolean(route.meta.requiresAuth && userStore.token))
const activeMenu = computed(() => '/' + (route.path.split('/').filter(Boolean)[0] || ''))
const currentDate = new Intl.DateTimeFormat('zh-CN', { dateStyle: 'full' }).format(new Date())
function menuPath(item) { return '/' + item.api }
async function handleLogout() {
  try { await ElMessageBox.confirm('确定退出当前账号吗？', '提示', { type: 'warning' }) } catch { return }
  try { await api.logout() } catch { }
  userStore.clearUserInfo()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>
