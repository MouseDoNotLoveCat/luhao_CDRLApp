<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择或创建项目"
    width="600px"
    @close="handleClose"
  >
    <div class="project-selection">
      <!-- 当前项目信息 -->
      <el-alert
        v-if="currentProjectName"
        :title="`当前项目：${currentProjectName}`"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <!-- 选择现有项目 -->
      <div class="section">
        <h4>从现有项目中选择</h4>
        <el-select
          v-model="selectedProjectId"
          placeholder="请选择项目"
          filterable
          style="width: 100%"
          @change="handleProjectSelect"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="`${project.project_name} (${project.builder_unit || '无建设单位'})`"
            :value="project.id"
          />
        </el-select>
      </div>

      <!-- 分隔线 -->
      <el-divider>或</el-divider>

      <!-- 创建新项目 -->
      <div class="section">
        <h4>创建新项目</h4>
        <el-form :model="newProject" label-width="100px">
          <el-form-item label="项目名称" required>
            <el-input
              v-model="newProject.project_name"
              placeholder="例如：玉岑铁路"
            />
          </el-form-item>
          <el-form-item label="建设单位" required>
            <el-input
              v-model="newProject.builder_unit"
              placeholder="例如：南宁铁路工程建设指挥部"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="isLoading">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  currentProjectName: {
    type: String,
    default: ''
  },
  sectionName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:visible', 'confirm'])

const dialogVisible = ref(false)
const projects = ref([])
const selectedProjectId = ref(null)
const newProject = ref({
  project_name: '',
  builder_unit: ''
})
const isLoading = ref(false)

// 监听 visible 属性变化
watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (val) {
    fetchProjects()
  }
})

// 监听 dialogVisible 变化，同步到父组件
watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

// 获取项目列表
const fetchProjects = async () => {
  try {
    console.log('🔍 开始获取项目列表...')
    const response = await api.get('/projects', {
      params: { limit: 1000 }
    })
    console.log('📥 项目列表响应:', response)
    // 后端返回格式：{ total: number, data: [...] }
    projects.value = response.data || []
    console.log('✅ 项目列表加载成功，共', projects.value.length, '个项目')
  } catch (error) {
    console.error('❌ 获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}

// 选择项目
const handleProjectSelect = () => {
  // 清空新建项目表单
  newProject.value = {
    project_name: '',
    builder_unit: ''
  }
}

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false
  selectedProjectId.value = null
  newProject.value = {
    project_name: '',
    builder_unit: ''
  }
}

// 确认选择
const handleConfirm = async () => {
  // 情况1：选择了现有项目
  if (selectedProjectId.value) {
    const project = projects.value.find(p => p.id === selectedProjectId.value)
    if (project) {
      emit('confirm', {
        project_id: project.id,
        project_name: project.project_name,
        builder_unit: project.builder_unit
      })
      handleClose()
    }
    return
  }

  // 情况2：创建新项目
  if (newProject.value.project_name && newProject.value.builder_unit) {
    isLoading.value = true
    try {
      console.log('🔍 创建新项目:', newProject.value)
      const response = await api.post('/projects', null, {
        params: {
          project_name: newProject.value.project_name,
          builder_unit: newProject.value.builder_unit
        }
      })
      console.log('✅ 项目创建成功:', response)

      ElMessage.success('项目创建成功')
      emit('confirm', {
        project_id: response.id,
        project_name: response.project_name,
        builder_unit: response.builder_unit
      })
      handleClose()
    } catch (error) {
      console.error('❌ 创建项目失败:', error)
      ElMessage.error(error.response?.data?.detail || '创建项目失败')
    } finally {
      isLoading.value = false
    }
    return
  }

  // 情况3：既没选择也没创建
  ElMessage.warning('请选择现有项目或创建新项目')
}

onMounted(() => {
  if (props.visible) {
    fetchProjects()
  }
})
</script>

<style scoped>
.project-selection {
  padding: 10px 0;
}

.section {
  margin-bottom: 20px;
}

.section h4 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}
</style>

