<template>
  <el-dialog
    :model-value="store.sectionFormVisible"
    :title="store.editingSection ? '编辑标段' : '新建标段'"
    width="600px"
    @close="store.closeSectionForm"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="标段名称" prop="section_name">
        <el-input
          v-model="formData.section_name"
          placeholder="请输入标段名称"
          clearable
        />
      </el-form-item>

      <el-form-item label="施工单位" prop="contractor_unit">
        <el-input
          v-model="formData.contractor_unit"
          placeholder="请输入施工单位"
          clearable
        />
      </el-form-item>

      <el-form-item label="监理单位" prop="supervisor_unit">
        <el-input
          v-model="formData.supervisor_unit"
          placeholder="请输入监理单位"
          clearable
        />
      </el-form-item>

      <el-form-item label="设计单位" prop="designer_unit">
        <el-input
          v-model="formData.designer_unit"
          placeholder="请输入设计单位"
          clearable
        />
      </el-form-item>

      <el-form-item label="第三方检测单位" prop="testing_unit">
        <el-input
          v-model="formData.testing_unit"
          placeholder="请输入第三方检测单位"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="store.closeSectionForm">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="store.isLoading">
        {{ store.editingSection ? '更新' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useProjectManagementStore } from '../stores/projectManagementStore'
import { ElMessage } from 'element-plus'

const store = useProjectManagementStore()
const formRef = ref(null)

const formData = ref({
  section_name: '',
  contractor_unit: '',
  supervisor_unit: '',
  designer_unit: '',
  testing_unit: ''
})

const rules = {
  section_name: [
    { required: true, message: '标段名称不能为空', trigger: 'blur' },
    { max: 200, message: '标段名称长度不能超过 200', trigger: 'blur' }
  ],
  contractor_unit: [
    { max: 100, message: '施工单位长度不能超过 100', trigger: 'blur' }
  ],
  supervisor_unit: [
    { max: 100, message: '监理单位长度不能超过 100', trigger: 'blur' }
  ],
  designer_unit: [
    { max: 100, message: '设计单位长度不能超过 100', trigger: 'blur' }
  ],
  testing_unit: [
    { max: 100, message: '第三方检测单位长度不能超过 100', trigger: 'blur' }
  ]
}

// 监听编辑标段变化
watch(() => store.editingSection, (newVal) => {
  if (newVal) {
    formData.value = {
      section_name: newVal.section_name || '',
      contractor_unit: newVal.contractor_unit || '',
      supervisor_unit: newVal.supervisor_unit || '',
      designer_unit: newVal.designer_unit || '',
      testing_unit: newVal.testing_unit || ''
    }
  } else {
    formData.value = {
      section_name: '',
      contractor_unit: '',
      supervisor_unit: '',
      designer_unit: '',
      testing_unit: ''
    }
  }
}, { immediate: true })

// 监听表单可见性
watch(() => store.sectionFormVisible, (newVal) => {
  if (newVal) {
    // 重置表单验证
    formRef.value?.clearValidate()
  }
})

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    if (store.editingSection) {
      await store.updateSection(store.editingSection.id, formData.value)
    } else {
      await store.createSection(formData.value)
    }
    
    if (!store.error) {
      ElMessage.success(store.message || '操作成功')
    }
  } catch (err) {
    console.error('表单验证失败:', err)
  }
}
</script>

<style scoped>
:deep(.el-dialog__body) {
  padding: 20px;
}
</style>

