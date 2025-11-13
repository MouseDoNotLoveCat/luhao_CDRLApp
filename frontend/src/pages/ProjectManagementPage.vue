<template>
  <div class="project-management-page">
    <!-- 消息提示 -->
    <el-alert
      v-if="store.message"
      :title="store.message"
      type="success"
      closable
      @close="store.message = null"
      class="message-alert"
    />

    <!-- 两层结构：项目列表 / 标段列表 -->
    <div v-if="!store.selectedProjectId" class="projects-view">
      <ProjectsList
        @select-project="handleSelectProject"
        @edit-project="handleEditProject"
      />
    </div>

    <div v-else class="sections-view">
      <SectionsList
        @back="handleBackToProjects"
        @edit-section="handleEditSection"
      />
    </div>

    <!-- 项目表单对话框 -->
    <ProjectForm />

    <!-- 标段表单对话框 -->
    <SectionForm />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useProjectManagementStore } from '../stores/projectManagementStore'
import ProjectsList from '../components/ProjectsList.vue'
import SectionsList from '../components/SectionsList.vue'
import ProjectForm from '../components/ProjectForm.vue'
import SectionForm from '../components/SectionForm.vue'

const store = useProjectManagementStore()

onMounted(() => {
  // 初始化加载项目列表
  store.fetchProjects()
})

const handleSelectProject = (project) => {
  console.log('选择项目:', project)
}

const handleEditProject = (project) => {
  console.log('编辑项目:', project)
}

const handleBackToProjects = () => {
  store.selectedProjectId = null
  store.sections = []
}

const handleEditSection = (section) => {
  console.log('编辑标段:', section)
}
</script>

<style scoped>
.project-management-page {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.message-alert {
  margin-bottom: 20px;
}

.projects-view,
.sections-view {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

