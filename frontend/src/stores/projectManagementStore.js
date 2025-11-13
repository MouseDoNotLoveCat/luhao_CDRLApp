import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useProjectManagementStore = defineStore('projectManagement', () => {
  // 状态
  const projects = ref([])
  const sections = ref([])
  const selectedProjectId = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const message = ref(null)
  
  // 分页
  const projectsPage = ref(1)
  const projectsPageSize = ref(20)
  const projectsTotal = ref(0)
  const sectionsPage = ref(1)
  const sectionsPageSize = ref(20)
  const sectionsTotal = ref(0)
  
  // 搜索
  const projectsSearch = ref('')
  const sectionsSearch = ref('')
  
  // 表单状态
  const projectFormVisible = ref(false)
  const sectionFormVisible = ref(false)
  const editingProject = ref(null)
  const editingSection = ref(null)
  
  // 计算属性
  const currentProject = computed(() => {
    return projects.value.find(p => p.id === selectedProjectId.value)
  })
  
  const hasSections = computed(() => {
    return sections.value.length > 0
  })
  
  // 获取项目列表
  const fetchProjects = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/projects', {
        params: {
          search: projectsSearch.value,
          limit: projectsPageSize.value,
          offset: (projectsPage.value - 1) * projectsPageSize.value
        }
      })
      console.log('API Response:', response)
      console.log('Response.data:', response.data)
      console.log('Response.total:', response.total)
      projects.value = response.data
      projectsTotal.value = response.total
      console.log('Projects updated:', projects.value)
    } catch (err) {
      error.value = err.response?.data?.detail || '获取项目列表失败'
      console.error('获取项目列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取标段列表
  const fetchSections = async () => {
    if (!selectedProjectId.value) {
      sections.value = []
      return
    }
    
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/projects/${selectedProjectId.value}/sections`, {
        params: {
          search: sectionsSearch.value,
          limit: sectionsPageSize.value,
          offset: (sectionsPage.value - 1) * sectionsPageSize.value
        }
      })
      sections.value = response.data
      sectionsTotal.value = response.total
    } catch (err) {
      error.value = err.response?.data?.detail || '获取标段列表失败'
      console.error('获取标段列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 创建项目
  const createProject = async (projectName, builderUnit) => {
    isLoading.value = true
    error.value = null
    try {
      await api.post('/projects', null, {
        params: {
          project_name: projectName,
          builder_unit: builderUnit
        }
      })
      message.value = '项目创建成功'
      projectFormVisible.value = false
      await fetchProjects()
    } catch (err) {
      error.value = err.response?.data?.detail || '创建项目失败'
      console.error('创建项目失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 更新项目
  const updateProject = async (projectId, projectName, builderUnit) => {
    isLoading.value = true
    error.value = null
    try {
      await api.put(`/projects/${projectId}`, null, {
        params: {
          project_name: projectName,
          builder_unit: builderUnit
        }
      })
      message.value = '项目修改成功'
      projectFormVisible.value = false
      editingProject.value = null
      await fetchProjects()
    } catch (err) {
      error.value = err.response?.data?.detail || '修改项目失败'
      console.error('修改项目失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除项目
  const deleteProject = async (projectId, cascade = false) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.delete(`/projects/${projectId}`, {
        params: { cascade }
      })
      
      if (response.success) {
        message.value = response.message
        if (selectedProjectId.value === projectId) {
          selectedProjectId.value = null
          sections.value = []
        }
        await fetchProjects()
      } else {
        return response
      }
    } catch (err) {
      error.value = err.response?.data?.detail || '删除项目失败'
      console.error('删除项目失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 创建标段
  const createSection = async (sectionData) => {
    isLoading.value = true
    error.value = null
    try {
      await api.post('/sections', null, {
        params: {
          project_id: selectedProjectId.value,
          ...sectionData
        }
      })
      message.value = '标段创建成功'
      sectionFormVisible.value = false
      await fetchSections()
    } catch (err) {
      error.value = err.response?.data?.detail || '创建标段失败'
      console.error('创建标段失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 更新标段
  const updateSection = async (sectionId, sectionData) => {
    isLoading.value = true
    error.value = null
    try {
      await api.put(`/sections/${sectionId}`, null, {
        params: sectionData
      })
      message.value = '标段修改成功'
      sectionFormVisible.value = false
      editingSection.value = null
      await fetchSections()
    } catch (err) {
      error.value = err.response?.data?.detail || '修改标段失败'
      console.error('修改标段失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除标段
  const deleteSection = async (sectionId) => {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/sections/${sectionId}`)
      message.value = '标段删除成功'
      await fetchSections()
    } catch (err) {
      error.value = err.response?.data?.detail || '删除标段失败'
      console.error('删除标段失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 选择项目
  const selectProject = (projectId) => {
    selectedProjectId.value = projectId
    sectionsPage.value = 1
    sectionsSearch.value = ''
    fetchSections()
  }
  
  // 打开项目表单
  const openProjectForm = (project = null) => {
    editingProject.value = project
    projectFormVisible.value = true
  }
  
  // 打开标段表单
  const openSectionForm = (section = null) => {
    editingSection.value = section
    sectionFormVisible.value = true
  }
  
  // 关闭表单
  const closeProjectForm = () => {
    projectFormVisible.value = false
    editingProject.value = null
  }
  
  const closeSectionForm = () => {
    sectionFormVisible.value = false
    editingSection.value = null
  }
  
  // 重置搜索
  const resetProjectsSearch = () => {
    projectsSearch.value = ''
    projectsPage.value = 1
    fetchProjects()
  }
  
  const resetSectionsSearch = () => {
    sectionsSearch.value = ''
    sectionsPage.value = 1
    fetchSections()
  }
  
  return {
    // 状态
    projects,
    sections,
    selectedProjectId,
    isLoading,
    error,
    message,
    projectsPage,
    projectsPageSize,
    projectsTotal,
    sectionsPage,
    sectionsPageSize,
    sectionsTotal,
    projectsSearch,
    sectionsSearch,
    projectFormVisible,
    sectionFormVisible,
    editingProject,
    editingSection,
    
    // 计算属性
    currentProject,
    hasSections,
    
    // 方法
    fetchProjects,
    fetchSections,
    createProject,
    updateProject,
    deleteProject,
    createSection,
    updateSection,
    deleteSection,
    selectProject,
    openProjectForm,
    openSectionForm,
    closeProjectForm,
    closeSectionForm,
    resetProjectsSearch,
    resetSectionsSearch
  }
})

