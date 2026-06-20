<template>
  <div class="page-container" style="max-width:1400px">
    <div class="page-header">
      <div>
        <h1 class="page-title">知识点管理</h1>
        <p class="page-subtitle">管理操作系统课程知识点库</p>
      </div>
      <el-button type="primary" @click="openCreate">
        <el-icon style="margin-right:6px"><Plus /></el-icon>
        新增知识点
      </el-button>
    </div>

    <div class="card">
      <div class="card-body" style="padding:0">
        <el-table :data="knowledgePoints" v-loading="loading" style="width:100%"
                  :header-cell-style="{ background: 'var(--ep-bg-hover)', fontWeight: 600 }">
          <el-table-column prop="chapter" label="章节" width="200" />
          <el-table-column prop="title" label="标题" min-width="200">
            <template #default="{ row }">
              <span style="font-weight:500">{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="difficultyType(row.difficulty)" size="small" effect="light" round>
                {{ diffLabels[row.difficulty] || row.difficulty }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="tags" label="标签" min-width="180">
            <template #default="{ row }">
              <el-tag v-for="tag in (row.tags || [])" :key="tag" size="small" effect="light" round
                      style="margin:2px 4px 2px 0">{{ tag }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="handleDelete(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="card" style="margin-top:20px">
      <div class="card-header" style="display:flex;align-items:center;justify-content:space-between">
        <div style="display:flex;align-items:center;gap:8px">
          <el-icon style="color:var(--ep-primary)"><Upload /></el-icon>
          <span>课程文档管理</span>
        </div>
        <el-upload :action="uploadUrl" :headers="uploadHeaders" :data="{ course_id: 1 }"
                   name="file" :show-file-list="false" accept=".pdf,.md,.txt,.markdown"
                   :on-success="onUploadSuccess" :on-error="onUploadError">
          <el-button type="primary" size="small">
            <el-icon style="margin-right:4px"><Upload /></el-icon>上传文档
          </el-button>
        </el-upload>
      </div>
      <div class="card-body" style="padding:0">
        <div v-if="!documents.length" style="text-align:center;padding:40px;color:var(--ep-text-secondary);font-size:14px">
          暂无文档，上传 PDF/Markdown/TXT 文件以增强知识库
        </div>
        <div v-else>
          <div v-for="doc in documents" :key="doc.id" class="doc-item">
            <div class="doc-info">
              <el-icon :size="18" style="color:var(--ep-primary);flex-shrink:0">
                <Document />
              </el-icon>
              <div>
                <div class="doc-name">{{ doc.filename }}</div>
                <div class="doc-meta">{{ doc.content_type.toUpperCase() }} · {{ doc.chunk_count }} 个文本段 · {{ doc.created_at?.slice(0, 10) }}</div>
              </div>
            </div>
            <el-button size="small" link type="danger" @click="deleteDocument(doc.id)">删除</el-button>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑知识点' : '新增知识点'" width="600px" top="8vh">
      <el-form :model="form" label-width="80px" label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="章节">
              <el-input v-model="form.chapter" placeholder="如：第一章 操作系统概述" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度">
              <el-select v-model="form.difficulty" style="width:100%">
                <el-option label="简单" value="easy" />
                <el-option label="中等" value="medium" />
                <el-option label="困难" value="hard" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="知识点标题" />
        </el-form-item>
        <el-form-item label="摘要">
          <el-input v-model="form.summary" type="textarea" :rows="3" placeholder="知识点摘要" />
        </el-form-item>
        <el-form-item label="核心内容">
          <el-input v-model="form.key_content" type="textarea" :rows="3" placeholder="核心内容" />
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Document } from '@element-plus/icons-vue'
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

const documents = ref<any[]>([])
const uploadUrl = computed(() => `${api.defaults.baseURL}/documents/upload?course_id=1`)
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
}))

const diffLabels: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }

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

async function fetchDocuments() {
  try {
    const res = await api.get('/documents', { params: { course_id: 1 } })
    documents.value = res.data
  } catch { /* ignore */ }
}

function onUploadSuccess() {
  ElMessage.success('文档上传成功')
  fetchDocuments()
}

function onUploadError() {
  ElMessage.error('文档上传失败')
}

async function deleteDocument(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该文档吗？', '确认', { type: 'warning' })
    await api.delete(`/documents/${id}`)
    ElMessage.success('删除成功')
    fetchDocuments()
  } catch { /* cancelled */ }
}

onMounted(() => {
  fetchData()
  fetchDocuments()
})
</script>

<style scoped>
.doc-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid var(--ep-border-light);
}

.doc-item:last-child {
  border-bottom: none;
}

.doc-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--ep-text-primary);
}

.doc-meta {
  font-size: 12px;
  color: var(--ep-text-secondary);
  margin-top: 2px;
}
</style>
