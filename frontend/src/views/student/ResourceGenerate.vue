<template>
  <el-container style="padding:24px;max-width:1200px;margin:0 auto">
    <el-header style="display:flex;justify-content:space-between;align-items:center;height:auto;padding:16px 0">
      <div style="display:flex;align-items:center;gap:12px">
        <el-button :icon="ArrowLeft" @click="$router.back()" circle />
        <h1 style="margin:0">资源生成</h1>
      </div>
      <div style="display:flex;gap:8px">
        <el-button @click="$router.push(`/student/exercise/${kpId}`)">做练习</el-button>
        <el-button type="primary" @click="startGeneration" :loading="generating" :disabled="!!taskId">
          {{ taskId ? '生成中...' : '开始生成' }}
        </el-button>
      </div>
    </el-header>
    <el-main>
      <el-row :gutter="24">
        <el-col :span="6">
          <AgentTracePanel :traces="traces" />
        </el-col>
        <el-col :span="18">
          <el-tabs v-if="resources.length" v-model="activeTab">
            <el-tab-pane v-for="res in resources" :key="res.id" :label="typeLabels[res.resource_type] || res.resource_type" :name="String(res.id)">
              <ResourceCard :resource="res" />
            </el-tab-pane>
          </el-tabs>
          <el-skeleton v-else-if="generating" :rows="8" animated />
          <el-empty v-else description="点击「开始生成」为当前知识点生成个性化资源" />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import api from '../../api/index'
import AgentTracePanel from '../../components/AgentTracePanel.vue'
import ResourceCard from '../../components/ResourceCard.vue'

const route = useRoute()
const kpId = Number(route.params.knowledgePointId)
const taskId = ref<number | null>(null)
const generating = ref(false)
const traces = ref<any[]>([])
const resources = ref<any[]>([])
const activeTab = ref('')
const typeLabels: Record<string, string> = {
  lecture: '个性化讲解', mindmap: '思维导图', exercise: '练习题',
  case: '实操案例', extended_reading: '拓展阅读', video_storyboard: '视频分镜',
}

onMounted(async () => {
  try {
    const res = await api.get('/resources', { params: { knowledge_point_id: kpId } })
    if (res.data.length) {
      resources.value = res.data
      activeTab.value = String(res.data[0].id)
    }
  } catch { /* no resources yet */ }
})

async function startGeneration() {
  generating.value = true
  try {
    const res = await api.post('/resources/generate', { knowledge_point_id: kpId })
    taskId.value = res.data.task_id
    pollSSE(res.data.task_id)
  } catch {
    ElMessage.error('启动生成失败')
    generating.value = false
  }
}

function pollSSE(tid: number) {
  const token = localStorage.getItem('token') || ''
  const source = new EventSource(`/api/resources/generate/${tid}/stream?token=${encodeURIComponent(token)}`)
  source.addEventListener('agent_status', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    const idx = traces.value.findIndex(t => t.agent_name === data.agent_name)
    if (idx >= 0) { traces.value[idx] = data } else { traces.value.push(data) }
  })
  source.addEventListener('resource_ready', async () => {
    const res = await api.get('/resources', { params: { knowledge_point_id: kpId } })
    resources.value = res.data
    if (!activeTab.value && res.data.length) activeTab.value = String(res.data[0].id)
  })
  source.addEventListener('done', () => {
    source.close()
    generating.value = false
    taskId.value = null
  })
  source.addEventListener('error', () => {
    source.close()
    generating.value = false
  })
}
</script>
