<template>
  <el-container style="padding:24px;max-width:1400px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center;height:auto;padding:16px 0">
      <h1 style="margin:0">知识点管理</h1>
      <el-button type="primary" @click="openCreate">新增知识点</el-button>
    </el-header>
    <el-main>
      <el-table :data="knowledgePoints" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="chapter" label="章节" width="200" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="difficultyType(row.difficulty)" size="small">{{ row.difficulty }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" min-width="150">
          <template #default="{ row }">
            <el-tag v-for="tag in (row.tags || [])" :key="tag" size="small" style="margin:2px">{{ tag }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑知识点' : '新增知识点'" width="600px">
        <el-form :model="form" label-width="80px">
          <el-form-item label="章节">
            <el-input v-model="form.chapter" placeholder="如：第一章 操作系统概述" />
          </el-form-item>
          <el-form-item label="标题">
            <el-input v-model="form.title" placeholder="知识点标题" />
          </el-form-item>
          <el-form-item label="摘要">
            <el-input v-model="form.summary" type="textarea" :rows="3" placeholder="知识点摘要" />
          </el-form-item>
          <el-form-item label="核心内容">
            <el-input v-model="form.key_content" type="textarea" :rows="3" placeholder="核心内容" />
          </el-form-item>
          <el-form-item label="难度">
            <el-select v-model="form.difficulty" style="width:100%">
              <el-option label="简单" value="easy" />
              <el-option label="中等" value="medium" />
              <el-option label="困难" value="hard" />
            </el-select>
          </el-form-item>
          <el-form-item label="标签">
            <el-input v-model="tagsInput" placeholder="逗号分隔，如：进程,调度,CPU" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </template>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api/index'

interface KnowledgePoint {
  id: number
  chapter: string
  title: string
  summary: string
  difficulty: string
  tags: string[]
}

interface FormData {
  course_id: number
  chapter: string
  title: string
  summary: string
  key_content: string
  difficulty: string
  tags: string[]
}

const knowledgePoints = ref<KnowledgePoint[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const tagsInput = ref('')

const form = ref<FormData>({
  course_id: 1,
  chapter: '',
  title: '',
  summary: '',
  key_content: '',
  difficulty: 'medium',
  tags: [],
})

function difficultyType(d: string) {
  if (d === 'easy') return 'success'
  if (d === 'hard') return 'danger'
  return 'warning'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/courses/1/knowledge-points')
    knowledgePoints.value = res.data
  } catch {
    ElMessage.error('获取知识点列表失败')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    course_id: 1,
    chapter: '',
    title: '',
    summary: '',
    key_content: '',
    difficulty: 'medium',
    tags: [],
  }
  tagsInput.value = ''
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: KnowledgePoint) {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    course_id: 1,
    chapter: row.chapter,
    title: row.title,
    summary: row.summary,
    key_content: '',
    difficulty: row.difficulty,
    tags: row.tags || [],
  }
  tagsInput.value = (row.tags || []).join(',')
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.chapter || !form.value.title) {
    ElMessage.warning('请填写章节和标题')
    return
  }
  form.value.tags = tagsInput.value ? tagsInput.value.split(',').map(t => t.trim()).filter(Boolean) : []
  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await api.put(`/knowledge-points/${editingId.value}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/knowledge-points', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该知识点吗？', '确认', { type: 'warning' })
    await api.delete(`/knowledge-points/${id}`)
    ElMessage.success('删除成功')
    await fetchData()
  } catch {
    /* cancelled or error */
  }
}

onMounted(fetchData)
</script>
