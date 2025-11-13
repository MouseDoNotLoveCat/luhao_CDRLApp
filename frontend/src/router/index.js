import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/import'
  },
  {
    path: '/import',
    name: 'Import',
    component: () => import('../pages/ImportPage.vue')
  },
  {
    path: '/issues',
    name: 'Issues',
    component: () => import('../pages/IssuesPage.vue')
  },
  {
    path: '/issues/:id',
    name: 'IssueDetail',
    component: () => import('../pages/IssueDetailPage.vue')
  },
  {
    path: '/project-management',
    name: 'ProjectManagement',
    component: () => import('../pages/ProjectManagementPage.vue')
  },
  {
    path: '/notice-management',
    name: 'NoticeManagement',
    component: () => import('../pages/NoticeManagementPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

