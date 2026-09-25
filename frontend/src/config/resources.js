const text = (prop, label, required = false, placeholder = '') => ({
  prop,
  label,
  type: 'text',
  required,
  placeholder: placeholder || `请输入${label}`,
})

const number = (prop, label, required = false, min = 0) => ({
  prop,
  label,
  type: 'number',
  required,
  min,
})

const boolean = (prop, label, required = false, defaultValue = false, activeText = '是', inactiveText = '否') => ({
  prop,
  label,
  type: 'boolean',
  required,
  default: defaultValue,
  activeText,
  inactiveText,
})

const date = (prop, label, required = false) => ({
  prop,
  label,
  type: 'date',
  required,
})

export const resourceConfigs = {
  drugs: {
    key: 'drugs',
    api: 'drugs',
    title: '药品管理',
    idField: 'drug_id',
    columns: [
      { prop: 'drug_id', label: '药品编号', width: 150 },
      { prop: 'generic_name', label: '通用名', minWidth: 130 },
      { prop: 'approval_no', label: '批准文号', minWidth: 150 },
      { prop: 'dosage_form', label: '剂型', width: 100 },
      { prop: 'specification', label: '规格', width: 110 },
      { prop: 'unit', label: '单位', width: 80 },
      { prop: 'purchase_price', label: '采购价', width: 100 },
      { prop: 'retail_price', label: '零售价', width: 100 },
      { prop: 'manufacturer_id', label: '厂家编号', width: 130 },
    ],
    fields: [
      text('drug_id', '药品编号', false, '留空自动生成'),
      text('generic_name', '通用名', true),
      text('approval_no', '批准文号', true),
      text('dosage_form', '剂型', true),
      text('specification', '规格', true),
      text('unit', '单位', true),
      number('purchase_price', '采购价', true, 0.01),
      number('retail_price', '零售价', true, 0.01),
      text('manufacturer_id', '生产厂家编号'),
    ],
  },
  customers: {
    key: 'customers',
    api: 'customers',
    title: '客户管理',
    idField: 'customer_id',
    columns: [
      { prop: 'customer_id', label: '客户编号', width: 150 },
      { prop: 'name', label: '客户名称', minWidth: 140 },
      { prop: 'type', label: '客户类型', width: 110 },
      { prop: 'contact_phone', label: '联系电话', width: 140 },
    ],
    fields: [
      text('customer_id', '客户编号', false, '留空自动生成'),
      text('name', '客户名称', true),
      text('type', '客户类型', true),
      text('contact_phone', '联系电话'),
    ],
  },
  suppliers: {
    key: 'suppliers',
    api: 'suppliers',
    title: '供应商管理',
    idField: 'supplier_id',
    columns: [
      { prop: 'supplier_id', label: '供应商编号', width: 150 },
      { prop: 'name', label: '供应商名称', minWidth: 160 },
      { prop: 'contact_phone', label: '联系电话', width: 140 },
      { prop: 'status', label: '合作状态', width: 110 },
    ],
    fields: [
      text('supplier_id', '供应商编号', false, '留空自动生成'),
      text('name', '供应商名称', true),
      text('contact_phone', '联系电话'),
      boolean('status', '合作状态', true, true, '启用', '停用'),
    ],
  },
  employees: {
    key: 'employees',
    api: 'employees',
    title: '员工管理',
    idField: 'employee_id',
    columns: [
      { prop: 'employee_id', label: '员工编号', width: 150 },
      { prop: 'name', label: '姓名', minWidth: 130 },
      { prop: 'post', label: '岗位', minWidth: 140 },
    ],
    fields: [
      text('employee_id', '员工编号', false, '留空自动生成'),
      text('name', '姓名', true),
      text('post', '岗位', true),
    ],
  },
  warehouses: {
    key: 'warehouses',
    api: 'warehouses',
    title: '仓库管理',
    idField: 'warehouse_id',
    columns: [
      { prop: 'warehouse_id', label: '仓库编号', width: 150 },
      { prop: 'name', label: '仓库名称', minWidth: 150 },
      { prop: 'location', label: '仓库位置', minWidth: 180 },
    ],
    fields: [
      text('warehouse_id', '仓库编号', false, '留空自动生成'),
      text('name', '仓库名称', true),
      text('location', '仓库位置'),
    ],
  },
  inventory: {
    key: 'inventory',
    api: 'inventory',
    title: '库存管理',
    idField: 'inventory_id',
    columns: [
      { prop: 'inventory_id', label: '库存编号', width: 150 },
      { prop: 'drug_id', label: '药品编号', width: 140 },
      { prop: 'warehouse_id', label: '仓库编号', width: 140 },
      { prop: 'batch_no', label: '批号', minWidth: 130 },
      { prop: 'quantity', label: '数量', width: 90 },
      { prop: 'validity_date', label: '有效期', width: 130 },
    ],
    fields: [
      text('inventory_id', '库存编号', false, '留空自动生成'),
      text('drug_id', '药品编号', true),
      text('warehouse_id', '仓库编号', true),
      text('batch_no', '批号', true),
      number('quantity', '库存数量', true, 1),
      date('validity_date', '有效期', true),
    ],
  },
  'purchase-orders': {
    key: 'purchase-orders',
    api: 'purchase-orders',
    title: '采购订单',
    idField: 'po_id',
    columns: [
      { prop: 'po_id', label: '采购单号', width: 150 },
      { prop: 'supplier_id', label: '供应商编号', width: 150 },
      { prop: 'employee_id', label: '经办人编号', width: 140 },
      { prop: 'po_date', label: '采购日期', width: 130 },
      { prop: 'audit_status', label: '审核状态', width: 110 },
    ],
    fields: [
      text('po_id', '采购单号', false, '留空自动生成'),
      text('supplier_id', '供应商编号', true),
      text('employee_id', '经办人编号', true),
      date('po_date', '采购日期', true),
      boolean('audit_status', '审核状态', true, false, '已审核', '未审核'),
    ],
  },
  'sales-orders': {
    key: 'sales-orders',
    api: 'sales-orders',
    title: '销售订单',
    idField: 'so_id',
    columns: [
      { prop: 'so_id', label: '销售单号', width: 150 },
      { prop: 'customer_id', label: '客户编号', width: 150 },
      { prop: 'employee_id', label: '经办人编号', width: 140 },
      { prop: 'so_date', label: '销售日期', width: 130 },
    ],
    fields: [
      text('so_id', '销售单号', false, '留空自动生成'),
      text('customer_id', '客户编号', true),
      text('employee_id', '经办人编号', true),
      date('so_date', '销售日期', true),
    ],
  },
  'warehouse-in': {
    key: 'warehouse-in',
    api: 'warehouse-in',
    title: '入库管理',
    idField: 'wi_id',
    columns: [
      { prop: 'wi_id', label: '入库单号', width: 150 },
      { prop: 'po_id', label: '采购单号', width: 150 },
      { prop: 'warehouse_id', label: '仓库编号', width: 140 },
      { prop: 'in_date', label: '入库日期', width: 130 },
      { prop: 'batch_no', label: '批号', minWidth: 130 },
      { prop: 'validity_date', label: '有效期', width: 130 },
    ],
    fields: [
      text('wi_id', '入库单号', false, '留空自动生成'),
      text('po_id', '采购单号', true),
      text('warehouse_id', '仓库编号', true),
      date('in_date', '入库日期', true),
      text('batch_no', '批号', true),
      date('validity_date', '有效期', true),
    ],
  },
}

export const resourceList = Object.values(resourceConfigs)

export function getResourceConfig(key) {
  return resourceConfigs[key]
}
