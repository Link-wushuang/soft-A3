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

    <!-- 重规划历史 -->
    <div v-if="history.length > 1" class="replan-history">
      <div class="history-header" @click="showHistory = !showHistory">
        <div class="history-header-left">
          <el-icon :size="16" style="color:var(--ep-primary)"><Clock /></el-icon>
          <span>重规划历史</span>
          <span class="history-count">{{ history.length }} 次规划</span>
        </div>
        <el-icon :size="14" style="color:var(--ep-text-muted);transition:transform 0.2s" :style="{transform: showHistory ? 'rotate(180deg)' : 'rotate(0)'}"><ArrowDown /></el-icon>
      </div>
      <transition name="collapse">
        <div v-show="showHistory" class="history-list">
          <div v-for="(item, i) in history" :key="item.id" :class="['history-item', { active: item.status === 'active' }]">
            <div class="history-item-header">
              <div :class="['history-status-dot', item.status]"></div>
              <span class="history-item-title">{{ item.status === 'active' ? '当前路径' : '历史路径' }}</span>
              <span class="history-item-time">{{ formatTime(item.created_at) }}</span>
              <span class="history-item-nodes">{{ item.node_count }} 个节点</span>
            </div>
            <div v-if="item.nodes.length" class="history-item-nodes">
              <span v-for="(node, ni) in item.nodes.slice(0, 5)" :key="ni" class="history-node-chip">
                {{ node.knowledge_point_title }}
              </span>
              <span v-if="item.nodes.length > 5" class="history-node-more">+{{ item.nodes.length - 5 }}</span>
            </div>
            <div v-if="i === 0 && history.length > 1" class="history-trigger">
              <el-icon :size="12" style="color:#6366f1"><Refresh /></el-icon>
              <span>由 ReflectionAgent 薄弱点变化自动触发</span>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Clock, ArrowDown } from '@element-plus/icons-vue'
import PathTimeline from '../../components/PathTimeline.vue'
import api from '../../api/index'

const router = useRouter()
const path = ref<any>(null)
const loading = ref(true)
const generating = ref(false)
const history = ref<any[]>([])
const showHistory = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/learning-path/current', { params: { course_id: 1 } })
    path.value = res.data
  } catch { /* no path yet */ }
  try {
    const res = await api.get('/learning-path/history', { params: { course_id: 1 } })
    history.value = res.data.history || []
    if (history.value.length > 1) showHistory.value = true
  } catch { /* no history */ }
  loading.value = false
})

async function generatePath() {
  generating.value = true
  try {
    const res = await api.post('/learning-path/generate', { course_id: 1 })
    path.value = res.data
    ElMessage.success('学习路径已生成')
    // 刷新历史
    try {
      const hres = await api.get('/learning-path/history', { params: { course_id: 1 } })
      history.value = hres.data.history || []
    } catch {}
  } catch {
    ElMessage.error('路径生成失败')
  } finally {
    generating.value = false
  }
}

function goToResources(node: any) {
  router.push(`/student/resources/${node.knowledge_point_id}`)
}

function formatTime(t: string | null): string {
  if (!t) return ''
  try {
    const d = new Date(t)
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } catch {
    return t
  }
}
</script>

<style scoped>
.replan-history {
  margin-top: 28px;
  border: 1px solid var(--ep-border-light);
  border-radius: var(--ep-radius-md);
  overflow: hidden;
}
.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: var(--ep-bg-elevated);
  cursor: pointer;
  transition: background 0.2s;
}
.history-header:hover { background: var(--ep-bg-hover); }
.history-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--ep-text-primary);
}
.history-count {
  font-size: 12px;
  font-weight: 400;
  color: var(--ep-text-muted);
  background: var(--ep-bg-soft);
  padding: 2px 8px;
  border-radius: 10px;
}
.history-list {
  padding: 8px 12px 12px;
}
.history-item {
  padding: 12px 14px;
  margin-bottom: 8px;
  border-radius: var(--ep-radius-sm);
  background: var(--ep-bg);
  border: 1px solid var(--ep-border-light);
}
.history-item.active {
  background: linear-gradient(135deg, #eef2ff, #f5f3ff);
  border-color: #c7d2fe;
}
.history-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.history-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.history-status-dot.active { background: #6366f1; box-shadow: 0 0 6px rgba(99,102,241,0.4); }
.history-status-dot.replaced { background: #94a3b8; }
.history-item-title { font-size: 13px; font-weight: 600; color: var(--ep-text-primary); }
.history-item-time { font-size: 11px; color: var(--ep-text-muted); font-family: monospace; }
.history-item-nodes { font-size: 11px; color: var(--ep-text-secondary); margin-left: auto; }
.history-item-nodes-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}
.history-node-chip {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(255,255,255,0.6);
  border: 1px solid var(--ep-border-light);
  color: var(--ep-text-secondary);
}
.history-node-more {
  font-size: 11px;
  padding: 2px 6px;
  color: var(--ep-text-muted);
}
.history-trigger {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--ep-border-light);
  font-size: 11px;
  color: #6366f1;
}
.collapse-enter-active, .collapse-leave-active { transition: all 0.3s ease; overflow: hidden; }
.collapse-enter-from, .collapse-leave-to { opacity: 0; max-height: 0; }
.collapse-enter-to, .collapse-leave-from { opacity: 1; max-height: 600px; }
</style>
