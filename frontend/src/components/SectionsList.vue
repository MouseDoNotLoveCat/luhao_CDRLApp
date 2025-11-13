<template>
  <div class="sections-list-container">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-button link @click="handleBack">
        ← 返回项目列表
      </el-button>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-current">{{ currentProject?.project_name }}</span>
    </div>

    <!-- 项目信息卡片 -->
    <div class="project-info-card">
      <div class="info-item">
        <span class="label">项目名称：</span>
        <span class="value">{{ currentProject?.project_name }}</span>
      </div>
      <div class="info-item">
        <span class="label">建设单位：</span>
        <span class="value">{{ currentProject?.builder_unit || '未填写' }}</span>
      </div>
      <div class="info-item">
        <span class="label">标段数量：</span>
        <span class="value">{{ currentProject?.sections_count || 0 }}</span>
      </div>
    </div>

    <!-- 标题和操作栏 -->
    <div class="list-header">
      <h2>标段列表</h2>
      <el-button type="primary" @click="handleNewSection">
        <span>➕ 新建标段</span>
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="store.sectionsSearch"
        placeholder="搜索标段名称或单位..."
        clearable
        @input="handleSearch"
      >
        <template #suffix>
          <el-icon class="is-loading" v-if="store.isLoading">
            <Loading />
          </el-icon>
        </template>
      </el-input>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="store.error"
      :title="store.error"
      type="error"
      closable
      @close="store.error = null"
      class="error-alert"
    />

    <!-- 标段表格 -->
    <el-table
      :data="store.sections"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'section_name', order: 'ascending' }"
    >
      <el-table-column prop="section_name" label="标段名称" min-width="150" />
      <el-table-column prop="contractor_unit" label="施工单位" min-width="150" />
      <el-table-column prop="supervisor_unit" label="监理单位" min-width="150" />
      <el-table-column prop="designer_unit" label="设计单位" min-width="150" />
      <el-table-column prop="testing_unit" label="第三方检测单位" min-width="150" />
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <el-button
            type="warning"
            size="small"
            @click="handleEditSection(row)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="handleDeleteSection(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="store.sectionsPage"
        v-model:page-size="store.sectionsPageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="store.sectionsTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @change="store.fetchSections"
      />
    </div>
  </div>
</template>

<script setup>
import { useProjectManagementStore } from '../stores/projectManagementStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const store = useProjectManagementStore()

const emit = defineEmits(['back', 'edit-section'])

const currentProject = () => store.currentProject

const handleBack = () => {
  store.selectedProjectId = null
  store.sections = []
  emit('back')
}

const handleSearch = () => {
  store.sectionsPage = 1
  store.fetchSections()
}

const handleNewSection = () => {
  store.openSectionForm()
  emit('edit-section', null)
}

const handleEditSection = (row) => {
  store.openSectionForm(row)
  emit('edit-section', row)
}

const handleDeleteSection = (row) => {
  ElMessageBox.confirm(
    `确定要删除标段"${row.section_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    store.deleteSection(row.id)
    ElMessage.success('标段已删除')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}
</script>

<style scoped>
.sections-list-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.breadcrumb-separator {
  margin: 0 10px;
  color: #ccc;
}

.breadcrumb-current {
  color: #333;
  font-weight: 500;
}

.project-info-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  font-weight: 500;
  color: #666;
  margin-right: 10px;
  min-width: 100px;
}

.info-item .value {
  color: #333;
  flex: 1;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.search-bar {
  margin-bottom: 20px;
}

.error-alert {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>

