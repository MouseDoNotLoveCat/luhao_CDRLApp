<template>
  <div class="project-section-mapping">
    <el-card class="mapping-card">
      <template #header>
        <div class="card-header">
          <span class="title">📋 项目-标段关联确认</span>
          <el-tag type="info" size="small">{{ mappingCount }} 个标段</el-tag>
        </div>
      </template>

      <el-alert
        title="提示：请确认每个标段关联的项目是否正确，如有错误请点击编辑按钮修改"
        type="warning"
        :closable="false"
        style="margin-bottom: 15px"
      />

      <!-- 批量操作栏 -->
      <div class="batch-operations">
        <div class="left-section">
          <el-checkbox
            v-model="selectAll"
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
          >
            全选
          </el-checkbox>
          <span class="selected-count" v-if="selectedSections.size > 0">
            已选中 {{ selectedSections.size }} 个标段
          </span>
        </div>
        <div class="right-section">
          <el-button
            type="primary"
            size="small"
            :disabled="selectedSections.size === 0"
            @click="handleBatchEdit"
          >
            批量设置项目
          </el-button>
        </div>
      </div>

      <div class="mapping-list">
        <div
          v-for="(projectInfo, sectionName) in sectionProjectMapping"
          :key="sectionName"
          class="mapping-item"
          :class="{ selected: selectedSections.has(sectionName) }"
        >
          <div class="checkbox-wrapper">
            <el-checkbox
              :model-value="selectedSections.has(sectionName)"
              @change="handleSectionSelect(sectionName, $event)"
            />
          </div>
          <div class="section-name">
            <el-tag type="primary" size="large">{{ sectionName }}</el-tag>
          </div>
          <div class="arrow">→</div>
          <div class="project-info">
            <div class="project-name">
              <strong>{{ projectInfo.project_name || '未知项目' }}</strong>
            </div>
            <div class="builder-unit" v-if="projectInfo.builder_unit">
              {{ projectInfo.builder_unit }}
            </div>
          </div>
          <div class="actions">
            <el-button
              type="primary"
              size="small"
              @click="handleEdit(sectionName, projectInfo)"
            >
              编辑
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 项目选择对话框 -->
    <ProjectSelectionDialog
      v-model:visible="dialogVisible"
      :current-project-name="currentProjectName"
      :section-name="currentSectionName"
      @confirm="handleProjectConfirm"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import ProjectSelectionDialog from './ProjectSelectionDialog.vue'

const props = defineProps({
  sectionProjectMapping: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update'])

const dialogVisible = ref(false)
const currentSectionName = ref('')
const currentProjectName = ref('')
const isBatchMode = ref(false)  // 是否为批量模式
const selectedSections = ref(new Set())  // 选中的标段集合

const mappingCount = computed(() => {
  return Object.keys(props.sectionProjectMapping).length
})

// 全选状态
const selectAll = computed({
  get() {
    return selectedSections.value.size === mappingCount.value && mappingCount.value > 0
  },
  set(value) {
    // 这个 setter 主要是为了让 v-model 工作，实际逻辑在 handleSelectAll 中
  }
})

// 是否为半选状态
const isIndeterminate = computed(() => {
  const count = selectedSections.value.size
  return count > 0 && count < mappingCount.value
})

// 处理全选/取消全选
const handleSelectAll = (checked) => {
  if (checked) {
    // 全选
    selectedSections.value = new Set(Object.keys(props.sectionProjectMapping))
  } else {
    // 取消全选
    selectedSections.value.clear()
  }
}

// 处理单个标段选择
const handleSectionSelect = (sectionName, checked) => {
  if (checked) {
    selectedSections.value.add(sectionName)
  } else {
    selectedSections.value.delete(sectionName)
  }
  // 触发响应式更新
  selectedSections.value = new Set(selectedSections.value)
}

// 单个编辑项目关联
const handleEdit = (sectionName, projectInfo) => {
  isBatchMode.value = false
  currentSectionName.value = sectionName
  currentProjectName.value = projectInfo.project_name
  dialogVisible.value = true
}

// 批量编辑
const handleBatchEdit = () => {
  if (selectedSections.value.size === 0) {
    ElMessage.warning('请先选择要修改的标段')
    return
  }

  isBatchMode.value = true
  currentSectionName.value = `${selectedSections.value.size} 个标段`
  currentProjectName.value = ''
  dialogVisible.value = true
}

// 确认项目选择
const handleProjectConfirm = async (projectInfo) => {
  if (isBatchMode.value) {
    // 批量模式：显示确认对话框
    try {
      await ElMessageBox.confirm(
        `确定要为 ${selectedSections.value.size} 个标段设置项目为"${projectInfo.project_name}"吗？`,
        '批量设置确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      // 用户确认后，批量更新
      handleBatchConfirm(projectInfo)
    } catch {
      // 用户取消
      console.log('用户取消批量设置')
    }
  } else {
    // 单个模式：直接更新
    emit('update', currentSectionName.value, projectInfo)
  }
}

// 批量确认更新
const handleBatchConfirm = (projectInfo) => {
  const sectionsArray = Array.from(selectedSections.value)

  // 为每个选中的标段更新项目信息
  sectionsArray.forEach(sectionName => {
    emit('update', sectionName, projectInfo)
  })

  // 显示成功提示
  ElMessage.success(`已成功为 ${sectionsArray.length} 个标段设置项目`)

  // 清空选中状态
  selectedSections.value.clear()
}
</script>

<style scoped>
.project-section-mapping {
  margin-bottom: 20px;
}

.mapping-card {
  border: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

/* 批量操作栏样式 */
.batch-operations {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #e4e7ed;
}

.batch-operations .left-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.batch-operations .right-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.selected-count {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

.mapping-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.mapping-item {
  display: flex;
  align-items: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  gap: 15px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.mapping-item:hover {
  background-color: #ecf5ff;
}

.mapping-item.selected {
  background-color: #ecf5ff;
  border-color: #409eff;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  min-width: 30px;
}

.section-name {
  min-width: 120px;
}

.arrow {
  font-size: 20px;
  color: #909399;
  font-weight: bold;
}

.project-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.project-name {
  font-size: 15px;
  color: #303133;
}

.builder-unit {
  font-size: 13px;
  color: #606266;
}

.actions {
  min-width: 80px;
  text-align: right;
}
</style>

