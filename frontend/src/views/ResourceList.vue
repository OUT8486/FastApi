<template>
  <div class='page-shell'>
    <div class='page-heading'>
      <div><h1>{{ config.title }}</h1><p>共 {{ filteredRows.length }} 条记录，数据来自本地 medicine 数据库。</p></div>
      <el-button v-if='userStore.isAdmin' type='primary' @click='router.push(`/${config.api}/new`)'><el-icon><Plus /></el-icon>新增{{ config.title }}</el-button>
    </div>
    <el-card>
      <div class='toolbar'>
        <el-input v-model='keyword' clearable placeholder='搜索当前列表'><template #prefix><el-icon><Search /></el-icon></template></el-input>
        <el-button @click='loadData'><el-icon><Refresh /></el-icon>刷新</el-button>
      </div>
      <el-table v-loading='loading' :data='pagedRows' stripe border>
        <el-table-column v-for='column in config.columns' :key='column.prop' :prop='column.prop' :label='column.label' :width='column.width' :min-width='column.minWidth'>
          <template #default='{ row }'>{{ displayValue(row, column.prop) }}</template>
        </el-table-column>
        <el-table-column v-if='userStore.isAdmin' label='操作' width='170' fixed='right'>
          <template #default='{ row }'>
            <el-button link type='primary' @click='router.push(`/${config.api}/${row[config.idField]}/edit`)'>编辑</el-button>
            <el-button link type='danger' @click='removeRow(row)'>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class='pagination-bar'>
        <el-pagination v-model:current-page='page' v-model:page-size='size' :page-sizes='[10, 20, 50]' layout='total, sizes, prev, pager, next' :total='filteredRows.length' />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { api } from '../api'
import { getResourceConfig } from '../config/resources'
import { useUserStore } from '../stores/user'

const props = defineProps({ resourceKey: { type: String, required: true } })
const router = useRouter()
const userStore = useUserStore()
const rows = ref([])
const keyword = ref('')
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const config = computed(() => getResourceConfig(props.resourceKey))
const filteredRows = computed(() => {
  const term = keyword.value.trim().toLowerCase()
  if (!term) return rows.value
  return rows.value.filter((row) => Object.values(row).some((value) => String(value ?? '').toLowerCase().includes(term)))
})
const pagedRows = computed(() => {
  const start = (page.value - 1) * size.value
  return filteredRows.value.slice(start, start + size.value)
})
function displayValue(row, prop) {
  const value = row[prop]
  if (value === null || value === undefined || value === '') return '-'
  if (prop === 'audit_status') return Number(value) === 1 ? '已审核' : '未审核'
  if (prop === 'status') return Number(value) === 1 ? '正常合作' : '已停用'
  return value
}
async function loadData() {
  loading.value = true
  try { rows.value = (await api.getList(config.value.api)).data || [] } finally { loading.value = false }
}
async function removeRow(row) {
  try {
    await ElMessageBox.confirm('删除后无法恢复，确定继续吗？', '删除确认', { type: 'warning' })
  } catch {
    return
  }
  await api.remove(config.value.api, row[config.value.idField])
  ElMessage.success('删除成功')
  loadData()
}
watch(() => props.resourceKey, () => { keyword.value = ''; page.value = 1; loadData() })
watch(keyword, () => { page.value = 1 })
onMounted(loadData)
</script>
