<template>
  <el-dialog
    :model-value="store.projectFormVisible"
    :title="store.editingProject ? '编辑项目' : '新建项目'"
    width="500px"
    @close="store.closeProjectForm"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="项目名称" prop="project_name">
        <el-input
          v-model="formData.project_name"
          placeholder="请输入项目名称"
          clearable
        />
      </el-form-item>

      <el-form-item label="建设单位" prop="builder_unit">
        <el-input
          v-model="formData.builder_unit"
          placeholder="请输入建设单位"
          clearable
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="store.closeProjectForm">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="store.isLoading">
        {{ store.editingProject ? '更新' : '创建' }}
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
  project_name: '',
  builder_unit: ''
})

const rules = {
  project_name: [
    { required: true, message: '项目名称不能为空', trigger: 'blur' },
    { min: 2, max: 200, message: '项目名称长度应在 2-200 之间', trigger: 'blur' }
  ],
  builder_unit: [
    { max: 100, message: '建设单位长度不能超过 100', trigger: 'blur' }
  ]
}

// 监听编辑项目变化
watch(() => store.editingProject, (newVal) => {
  if (newVal) {
    formData.value = {
      project_name: newVal.project_name,
      builder_unit: newVal.builder_unit || ''
    }
  } else {
    formData.value = {
      project_name: '',
      builder_unit: ''
    }
  }
}, { immediate: true })

// 监听表单可见性
watch(() => store.projectFormVisible, (newVal) => {
  if (newVal) {
    // 重置表单验证
    formRef.value?.clearValidate()
  }
})

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    if (store.editingProject) {
      await store.updateProject(
        store.editingProject.id,
        formData.value.project_name,
        formData.value.builder_unit
      )
    } else {
      await store.createProject(
        formData.value.project_name,
        formData.value.builder_unit
      )
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

