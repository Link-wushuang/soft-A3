<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center;height:auto;padding:16px 0">
      <h1 style="margin:0">学习路径</h1>
      <el-button type="primary" @click="generatePath" :loading="generating">生成路径</el-button>
    </el-header>
    <el-main>
      <el-skeleton v-if="loading" :rows="6" animated />
      <el-empty v-else-if="!path" description="暂无学习路径，请先建档后生成" />
      <PathTimeline v-else :nodes="path.nodes" @nodeClick="goToResources" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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
