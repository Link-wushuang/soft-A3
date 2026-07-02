<template>
  <div class="page-container">
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:12px">
        <button class="back-btn" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <div>
          <h1 class="page-title">资源生成</h1>
          <p class="page-subtitle">多智能体协同为你生成6种个性化学习资源</p>
        </div>
      </div>
      <div style="display:flex;gap:10px">
        <el-button @click="$router.push(`/student/tutor/${kpId}`)">
          <el-icon style="margin-right:6px"><ChatDotRound /></el-icon>
          智能答疑
        </el-button>
        <el-button @click="$router.push(`/student/exercise/${kpId}`)">
          <el-icon style="margin-right:6px"><EditPen /></el-icon>
          做练习
        </el-button>
        <el-button type="primary" @click="startGeneration" :loading="generating" :disabled="!!taskId">
          <el-icon style="margin-right:6px"><MagicStick /></el-icon>
          {{ taskId ? '生成中...' : '开始生成' }}
        </el-button>
      </div>
    </div>

    <div class="resource-layout">
      <div class="resource-sidebar">
        <AgentTracePanel :traces="traces" />
      </div>
      <div class="resource-main">
        <div v-if="resources.length" class="resource-tabs card">
          <div class="tab-bar">
            <button v-for="res in resources" :key="res.id"
                    :class="['res-tab', { active: activeTab === String(res.id) }]"
                    @click="activeTab = String(res.id)">
              <span class="tab-icon">{{ typeIcons[res.resource_type] || '📄' }}</span>
              {{ typeLabels[res.resource_type] || res.resource_type }}
            </button>
          </div>
          <div class="tab-content">
            <ResourceCard v-for="res in resources" :key="res.id" v-show="activeTab === String(res.id)" :resource="res" />
          </div>
        </div>
        <el-skeleton v-else-if="generating" :rows="8" animated />
        <div v-else class="empty-state card">
          <div class="card-body" style="text-align:center;padding:60px 40px">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none" style="margin-bottom:20px">
              <rect width="56" height="56" rx="14" fill="#f5f3ff"/>
              <path d="M28 20V36M20 28H36" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
            <h3 style="margin:0 0 8px;font-size:18px">准备生成学习资源</h3>
            <p style="color:var(--ep-text-secondary);margin:0;font-size:14px">
              点击「开始生成」，6 类资源智能体将并行协同生成，经知识与安全智能体校验
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ChatDotRound, EditPen, MagicStick } from '@element-plus/icons-vue'
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
let eventSource: EventSource | null = null

const TYPE_ORDER = ['lecture', 'mindmap', 'case', 'video_storyboard', 'exercise', 'extended_reading']
const typeLabels: Record<string, string> = {
  lecture: '个性化讲解', mindmap: '思维导图', exercise: '练习题',
  case: '实操案例', extended_reading: '拓展阅读', video_storyboard: '视频分镜',
}
const typeIcons: Record<string, string> = {
  lecture: '📖', mindmap: '🧠', exercise: '✏️',
  case: '💻', extended_reading: '📚', video_storyboard: '🎬',
}

function sortResources(list: any[]) {
  return [...list].sort((a, b) => {
    const ai = TYPE_ORDER.indexOf(a.resource_type)
    const bi = TYPE_ORDER.indexOf(b.resource_type)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })
}

onMounted(async () => {
  // 重新进入页面：先拉取已生成的资源（即使生成未完成，部分资源也已入库）
  try {
    const res = await api.get('/resources', { params: { knowledge_point_id: kpId } })
    if (res.data.length) {
      resources.value = sortResources(res.data)
      if (!activeTab.value) activeTab.value = String(resources.value[0].id)
    }
  } catch { /* no resources yet */ }
  // 检查是否有运行中的任务，有则重连 SSE
  try {
    const t = await api.get('/resources/active-task', { params: { knowledge_point_id: kpId } })
    if (t.data.task_id) {
      taskId.value = t.data.task_id
      generating.value = true
      const traceRes = await api.get(`/agent-tasks/${t.data.task_id}/trace`)
      traces.value = traceRes.data
      pollSSE(t.data.task_id)
    }
  } catch { /* no active task */ }
})

onBeforeUnmount(() => {
  // 组件销毁时关闭 SSE 连接，避免后台泄漏 + 回来后重复连接
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
})

async function startGeneration() {
  generating.value = true
  requestNotifyPermission()
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
  // 关闭旧连接（防御性：避免重复连接）
  if (eventSource) eventSource.close()
  const token = localStorage.getItem('token') || ''
  const source = new EventSource(`/api/resources/generate/${tid}/stream?token=${encodeURIComponent(token)}`)
  eventSource = source
  source.addEventListener('agent_status', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    const idx = traces.value.findIndex(t => t.agent_name === data.agent_name)
    if (idx >= 0) { traces.value[idx] = data } else { traces.value.push(data) }
  })
  source.addEventListener('resource_ready', async () => {
    // 有新资源就绪，立即拉取并刷新展示
    const res = await api.get('/resources', { params: { knowledge_point_id: kpId } })
    resources.value = sortResources(res.data)
    if (!activeTab.value && resources.value.length) activeTab.value = String(resources.value[0].id)
  })
  source.addEventListener('done', () => {
    source.close()
    eventSource = null
    generating.value = false
    taskId.value = null
    // 最终再拉一次确保拿到全部资源
    api.get('/resources', { params: { knowledge_point_id: kpId } }).then(res => {
      if (res.data.length) {
        resources.value = sortResources(res.data)
        if (!activeTab.value) activeTab.value = String(resources.value[0].id)
      }
    }).catch(() => {})
    // 浏览器桌面通知：用户切到别的 tab 时也能收到完成提醒
    notifyGenerationComplete()
  })
  source.addEventListener('error', () => {
    source.close()
    eventSource = null
    // SSE 断开不立即设 generating=false，可能是临时网络波动；
    // onMounted 重新进入时会通过 active-task 判断是否还在运行
    // 只有明确收到 done 才算真正结束
  })
}

/** 浏览器桌面通知：资源生成完成时推送，即使用户切到别的 tab 也能收到。 */
function notifyGenerationComplete() {
  const resourceCount = resources.value.length
  const title = '学习资源生成完成'
  const body = `${resourceCount} 类个性化资源已就绪，点击查看`

  // 优先用 Notification API
  if ('Notification' in window && Notification.permission === 'granted') {
    try {
      const n = new Notification(title, {
        body,
        icon: '/favicon.ico',
        tag: 'edupath-gen-complete',
      })
      n.onclick = () => {
        window.focus()
        n.close()
      }
      return
    } catch { /* fall through */ }
  }

  // 降级：页面内 ElMessage + 标题闪烁
  ElMessage.success(body)
  // 标题闪烁提醒（用户在别的 tab 时能看到 tab 标题变化）
  let isOrigTitle = true
  const origTitle = document.title
  const flashTimer = setInterval(() => {
    document.title = isOrigTitle ? `✅ ${title}` : origTitle
    isOrigTitle = !isOrigTitle
  }, 800)
  // 用户回到页面时停止闪烁
  const stopFlash = () => {
    if (!document.hidden) {
      clearInterval(flashTimer)
      document.title = origTitle
      document.removeEventListener('visibilitychange', stopFlash)
    }
  }
  document.addEventListener('visibilitychange', stopFlash)
  // 10 秒后自动停止
  setTimeout(() => {
    clearInterval(flashTimer)
    document.title = origTitle
    document.removeEventListener('visibilitychange', stopFlash)
  }, 10000)
}

/** 在开始生成时请求通知权限（需用户交互触发）。 */
function requestNotifyPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}
</script>

<style scoped>
.resource-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
  align-items: start;
}

.resource-sidebar {
  position: sticky;
  top: 32px;
}

.resource-tabs {
  overflow: hidden;
}

.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--ep-border-light);
  overflow-x: auto;
  padding: 0 8px;
}

.res-tab {
  padding: 14px 18px;
  border: none;
  background: none;
  font-size: 13px;
  font-weight: 500;
  color: var(--ep-text-secondary);
  cursor: pointer;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  transition: all var(--ep-transition);
  display: flex;
  align-items: center;
  gap: 6px;
}

.res-tab:hover {
  color: var(--ep-text-primary);
}

.res-tab.active {
  color: var(--ep-primary);
  border-bottom-color: var(--ep-primary);
}

.tab-icon {
  font-size: 15px;
}

.tab-content {
  padding: 20px;
}
</style>
