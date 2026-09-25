<template>
  <div class='page-shell'>
    <div class='page-heading'>
      <div><h1>{{ isEdit ? '编辑' : '新增' }}{{ config.title }}</h1><p>填写业务字段后保存，留空的编号会自动生成。</p></div>
      <el-button @click='router.back()'>返回</el-button>
    </div>
    <el-card class='form-card'>
      <el-form ref='formRef' :model='form' :rules='rules' label-width='150px'>
        <el-form-item v-for='field in config.fields' :key='field.prop' :label='field.label' :prop='field.prop'>
          <el-input-number v-if='field.type === "number"' v-model='form[field.prop]' :min='field.min' style='width:100%' />
          <el-switch v-else-if='field.type === "boolean"' v-model='form[field.prop]' :active-text='field.activeText' :inactive-text='field.inactiveText' />
          <el-date-picker v-else-if='field.type === "date"' v-model='form[field.prop]' type='date' value-format='YYYY-MM-DD' :placeholder='field.placeholder' style='width:100%' />
          <el-input v-else v-model='form[field.prop]' :placeholder='field.placeholder' clearable />
        </el-form-item>
        <el-form-item>
          <el-button type='primary' :loading='saving' @click='submit'>保存</el-button>
          <el-button @click='router.back()'>取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { getResourceConfig } from '../config/resources'

const props = defineProps({ resourceKey: { type: String, required: true } })
const route = useRoute()
const router = useRouter()
const formRef = ref()
const saving = ref(false)
const config = computed(() => getResourceConfig(props.resourceKey))
const isEdit = computed(() => Boolean(route.params.id))
const form = reactive({})
const rules = computed(() => Object.fromEntries(config.value.fields.filter((field) => field.required).map((field) => [field.prop, [{ required: true, message: `请填写${field.label}` }]])))
function resetForm() {
  Object.keys(form).forEach((key) => delete form[key])
  config.value.fields.forEach((field) => { form[field.prop] = field.type === 'number' ? field.min : field.type === 'boolean' ? field.default : '' })
}
async function loadDetail() {
  if (!isEdit.value) return
  const result = await api.getById(config.value.api, route.params.id)
  Object.assign(form, result.data)
}
async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) await api.update(config.value.api, route.params.id, form)
    else await api.create(config.value.api, form)
    ElMessage.success('保存成功')
    router.push(`/${config.value.api}`)
  } finally { saving.value = false }
}
onMounted(async () => { resetForm(); await loadDetail() })
</script>
