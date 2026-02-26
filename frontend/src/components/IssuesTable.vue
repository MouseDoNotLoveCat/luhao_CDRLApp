<template>
  <div class="issues-table-container">
    <!-- 搜索和筛选 -->
    <div class="table-toolbar">
      <el-button type="primary" @click="toggleEditMode">
        {{ isEditMode ? '取消编辑' : '编辑' }}
      </el-button>
      <el-input
        v-model="searchText"
        placeholder="搜索项目名称、工点名称..."
        style="width: 300px"
        clearable
      />
      <el-select
        v-model="filterPrimaryCategory"
        placeholder="一级分类"
        clearable
        style="width: 150px; margin-left: 12px"
        @change="handlePrimaryCategoryChange"
      >
        <el-option label="工程质量" value="工程质量" />
        <el-option label="施工安全" value="施工安全" />
        <el-option label="管理行为" value="管理行为" />
        <el-option label="其它" value="其它" />
      </el-select>

      <el-select
        v-model="filterSecondaryCategory"
        placeholder="二级分类"
        clearable
        style="width: 150px; margin-left: 12px"
        :disabled="!filterPrimaryCategory"
      >
        <el-option
          v-for="category in availableSecondaryCategories"
          :key="category"
          :label="category"
          :value="category"
        />
      </el-select>

      <el-button
        type="success"
        style="margin-left: 12px"
        @click="openExportDialog"
      >
        导出 Excel
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table
      :data="filteredIssues"
      stripe
      style="width: 100%; margin-top: 16px"
      highlight-current-row
    >
      <!-- 1. 序号 -->
      <el-table-column type="index" label="序号" width="60" />

      <!-- 2. 检查时间 -->
      <el-table-column prop="inspection_date" label="检查时间" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'inspection_date')">
            <el-date-picker
              v-model="inlineCellEditingValue"
              type="date"
              placeholder="选择日期"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'inspection_date')"
              @blur="saveInlineCellEdit(row, 'inspection_date')"
              @click.stop
              style="width: 100%"
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'inspection_date')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.inspection_date }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 3. 检查单位 -->
      <el-table-column prop="inspection_unit" label="检查单位" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'inspection_unit')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'inspection_unit')"
              @blur="saveInlineCellEdit(row, 'inspection_unit')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'inspection_unit')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.inspection_unit }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 4. 检查项目 -->
      <el-table-column prop="project_name" label="检查项目" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'project_name')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'project_name')"
              @blur="saveInlineCellEdit(row, 'project_name')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'project_name')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.project_name }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 5. 标段 -->
      <el-table-column prop="section_name" label="标段" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'section_name')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'section_name')"
              @blur="saveInlineCellEdit(row, 'section_name')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'section_name')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.section_name }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 施工单位 -->
      <el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <div style="padding: 8px; min-height: 32px; display: flex; align-items: center;">
            {{ row.contractor || '未知施工单位' }}
          </div>
        </template>
      </el-table-column>

      <!-- 监理单位 -->
      <el-table-column prop="supervisor" label="监理单位" width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <div style="padding: 8px; min-height: 32px; display: flex; align-items: center;">
            {{ row.supervisor || '未知监理单位' }}
          </div>
        </template>
      </el-table-column>


      <!-- 6. 检查工点 -->
      <el-table-column prop="site_name" label="检查工点" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'site_name')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'site_name')"
              @blur="saveInlineCellEdit(row, 'site_name')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'site_name')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.site_name }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 7. 问题描述 -->
      <el-table-column prop="description" label="问题描述" min-width="150">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'description')">
            <el-input
              v-model="inlineCellEditingValue"
              type="textarea"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'description')"
              @blur="saveInlineCellEdit(row, 'description')"
              @click.stop
              autofocus
              :rows="2"
            />
          </template>
          <template v-else>
            <span class="description-text" @click.stop="startInlineCellEdit(row, 'description')" style="cursor: pointer;">
              {{ truncateText(row.description, 40) }}
            </span>
          </template>
        </template>
      </el-table-column>

      <!-- 8. 问题类别 -->
      <el-table-column prop="issue_category" label="问题类别" width="100">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'issue_category')">
            <el-select
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'issue_category')"
              @blur="saveInlineCellEdit(row, 'issue_category')"
              @click.stop
              @change="() => {
                row.issue_type_level1 = ''
                row.issue_type_level2 = ''
              }"
              style="width: 100%"
            >
              <el-option
                v-for="category in inlinePrimaryCategories"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'issue_category')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.issue_category }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 9. 问题子类1 -->
      <el-table-column prop="issue_type_level1" label="问题子类1" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'issue_type_level1')">
            <el-select
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'issue_type_level1')"
              @blur="saveInlineCellEdit(row, 'issue_type_level1')"
              @click.stop
              @change="() => {
                row.issue_type_level2 = ''
              }"
              style="width: 100%"
            >
              <el-option
                v-for="category in getInlineSecondaryCategories(row.issue_category)"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'issue_type_level1')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.issue_type_level1 }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 10. 问题子类2 -->
      <el-table-column prop="issue_type_level2" label="问题子类2" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'issue_type_level2')">
            <el-select
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'issue_type_level2')"
              @blur="saveInlineCellEdit(row, 'issue_type_level2')"
              @click.stop
              style="width: 100%"
            >
              <el-option
                v-for="category in getInlineTertiaryCategories(row.issue_type_level1)"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'issue_type_level2')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.issue_type_level2 }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 11. 问题等级 -->
      <el-table-column prop="severity" label="问题等级" width="100">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'severity')">
            <el-select
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'severity')"
              @blur="saveInlineCellEdit(row, 'severity')"
              @click.stop
              style="width: 100%"
            >
              <el-option
                v-for="severity in severityOptions"
                :key="severity"
                :label="severity"
                :value="severity"
              />
            </el-select>
          </template>
          <template v-else>
            <el-tag :type="getSeverityType(row.severity)" @click.stop="startInlineCellEdit(row, 'severity')" style="cursor: pointer;">
              {{ row.severity }}
            </el-tag>
          </template>
        </template>
      </el-table-column>

      <!-- 12. 整改要求/措施 -->
      <el-table-column prop="rectification_requirements" label="整改要求/措施" min-width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'rectification_requirements')">
            <el-input
              v-model="inlineCellEditingValue"
              type="textarea"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'rectification_requirements')"
              @blur="saveInlineCellEdit(row, 'rectification_requirements')"
              @click.stop
              autofocus
              :rows="2"
            />
          </template>
          <template v-else>
            <span class="description-text" @click.stop="startInlineCellEdit(row, 'rectification_requirements')" style="cursor: pointer;">
              {{ truncateText(row.rectification_requirements, 30) }}
            </span>
          </template>
        </template>
      </el-table-column>

      <!-- 13. 整改期限 -->
      <el-table-column prop="rectification_deadline" label="整改期限" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'rectification_deadline')">
            <el-date-picker
              v-model="inlineCellEditingValue"
              type="date"
              placeholder="选择日期"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'rectification_deadline')"
              @blur="saveInlineCellEdit(row, 'rectification_deadline')"
              @click.stop
              style="width: 100%"
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'rectification_deadline')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.rectification_deadline }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 14. 整改责任单位 -->
      <el-table-column prop="responsible_unit" label="整改责任单位" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'responsible_unit')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'responsible_unit')"
              @blur="saveInlineCellEdit(row, 'responsible_unit')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'responsible_unit')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.responsible_unit }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 15. 整改责任人 -->
      <el-table-column prop="responsible_person" label="整改责任人" width="100">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'responsible_person')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'responsible_person')"
              @blur="saveInlineCellEdit(row, 'responsible_person')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'responsible_person')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.responsible_person }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 16. 销号日期 -->
      <el-table-column prop="closure_date" label="销号日期" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'closure_date')">
            <el-date-picker
              v-model="inlineCellEditingValue"
              type="date"
              placeholder="选择日期"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'closure_date')"
              @blur="saveInlineCellEdit(row, 'closure_date')"
              @click.stop
              style="width: 100%"
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'closure_date')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.closure_date }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 17. 销号人员 -->
      <el-table-column prop="closure_personnel" label="销号人员" width="100">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'closure_personnel')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'closure_personnel')"
              @blur="saveInlineCellEdit(row, 'closure_personnel')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'closure_personnel')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.closure_personnel }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 18. 销号状态 -->
      <el-table-column prop="closure_status" label="销号状态" width="100">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'closure_status')">
            <el-input
              v-model="inlineCellEditingValue"
              size="small"
              @keydown="handleInlineCellKeydown($event, row, 'closure_status')"
              @blur="saveInlineCellEdit(row, 'closure_status')"
              @click.stop
              autofocus
            />
          </template>
          <template v-else>
            <div @click.stop="startInlineCellEdit(row, 'closure_status')" style="cursor: pointer; padding: 8px; min-height: 32px; display: flex; align-items: center;">
              {{ row.closure_status }}
            </div>
          </template>
        </template>
      </el-table-column>

      <!-- 19. 是否下发整改通知书 -->
      <el-table-column prop="is_rectification_notice" label="下发整改通知书" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'is_rectification_notice')">
            <el-checkbox
              v-model="inlineCellEditingValue"
              @keydown="handleInlineCellKeydown($event, row, 'is_rectification_notice')"
              @blur="saveInlineCellEdit(row, 'is_rectification_notice')"
              @click.stop
            />
          </template>
          <template v-else>
            <el-tag :type="row.is_rectification_notice ? 'success' : 'info'" @click.stop="startInlineCellEdit(row, 'is_rectification_notice')" style="cursor: pointer;">
              {{ row.is_rectification_notice ? '是' : '否' }}
            </el-tag>
          </template>
        </template>
      </el-table-column>

      <!-- 20. 是否认定不良行为 -->
      <el-table-column prop="is_bad_behavior_notice" label="认定不良行为" width="120">
        <template #default="{ row }">
          <template v-if="isInlineCellEditing(row, 'is_bad_behavior_notice')">
            <el-checkbox
              v-model="inlineCellEditingValue"
              @keydown="handleInlineCellKeydown($event, row, 'is_bad_behavior_notice')"
              @blur="saveInlineCellEdit(row, 'is_bad_behavior_notice')"
              @click.stop
            />
          </template>
          <template v-else>
            <el-tag :type="row.is_bad_behavior_notice ? 'danger' : 'info'" @click.stop="startInlineCellEdit(row, 'is_bad_behavior_notice')" style="cursor: pointer;">
              {{ row.is_bad_behavior_notice ? '是' : '否' }}
            </el-tag>
          </template>
        </template>
      </el-table-column>

      <!-- 操作列 -->
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click.stop="handleViewDetail(row)">
            详情
          </el-button>
          <el-button v-if="isEditMode" type="warning" link @click.stop="handleEditRow(row)">
            编辑
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalFilteredIssues"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑问题"
      width="70%"
      @close="resetEditForm"
    >
      <el-form
        v-if="editingIssue"
        :model="editingIssue"
        label-width="120px"
        class="edit-form"
      >
        <!-- 基本信息 -->
        <el-form-item label="问题编号">
          <el-input v-model="editingIssue.issue_number" disabled />
        </el-form-item>

        <el-form-item label="检查时间">
          <el-date-picker
            v-model="editingIssue.inspection_date"
            type="date"
            placeholder="选择日期"
          />
        </el-form-item>

        <el-form-item label="检查单位">
          <el-input v-model="editingIssue.inspection_unit" />
        </el-form-item>

        <el-form-item label="检查项目">
          <el-input v-model="editingIssue.project_name" disabled />
        </el-form-item>

        <el-form-item label="标段">
          <el-input v-model="editingIssue.section_name" disabled />
        </el-form-item>

        <!-- 新增：施工单位/监理单位（默认可编辑，初始值来自解析结果，空则显示占位） -->
        <el-form-item label="施工单位">
          <el-input v-model="editingIssue.contractor" placeholder="未知施工单位" />
        </el-form-item>
        <el-form-item label="监理单位">
          <el-input v-model="editingIssue.supervisor" placeholder="未知监理单位" />
        </el-form-item>

        <el-form-item label="检查工点">
          <el-input v-model="editingIssue.site_name" />
        </el-form-item>

        <!-- 问题分类 -->
        <el-form-item label="问题类别">
          <el-select
            v-model="editingIssue.issue_category"
            placeholder="选择问题类别"
            @change="handleCategoryChange"
          >
            <el-option label="工程质量" value="工程质量" />
            <el-option label="施工安全" value="施工安全" />
            <el-option label="管理行为" value="管理行为" />
            <el-option label="其它" value="其它" />
          </el-select>
        </el-form-item>

        <el-form-item label="问题子类1">
          <el-select
            v-model="editingIssue.issue_type_level1"
            placeholder="选择二级分类"
            :disabled="!editingIssue.issue_category"
            @change="handleSecondaryChange"
          >
            <el-option
              v-for="cat in availableEditSecondaryCategories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="问题子类2">
          <el-select
            v-model="editingIssue.issue_type_level2"
            placeholder="选择三级分类"
            :disabled="!editingIssue.issue_type_level1"
          >
            <el-option
              v-for="cat in availableEditTertiaryCategories"
              :key="cat"
              :label="cat"
              :value="cat"
            />
          </el-select>
        </el-form-item>

        <!-- 问题描述 -->
        <el-form-item label="问题描述">
          <el-input
            v-model="editingIssue.description"
            type="textarea"
            rows="3"
          />
        </el-form-item>

        <el-form-item label="问题等级">
          <el-select v-model="editingIssue.severity" placeholder="选择等级">
            <el-option label="1" :value="1" />
            <el-option label="2" :value="2" />
            <el-option label="3" :value="3" />
            <el-option label="4" :value="4" />
            <el-option label="5" :value="5" />
          </el-select>
        </el-form-item>

        <!-- 整改信息 -->
        <el-form-item label="整改要求/措施">
          <el-input
            v-model="editingIssue.rectification_requirements"
            type="textarea"
            rows="3"
          />
        </el-form-item>

        <el-form-item label="整改期限">
          <el-date-picker
            v-model="editingIssue.rectification_deadline"
            type="date"
            placeholder="选择日期"
          />
        </el-form-item>

        <el-form-item label="整改责任单位">
          <el-input v-model="editingIssue.responsible_unit" />
        </el-form-item>

        <el-form-item label="整改责任人">
          <el-input v-model="editingIssue.responsible_person" />
        </el-form-item>

        <!-- 销号信息 -->
        <el-form-item label="销号日期">
          <el-date-picker
            v-model="editingIssue.closure_date"
            type="date"
            placeholder="选择日期"
          />
        </el-form-item>

        <el-form-item label="销号人员">
          <el-input v-model="editingIssue.closure_personnel" />
        </el-form-item>

        <el-form-item label="销号状态">
          <el-input v-model="editingIssue.closure_status" />
        </el-form-item>

        <!-- 标志位 -->
        <el-form-item label="下发整改通知书">
          <el-checkbox v-model="editingIssue.is_rectification_notice" />
        </el-form-item>

        <el-form-item label="认定不良行为">
          <el-checkbox v-model="editingIssue.is_bad_behavior_notice" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEditedIssue">保存</el-button>
      </template>
    </el-dialog>

    <!-- 导出 Excel 对话框 -->
    <el-dialog
      v-model="exportDialogVisible"
      title="导出 Excel 表格"
      width="520px"
    >
      <div style="margin-bottom: 12px; color: #606266; font-size: 13px;">
        当前筛选结果共 <strong>{{ allFilteredIssues.length }}</strong> 条记录，请选择要导出的字段：
      </div>

      <el-checkbox
        v-model="exportSelectAll"
        :indeterminate="exportIndeterminate"
        @change="handleExportSelectAll"
        style="margin-bottom: 8px; font-weight: 600;"
      >全选</el-checkbox>

      <el-divider style="margin: 8px 0;" />

      <el-checkbox-group v-model="exportSelectedFields" style="display: flex; flex-wrap: wrap; gap: 8px 0;">
        <el-checkbox
          v-for="field in exportFieldOptions"
          :key="field.key"
          :value="field.key"
          style="width: 50%; margin-right: 0;"
        >{{ field.label }}</el-checkbox>
      </el-checkbox-group>

      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="exportSelectedFields.length === 0"
          @click="doExport"
        >导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import { getSecondaryCategories, getTertiaryCategories } from '../config/issueCategories'

const props = defineProps({
  issues: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['row-click', 'edit-row'])

const searchText = ref('')
const filterPrimaryCategory = ref('')
const filterSecondaryCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const isEditMode = ref(false)
const editDialogVisible = ref(false)
const editingIssue = ref(null)
const editingIssueIndex = ref(-1)

// 单元格直接编辑相关状态
const inlineCellEditingId = ref(null) // 正在编辑的单元格 ID (格式: "rowId_fieldName")
const inlineCellEditingValue = ref('') // 正在编辑的单元格值
const inlineCellEditingField = ref('') // 正在编辑的字段名

// 根据选中的一级分类，获取可用的二级分类
const availableSecondaryCategories = computed(() => {
  if (!filterPrimaryCategory.value) {
    return []
  }
  return getSecondaryCategories(filterPrimaryCategory.value)
})

// 当一级分类改变时，重置二级分类
const handlePrimaryCategoryChange = () => {
  filterSecondaryCategory.value = ''
}

// 获取过滤后的所有问题（不分页）
const allFilteredIssues = computed(() => {
  let filtered = props.issues

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(issue =>
      (issue.project_name?.toLowerCase().includes(search)) ||
      (issue.site_name?.toLowerCase().includes(search)) ||
      (issue.description?.toLowerCase().includes(search))
    )
  }

  // 一级分类过滤
  if (filterPrimaryCategory.value) {
    filtered = filtered.filter(issue =>
      issue.issue_category === filterPrimaryCategory.value
    )
  }

  // 二级分类过滤
  if (filterSecondaryCategory.value) {
    filtered = filtered.filter(issue =>
      issue.issue_type_level1 === filterSecondaryCategory.value
    )
  }

  return filtered
})

// 获取总数（用于分页）
const totalFilteredIssues = computed(() => allFilteredIssues.value.length)

// 获取当前页的问题（分页）
const filteredIssues = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return allFilteredIssues.value.slice(start, end)
})

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const getSeverityType = (severity) => {
  const typeMap = {
    '严重': 'danger',
    '一般': 'warning',
    '轻微': 'info'
  }
  return typeMap[severity] || 'info'
}

// ── 导出 Excel ────────────────────────────────────────────────────────────
const exportFieldOptions = [
  { key: 'inspection_date',      label: '检查时间' },
  { key: 'inspection_unit',      label: '检查单位' },
  { key: 'project_name',         label: '检查项目' },
  { key: 'section_name',         label: '标段' },
  { key: 'contractor',           label: '施工单位' },
  { key: 'supervisor',           label: '监理单位' },
  { key: 'site_name',            label: '工点名称' },
  { key: 'description',          label: '问题描述' },
  { key: 'issue_category',       label: '一级分类' },
  { key: 'issue_type_level1',    label: '二级分类' },
  { key: 'issue_type_level2',    label: '三级分类' },
  { key: 'severity',             label: '严重程度' },
  { key: 'rectification_deadline', label: '整改期限' },
  { key: 'is_rectification',     label: '是否下发整改通知单' },
]

const exportDialogVisible = ref(false)
const exportSelectedFields = ref(exportFieldOptions.map(f => f.key))

const exportSelectAll = computed({
  get: () => exportSelectedFields.value.length === exportFieldOptions.length,
  set: () => {}
})
const exportIndeterminate = computed(() =>
  exportSelectedFields.value.length > 0 &&
  exportSelectedFields.value.length < exportFieldOptions.length
)

const handleExportSelectAll = (val) => {
  exportSelectedFields.value = val ? exportFieldOptions.map(f => f.key) : []
}

const openExportDialog = () => {
  // 每次打开时重置为全选
  exportSelectedFields.value = exportFieldOptions.map(f => f.key)
  exportDialogVisible.value = true
}

const doExport = () => {
  const data = allFilteredIssues.value
  if (!data.length) {
    ElMessage.warning('当前筛选结果为空，无数据可导出')
    return
  }

  // 构建表头（按 exportFieldOptions 顺序，只保留选中字段）
  const selectedOptions = exportFieldOptions.filter(f => exportSelectedFields.value.includes(f.key))
  const header = selectedOptions.map(f => f.label)

  // 构建数据行
  const rows = data.map(issue =>
    selectedOptions.map(f => {
      const val = issue[f.key]
      if (f.key === 'is_rectification') return val ? '是' : '否'
      return val ?? ''
    })
  )

  // 生成工作表
  const ws = XLSX.utils.aoa_to_sheet([header, ...rows])

  // 设置列宽（根据字段类型给合理默认宽度）
  const colWidths = selectedOptions.map(f => {
    if (f.key === 'description') return { wch: 60 }
    if (['contractor', 'supervisor', 'inspection_unit'].includes(f.key)) return { wch: 20 }
    return { wch: 16 }
  })
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '问题记录')

  // 生成文件名（含当前日期）
  const today = new Date().toISOString().slice(0, 10)
  const fileName = `问题记录_${today}.xlsx`

  XLSX.writeFile(wb, fileName)
  exportDialogVisible.value = false
  ElMessage.success(`已导出 ${data.length} 条记录`)
}

const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value
  console.log(`🔄 编辑模式已切换: isEditMode=${isEditMode.value}`)
}

const handleRowClick = (row) => {
  console.log('🔵 handleRowClick 被触发，row:', row)
  emit('row-click', row)
}

const handleViewDetail = (row) => {
  console.log('🟡 handleViewDetail 被触发，row:', row)
  emit('row-click', row)
}

const handlePageChange = () => {
  // 分页变化时的处理
}

// 编辑相关方法
const availableEditSecondaryCategories = computed(() => {
  if (!editingIssue.value?.issue_category) {
    return []
  }
  return getSecondaryCategories(editingIssue.value.issue_category)
})

// 获取三级分类列表
const availableEditTertiaryCategories = computed(() => {
  if (!editingIssue.value?.issue_type_level1) {
    return []
  }
  return getTertiaryCategories(editingIssue.value.issue_type_level1)
})

// 用于直接编辑的级联下拉列表计算属性
// 获取一级分类列表
const inlinePrimaryCategories = computed(() => {
  return ['工程质量', '施工安全', '管理行为', '其它']
})

// 获取二级分类列表（基于当前编辑的一级分类）
const getInlineSecondaryCategories = (primaryCategory) => {
  if (!primaryCategory) return []
  return getSecondaryCategories(primaryCategory)
}

// 获取三级分类列表（基于当前编辑的二级分类）
const getInlineTertiaryCategories = (secondaryCategory) => {
  if (!secondaryCategory) return []
  return getTertiaryCategories(secondaryCategory)
}

// 问题等级选项
const severityOptions = computed(() => {
  return ['严重', '一般', '轻微']
})

const handleEditRow = (row) => {
  console.log('✏️ handleEditRow 被触发，row:', row)
  editingIssue.value = JSON.parse(JSON.stringify(row))
  editingIssueIndex.value = allFilteredIssues.value.findIndex(i => i.id === row.id)
  editDialogVisible.value = true
}

const handleCategoryChange = () => {
  // 当一级分类改变时，重置二级和三级分类
  editingIssue.value.issue_type_level1 = ''
  editingIssue.value.issue_type_level2 = ''
}

const handleSecondaryChange = () => {
  // 当二级分类改变时，重置三级分类
  editingIssue.value.issue_type_level2 = ''
}

const resetEditForm = () => {
  editingIssue.value = null
  editingIssueIndex.value = -1
}

const saveEditedIssue = async () => {
  if (!editingIssue.value) return

  try {
    // 调用 API 保存编辑
    console.log('💾 保存编辑的问题:', editingIssue.value)

    // 这里需要调用后端 API 更新问题
    // await importService.updateIssue(editingIssue.value.id, editingIssue.value)

    // 临时：直接更新本地数据
    if (editingIssueIndex.value >= 0) {
      props.issues[editingIssueIndex.value] = editingIssue.value
    }

    ElMessage.success('保存成功')
    editDialogVisible.value = false
    resetEditForm()
  } catch (err) {
    console.error('❌ 保存失败:', err)
    ElMessage.error('保存失败')
  }
}

// 单元格直接编辑相关方法
const startInlineCellEdit = (row, fieldName) => {
  console.log(`🔍 startInlineCellEdit 被调用: fieldName=${fieldName}, isEditMode=${isEditMode.value}, row.id=${row.id}`)

  if (!isEditMode.value) {
    console.log(`⚠️ 编辑模式未启用，无法编辑`)
    return
  }

  const cellId = `${row.id}_${fieldName}`
  inlineCellEditingId.value = cellId
  inlineCellEditingField.value = fieldName

  // 处理不同类型的字段值
  const value = row[fieldName]
  if (value === null || value === undefined) {
    inlineCellEditingValue.value = ''
  } else if (typeof value === 'boolean') {
    inlineCellEditingValue.value = value
  } else {
    inlineCellEditingValue.value = value
  }

  console.log(`📝 开始编辑单元格: ${cellId}, 值: ${inlineCellEditingValue.value}`)
}

const saveInlineCellEdit = (row, fieldName) => {
  if (inlineCellEditingId.value !== `${row.id}_${fieldName}`) return

  // 更新行数据
  row[fieldName] = inlineCellEditingValue.value

  // 同时更新 props.issues 中的数据
  const issueIndex = props.issues.findIndex(i => i.id === row.id)
  if (issueIndex >= 0) {
    props.issues[issueIndex][fieldName] = inlineCellEditingValue.value
  }

  console.log(`✅ 保存单元格编辑: ${fieldName} = ${inlineCellEditingValue.value}`)
  ElMessage.success('保存成功')
  cancelInlineCellEdit()
}

const cancelInlineCellEdit = () => {
  inlineCellEditingId.value = null
  inlineCellEditingField.value = ''
  inlineCellEditingValue.value = ''
}

const handleInlineCellKeydown = (event, row, fieldName) => {
  if (event.key === 'Enter') {
    saveInlineCellEdit(row, fieldName)
  } else if (event.key === 'Escape') {
    cancelInlineCellEdit()
  }
}

const isInlineCellEditing = (row, fieldName) => {
  return inlineCellEditingId.value === `${row.id}_${fieldName}`
}
</script>

<style scoped>
.issues-table-container {
  background: white;
  border-radius: 8px;
  padding: 16px;
}

.table-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.description-text {
  color: #666;
  font-size: 13px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.edit-form {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 10px;
}

.edit-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.edit-form :deep(.el-input__wrapper) {
  width: 100%;
}

.edit-form :deep(.el-select) {
  width: 100%;
}

.edit-form :deep(.el-date-picker) {
  width: 100%;
}
</style>

