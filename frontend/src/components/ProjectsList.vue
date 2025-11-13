<template>
  <div class="projects-list-container">
    <!-- 标题和操作栏 -->
    <div class="list-header">
      <h2>项目一览表</h2>
      <el-button type="primary" @click="handleNewProject">
        <span>➕ 新建项目</span>
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="store.projectsSearch"
        placeholder="搜索项目名称或建设单位..."
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

    <!-- 项目表格 -->
    <el-table
      :data="store.projects"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'id', order: 'descending' }"
      @row-click="handleSelectProject"
    >
      <el-table-column prop="project_name" label="项目名称" min-width="200" />
      <el-table-column prop="builder_unit" label="建设单位" min-width="150" />
      <el-table-column prop="sections_count" label="标段数量" width="100" align="center" />
      <el-table-column label="操作" width="280" align="center">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="primary"
              size="small"
              @click.stop="handleSelectProject(row)"
            >
              查看标段
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click.stop="handleEditProject(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click.stop="handleDeleteProject(row)"
            >
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="store.projectsPage"
        v-model:page-size="store.projectsPageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="store.projectsTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @change="store.fetchProjects"
      />
    </div>
  </div>
</template>

<script setup>
import { useProjectManagementStore } from '../stores/projectManagementStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const store = useProjectManagementStore()

const emit = defineEmits(['select-project', 'edit-project'])

const handleSearch = () => {
  store.projectsPage = 1
  store.fetchProjects()
}

const handleNewProject = () => {
  store.openProjectForm()
  emit('edit-project', null)
}

const handleSelectProject = (row) => {
  store.selectProject(row.id)
  emit('select-project', row)
}

const handleEditProject = (row) => {
  store.openProjectForm(row)
  emit('edit-project', row)
}

const handleDeleteProject = (row) => {
  ElMessageBox.confirm(
    `确定要删除项目"${row.project_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const result = await store.deleteProject(row.id, false)
    if (result && !result.success) {
      // 项目下有标段，询问是否级联删除
      ElMessageBox.confirm(
        result.message,
        '级联删除确认',
        {
          confirmButtonText: '级联删除',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        store.deleteProject(row.id, true)
        ElMessage.success('项目及其标段已删除')
      }).catch(() => {
        ElMessage.info('已取消删除')
      })
    } else {
      ElMessage.success('项目已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}
</script>

<style scoped>
.projects-list-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
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

:deep(.el-table__row) {
  cursor: pointer;
  transition: background-color 0.3s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-buttons :deep(.el-button) {
  margin: 0;
}
</style>

