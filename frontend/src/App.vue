<template>
  <div class="app-container">
    <!-- 顶部标题栏 -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">铁路工程质量安全监督问题库管理平台</h1>
      </div>
    </header>

    <!-- 主容器 -->
    <div class="app-main">
      <!-- 左侧菜单 -->
      <aside class="app-sidebar">
        <nav class="menu">
          <div 
            class="menu-item" 
            :class="{ active: activeMenu === 'import' }"
            @click="activeMenu = 'import'"
          >
            <span class="menu-icon">📥</span>
            <span class="menu-text">导入监督检查通知书</span>
          </div>
          <div
            class="menu-item"
            :class="{ active: activeMenu === 'issues' }"
            @click="activeMenu = 'issues'"
          >
            <span class="menu-icon">📊</span>
            <span class="menu-text">工程质量安全问题库</span>
          </div>
          <div
            class="menu-item"
            :class="{ active: activeMenu === 'project-management' }"
            @click="activeMenu = 'project-management'"
          >
            <span class="menu-icon">🏗️</span>
            <span class="menu-text">项目与标段管理</span>
          </div>
          <div
            class="menu-item"
            :class="{ active: activeMenu === 'notice-management' }"
            @click="activeMenu = 'notice-management'"
          >
            <span class="menu-icon">📋</span>
            <span class="menu-text">通知书管理</span>
          </div>
        </nav>
      </aside>

      <!-- 右侧内容区 -->
      <main class="app-content">
        <!-- 导入页面 -->
        <ImportPage v-if="activeMenu === 'import'" @show-detail="showIssueDetail" />

        <!-- 问题库页面 -->
        <IssuesPage v-if="activeMenu === 'issues'" />

        <!-- 问题详情页面 -->
        <IssueDetailPage v-if="activeMenu === 'detail'" :issue-id="selectedIssueId" @back="goBackToImport" />

        <!-- 项目与标段管理页面 -->
        <ProjectManagementPage v-if="activeMenu === 'project-management'" />

        <!-- 通知书管理页面 -->
        <NoticeManagementPage v-if="activeMenu === 'notice-management'" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ImportPage from './pages/ImportPage.vue'
import IssuesPage from './pages/IssuesPage.vue'
import IssueDetailPage from './pages/IssueDetailPage.vue'
import ProjectManagementPage from './pages/ProjectManagementPage.vue'
import NoticeManagementPage from './pages/NoticeManagementPage.vue'

const activeMenu = ref('import')
const selectedIssueId = ref(null)

const showIssueDetail = (issueId) => {
  console.log('🔴 App.vue: showIssueDetail 被调用，issueId:', issueId)
  selectedIssueId.value = issueId
  activeMenu.value = 'detail'
}

const goBackToImport = () => {
  console.log('🔴 App.vue: goBackToImport 被调用')
  activeMenu.value = 'import'
  selectedIssueId.value = null
}
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.app-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.05);
}

.menu {
  padding: 20px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #333;
  font-size: 14px;
}

.menu-item:hover {
  background-color: #f5f5f5;
  color: #667eea;
}

.menu-item.active {
  background-color: #f0f4ff;
  color: #667eea;
  border-left: 3px solid #667eea;
  padding-left: 17px;
}

.menu-icon {
  margin-right: 12px;
  font-size: 16px;
}

.menu-text {
  flex: 1;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-sidebar {
    width: 180px;
  }
  
  .app-title {
    font-size: 18px;
  }
}
</style>

