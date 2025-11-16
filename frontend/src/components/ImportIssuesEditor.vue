<template>
  <div class="import-issues-editor">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" style="margin-bottom: 20px">
      <el-breadcrumb-item @click="goBack" style="cursor: pointer">
        ← 返回
      </el-breadcrumb-item>
      <el-breadcrumb-item>编辑问题</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 统计信息 -->
    <div class="statistics" style="margin-bottom: 20px">
      <el-statistic title="总问题数" :value="issues.length" />
      <el-statistic title="已选择" :value="selectedCount" />
      <el-statistic title="已修改" :value="modifiedCount" />
    </div>

    <!-- 问题编辑表格 -->
    <el-table
      :data="issues"
      stripe
      border
      max-height="600px"
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <!-- 选择框 -->
      <el-table-column type="selection" width="50" />

      <!-- 序号 -->
      <el-table-column type="index" label="序号" width="60" />

      <!-- 标段名称（可编辑，带下拉） -->
      <el-table-column label="标段" width="150">
        <template #default="{ row, $index }">
          <el-select
            :model-value="row.section_name"
            @change="(val) => updateIssue($index, 'section_name', val)"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入标段"
            style="width: 100%"
          >
            <el-option
              v-for="section in getSectionOptions()"
              :key="section"
              :label="section"
              :value="section"
            />
          </el-select>
        </template>
      </el-table-column>

      <!-- 工点名称（可编辑） -->
      <el-table-column label="工点" width="120">
        <template #default="{ row, $index }">
          <el-input
            :model-value="row.site_name"
            @change="(val) => updateIssue($index, 'site_name', val)"
            placeholder="输入工点名称"
            size="small"
          />
        </template>
      </el-table-column>

      <!-- 问题描述（可编辑） -->
      <el-table-column label="问题描述" width="200">
        <template #default="{ row, $index }">
          <el-input
            :model-value="row.description"
            @change="(val) => updateIssue($index, 'description', val)"
            type="textarea"
            :rows="2"
            placeholder="输入问题描述"
            size="small"
          />
        </template>
      </el-table-column>

      <!-- 问题类别（三层级联） -->
      <el-table-column label="问题类别" width="150">
        <template #default="{ row, $index }">
          <div style="display: flex; flex-direction: column; gap: 8px">
            <el-select
              :model-value="row.issue_category"
              @change="(val) => handleCategoryChange($index, val)"
              placeholder="一级分类"
              size="small"
              style="width: 100%"
            >
              <el-option
                v-for="cat in primaryCategories"
                :key="cat"
                :label="cat"
                :value="cat"
              />
            </el-select>
            <el-select
              :model-value="row.issue_type_level1"
              @change="(val) => handleLevel1Change($index, val)"
              :disabled="!row.issue_category"
              placeholder="二级分类"
              size="small"
              style="width: 100%"
            >
              <el-option
                v-for="sub in getSecondaryCategories(row.issue_category)"
                :key="sub"
                :label="sub"
                :value="sub"
              />
            </el-select>
            <el-select
              :model-value="row.issue_type_level2"
              @change="(val) => updateIssue($index, 'issue_type_level2', val)"
              :disabled="!row.issue_type_level1"
              placeholder="三级分类"
              size="small"
              style="width: 100%"
            >
              <el-option
                v-for="detail in getTertiaryCategories(row.issue_type_level1)"
                :key="detail"
                :label="detail"
                :value="detail"
              />
            </el-select>
          </div>
        </template>
      </el-table-column>

      <!-- 严重程度（可编辑） -->
      <el-table-column label="严重程度" width="120">
        <template #default="{ row, $index }">
          <el-select
            :model-value="row.severity"
            @change="(val) => updateIssue($index, 'severity', val)"
            placeholder="选择严重程度"
            size="small"
            style="width: 100%"
          >
            <el-option label="1 - 轻微" :value="1" />
            <el-option label="2 - 一般" :value="2" />
            <el-option label="3 - 中等" :value="3" />
            <el-option label="4 - 严重" :value="4" />
            <el-option label="5 - 极严重" :value="5" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <!-- 操作按钮 -->
    <div class="action-buttons" style="margin-top: 20px">
      <el-button @click="goBack">返回</el-button>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSave">保存修改</el-button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useImportStore } from '@/stores/importStore'
import { useRouter } from 'vue-router'
import {
  getPrimaryCategories,
  getSecondaryCategories,
  getTertiaryCategories
} from '@/config/issueCategories'
import { ElMessage } from 'element-plus'

const router = useRouter()
const importStore = useImportStore()

const issues = computed(() => importStore.recognizedIssues)
const primaryCategories = ref(getPrimaryCategories())
const sectionOptions = ref([])

const selectedCount = computed(() => {
  return importStore.selectedIssueIds.size
})

const modifiedCount = computed(() => {
  return importStore.modifiedRecords.size
})

// 获取标段选项
const getSectionOptions = () => {
  const sections = new Set()
  issues.value.forEach(issue => {
    if (issue.section_name) {
      sections.add(issue.section_name)
    }
  })
  return Array.from(sections).sort()
}

// 更新问题字段
const updateIssue = (index, fieldName, value) => {
  importStore.updateRecognizedIssue(index, fieldName, value)
}

// 处理一级分类变化
const handleCategoryChange = (index, value) => {
  updateIssue(index, 'issue_category', value)
  updateIssue(index, 'issue_type_level1', '')
  updateIssue(index, 'issue_type_level2', '')
}

// 处理二级分类变化
const handleLevel1Change = (index, value) => {
  updateIssue(index, 'issue_type_level1', value)
  updateIssue(index, 'issue_type_level2', '')
}

// 处理问题选择
const handleSelectionChange = (selection) => {
  // 清空之前的选择
  importStore.selectedIssueIds.clear()
  // 添加新的选择（使用问题在数组中的索引）
  selection.forEach((issue) => {
    const index = issues.value.indexOf(issue)
    if (index !== -1) {
      importStore.selectedIssueIds.add(index)
    }
  })
}

// 返回
const goBack = () => {
  importStore.viewMode = 'preview-notices'
}

// 取消
const handleCancel = () => {
  importStore.resetRecognition()
  router.push('/import')
}

// 保存修改
const handleSave = () => {
  // 检查是否选择了问题
  if (importStore.selectedIssueIds.size === 0) {
    ElMessage.warning('请先选择要导入的问题')
    return
  }
  ElMessage.success('修改已保存')
  // 直接进入确认界面
  importStore.viewMode = 'confirm'
}

onMounted(() => {
  // 初始化标段选项
  sectionOptions.value = getSectionOptions()
})
</script>

<style scoped>
.import-issues-editor {
  padding: 20px;
}

.statistics {
  display: flex;
  gap: 40px;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
</style>

