<template>
  <div class='page-shell'>
    <section class='dashboard-hero'>
      <div>
        <span class='hero-kicker'>药房运营中心</span>
        <h1>欢迎回来，{{ userStore.userInfo.user_name || '用户' }}</h1>
        <p>药品、库存和订单数据已与本地 medicine 数据库实时同步。</p>
      </div>
      <el-button type='primary' @click='loadStats'>刷新数据</el-button>
    </section>

    <section class='stats-grid'>
      <div v-for='item in statItems' :key='item.key' class='stat-card'>
        <span>{{ item.label }}</span>
        <strong>{{ formatValue(item) }}</strong>
        <small>{{ item.hint }}</small>
      </div>
    </section>

    <div class='section-title'><h2>业务模块</h2><span>选择模块进入管理页面</span></div>
    <section class='module-grid'>
      <button v-for='item in resourceList' :key='item.key' class='module-card' @click='router.push("/" + item.api)'>
        <span class='module-icon'><el-icon><Grid /></el-icon></span>
        <span><strong>{{ item.title }}</strong><small>查看、新增和编辑{{ item.title }}</small></span>
        <el-icon><ArrowRight /></el-icon>
      </button>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Grid } from '@element-plus/icons-vue'
import { api } from '../api'
import { resourceList } from '../config/resources'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const stats = ref({})
const statItems = [
  { key: 'drugs', label: '药品品种', hint: '在库药品档案', suffix: '种' },
  { key: 'inventory_units', label: '库存总量', hint: '所有仓库库存', suffix: '件' },
  { key: 'suppliers', label: '合作供应商', hint: '供应商档案', suffix: '家' },
  { key: 'customers', label: '客户数量', hint: '客户档案', suffix: '位' },
  { key: 'purchase_orders', label: '采购订单', hint: '累计采购单', suffix: '单' },
  { key: 'sales_orders', label: '销售订单', hint: '累计销售单', suffix: '单' },
  { key: 'low_stock_items', label: '低库存预警', hint: '库存少于 20', suffix: '种' },
  { key: 'sales_amount', label: '销售金额', hint: '销售明细合计', prefix: '¥' },
]
const formatValue = (item) => `${item.prefix || ''}${Number(stats.value[item.key] || 0).toLocaleString()}${item.suffix || ''}`
async function loadStats() {
  const result = await api.dashboard()
  stats.value = result.data
}
onMounted(loadStats)
</script>
