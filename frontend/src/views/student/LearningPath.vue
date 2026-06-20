<template>
  <div class="page-container" style="max-width:800px">
    <div class="page-header">
      <div>
        <h1 class="page-title">学习路径</h1>
        <p class="page-subtitle">根据你的画像智能规划的个性化学习路线</p>
      </div>
      <el-button type="primary" @click="generatePath" :loading="generating">
        <el-icon style="margin-right:6px"><Refresh /></el-icon>
        {{ path ? '重新生成' : '生成路径' }}
      </el-button>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated />
    <div v-else-if="!path" class="empty-state card">
      <div class="card-body" style="text-align:center;padding:60px 40px">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" style="margin-bottom:20px">
          <rect width="56" height="56" rx="14" fill="#eff6ff"/>
          <path d="M20 36L28 18L36 36" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          <line x1="23" y1="30" x2="33" y2="30" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3 style="margin:0 0 8px;font-size:18px">暂无学习路径</h3>
        <p style="color:var(--ep-text-secondary);margin:0 0 24px;font-size:14px">
          请先通过「对话建档」完善你的学习画像，然后生成个性化路径
        </p>
        <el-button type="primary" @click="generatePath" :loading="generating">立即生成</el-button>
      </div>
    </div>
    <PathTimeline v-else :nodes="path.nodes" @nodeClick="goToResources" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import PathTimeline from '../../components/PathTimeline.vue'
import api from '../../api/index'

const router = useRouter()
const path = ref<any>(null)
const loading = ref(true)
const generating = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/learning-path/current', { params: { course_id: 1 } })
    path.value = res.data
  } catch { /* no path yet */ }
  loading.value = false
})

async function generatePath() {
  generating.value = true
  try {
    const res = await api.post('/learning-path/generate', { course_id: 1 })
    path.value = res.data
    ElMessage.success('学习路径已生成')
  } catch {
    ElMessage.error('路径生成失败')
  } finally {
    generating.value = false
  }
}

function goToResources(node: any) {
  router.push(`/student/resources/${node.knowledge_point_id}`)
}
</script>
