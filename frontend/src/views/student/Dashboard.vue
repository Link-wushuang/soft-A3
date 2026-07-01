<template>
  <div class="page-container">
    <div class="breadcrumb">
      <el-icon :size="14"><HomeFilled /></el-icon><span class="bread-sep">/</span><span>学习中心</span><span class="bread-sep">/</span><span class="bread-current">学习仪表盘</span>
    </div>
    <div class="page-header">
      <div><h1 class="page-title">欢迎回来，{{ auth.user?.display_name || '同学' }} 👋</h1><p class="page-subtitle">基于你的学习画像，以下是今日推荐</p></div>
      <el-button type="primary" size="large" @click="$router.push('/student/profile-chat')"><el-icon style="margin-right:6px"><ChatDotRound /></el-icon>更新学习画像</el-button>
    </div>
    <template v-if="loading"><div class="stats-grid"><el-skeleton v-for="i in 4" :key="i" animated style="padding:24px;border-radius:var(--ep-radius-lg);background:var(--ep-bg-elevated)"><template #template><el-skeleton-item variant="text" style="width:60%" /><el-skeleton-item variant="text" style="width:40%;margin-top:10px" /></template></el-skeleton></div><el-skeleton :rows="6" animated style="margin-bottom:20px" /></template>
    <div v-else-if="error" class="card" style="border-color:#fecaca"><div class="card-body" style="text-align:center;padding:48px"><div class="empty-state-icon" style="background:#fef2f2"><el-icon :size="28" style="color:#ef4444"><WarningFilled /></el-icon></div><p class="empty-state-title">数据加载失败</p><p class="empty-state-desc">{{ error }}</p><el-button type="primary" @click="fetchAll">重新加载</el-button></div></div>
    <template v-else>
      <!-- KPI cards -->
      <div class="stats-grid">
        <div :class="['kpi-card','kpi-wide',{'kpi-active':activeKey==='mastery'}]" @click="activeKey='mastery'">
          <MiniKnowledgeMap
            subject="操作系统"
            :overall-percent="displayMastery"
            :clusters="knowledgeClusters"
          />
          <div class="kpi-action" @click.stop="$router.push('/student/knowledge-map')">查看完整图谱 →</div>
        </div>
        <div :class="['kpi-card','kpi-wide',{'kpi-active':activeKey==='learned'}]" @click="activeKey='learned'">
          <MiniKnowledgeProgress
            :total="totalKpCount"
            :mastered="profile?.mastered_points || []"
            :weak="profile?.weak_points || []"
            :untouched="untouchedPoints"
          />
          <div class="kpi-action" @click.stop="$router.push('/student/learning-records')">查看学习记录 →</div>
        </div>
        <div :class="['kpi-card','kpi-wide',{'kpi-active':activeKey==='time'}]" @click="activeKey='time'">
          <TimeBudgetCard
            :daily-budget-minutes="studyTime.daily_budget_minutes"
            :today-minutes="studyTime.today_minutes"
            :weekly-data="studyTime.week_data"
            :suggestion="studyTime.suggestion"
          />
          <div class="kpi-action" @click.stop="$router.push('/student/study-plan')">制定学习计划 →</div>
        </div>
        <div :class="['kpi-card','kpi-featured','kpi-wide',{'kpi-active':activeKey==='today'}]" @click="activeKey='today'">
          <div class="kpi-badge" v-if="activeKey==='today'">当前</div>
          <div class="kpi-top"><div class="kpi-icon" style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;box-shadow:0 2px 12px rgba(99,102,241,0.35)"><el-icon :size="20"><Aim /></el-icon></div></div>
          <div class="kpi-body">
            <div class="kpi-value">{{ recommendations.length }}<span class="kpi-unit">项</span></div>
            <div class="kpi-title">今日推荐学习</div>
            <div class="kpi-bar"><div class="kpi-bar-fill" style="--bar-color:#6366f1" :style="{width:Math.min(recommendations.length*12.5,100)+'%'}" /></div>
            <div class="kpi-sub">基于画像智能匹配</div>

            <!-- Priority preview -->
            <div class="kpi-sep" />
            <div class="kpi-preview-head">📋 优先推荐 <span>前 2 项</span></div>
            <div class="kpi-preview-list">
              <div v-for="(item, i) in priorityPreview" :key="item.id" class="kpi-preview-item"
                   @click.stop="$router.push(`/student/resources/${item.id}`)">
                <span class="kpi-preview-rank" :class="'r'+i">{{ i+1 }}</span>
                <span class="kpi-preview-icon">{{ item.icon }}</span>
                <div class="kpi-preview-info">
                  <div class="kpi-preview-title">{{ item.title }}</div>
                  <div class="kpi-preview-meta">{{ item.category }} · {{ item.note }}</div>
                </div>
                <span class="kpi-preview-min">{{ item.minutes }}m</span>
                <span class="kpi-preview-arrow">→</span>
              </div>
            </div>
            <div class="kpi-preview-summary">
              还有 <strong>{{ Math.max(0, recommendations.length - 2) }}</strong> 项 · 预计 <strong>{{ totalEstMinutes }}</strong> 分钟
            </div>

            <!-- Insight -->
            <div class="kpi-insight">
              <span class="kpi-insight-icon">💡</span>
              <div>
                <div class="kpi-insight-title">今日洞察</div>
                <div class="kpi-insight-text">{{ insightText }}</div>
              </div>
            </div>
          </div>
          <div class="kpi-dots"><span v-for="d in 4" :key="d" class="kpi-dot" :class="{on:d===1}" /></div>
          <div class="kpi-action" @click.stop="$router.push('/student/recommendations')">查看全部推荐 →</div>
        </div>
      </div>

      <div class="content-grid">
        <div class="content-main">
          <div class="card detail-panel">
            <div class="card-body" style="min-height:420px">
              <Transition name="swap" mode="out-in">
                <component :is="detailComponent" :key="activeKey"
                  :recommendations="recommendations"
                  :rank-colors="rankColors"
                  :profile="profile"
                  @go-resource="(id:number) => $router.push(`/student/resources/${id}`)"
                  @go-tutor="() => $router.push('/student/tutor')"
                  @open-plan="showPlanBuilder = true"
                  @navigate="(path:string) => $router.push(path)"
                />
              </Transition>
            </div>
          </div>
          <ProfileCard v-if="profile" :profile="profile" style="margin-top:20px" />
        </div>
      </div>
    </template>

    <PlanBuilderDrawer
      v-model="showPlanBuilder"
      :remaining-minutes="Math.max(0, studyTime.daily_budget_minutes - studyTime.today_minutes)"
      :topics="topicsForPlan"
      @start="handlePlanStart"
    />

    <FocusMode
      v-if="showFocusMode"
      :topics="focusTopics"
      @exit="handleFocusExit"
      @complete="handleFocusComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { ElMessage } from 'element-plus'
import { HomeFilled, ChatDotRound, WarningFilled, Aim } from '@element-plus/icons-vue'
import ProfileCard from '../../components/ProfileCard.vue'
import MiniKnowledgeMap from '../../components/MiniKnowledgeMap.vue'
import MiniKnowledgeProgress from '../../components/MiniKnowledgeProgress.vue'
import TimeBudgetCard from '../../components/TimeBudgetCard.vue'
import PlanBuilderDrawer from '../../components/PlanBuilderDrawer.vue'
import FocusMode from '../../components/FocusMode.vue'
import MasteryDetail from './details/MasteryDetail.vue'
import LearnedDetail from './details/LearnedDetail.vue'
import TimeDetail from './details/TimeDetail.vue'
import TodayDetail from './details/TodayDetail.vue'
import api from '../../api/index'

const auth = useAuthStore(); const profile = ref<any>(null); const recommendations = ref<any[]>([]); const allKpTitles = ref<string[]>([])
// 当前为单课程上下文（course_id=1），后端 /profile/{course_id} 基于登录用户鉴权
const COURSE_ID = 1
const studyTime = ref<any>({ today_minutes: 0, daily_budget_minutes: 90, week_data: [], suggestion: '' })
type DetailKey = 'mastery'|'learned'|'time'|'today'
const activeKey = ref<DetailKey>('today')
const detailComponent = computed(() => ({mastery:MasteryDetail,learned:LearnedDetail,time:TimeDetail,today:TodayDetail}[activeKey.value]))
const showPlanBuilder = ref(false)
const showFocusMode = ref(false)
const focusTopics = ref<Array<{id:string;title:string;plannedMinutes:number}>>([])

// 图标映射：根据知识点标题关键词选择
function iconFor(title: string): string {
  const t = title || ''
  if (/进程|线程|调度/.test(t)) return '⚙️'
  if (/内存|页|虚拟/.test(t)) return '💾'
  if (/文件|磁盘|I\/O|输入输出/.test(t)) return '📁'
  if (/同步|死锁|锁|信号/.test(t)) return '🔒'
  if (/中断|异常|调用/.test(t)) return '⚡'
  if (/设备|驱动/.test(t)) return '🔌'
  return '📘'
}

function handlePlanStart(plan: { selectedIds: string[]; mode: string }) {
  focusTopics.value = plan.selectedIds.map(id => {
    const t = topicsForPlan.value.find(x => x.id === id)
    return { id, title: t?.title || id, plannedMinutes: t?.recommendedMinutes || 15 }
  })
  showFocusMode.value = true
}
function handleFocusComplete(result: { totalMinutes: number; completedCount: number }) {
  showFocusMode.value = false
  fetchAll()
}
function handleFocusExit() { showFocusMode.value = false }

// 基于真实推荐数据派生学习计划可选主题（替代原硬编码 mockTopics）
const topicsForPlan = computed(() => recommendations.value.slice(0, 6).map((r: any) => ({
  id: String(r.knowledge_point_id),
  title: r.title,
  category: r.chapter || '推荐主题',
  difficulty: r.difficulty || 'medium',
  status: 'unmastered' as const,
  recommendedMinutes: r.est_minutes || 15,
  masteredCount: 0,
  totalCount: 10,
  recommended: !!r.reasons?.length,
  reason: r.reasons?.[0] || '推荐学习',
})))

const loading = ref(true); const error = ref('')
const totalKpCount = ref(40)

const displayMastery = computed(() => { const m=profile.value?.mastered_points?.length||0; const w=profile.value?.weak_points?.length||0; const t=m+w; if(!t) return 0; return Math.round(m/t*100) })
const untouchedPoints = computed(() => {
  const done = new Set([...(profile.value?.mastered_points||[]), ...(profile.value?.weak_points||[])])
  return allKpTitles.value.filter(t => !done.has(t))
})
const hasChartData = computed(() => (profile.value?.mastered_points?.length||0)>0)

// 基于真实推荐数据派生优先预览（替代原硬编码 priorityPreview）
const priorityPreview = computed(() => recommendations.value.slice(0, 2).map((r: any) => ({
  id: String(r.knowledge_point_id),
  icon: iconFor(r.title),
  title: r.title,
  category: r.chapter || '推荐',
  minutes: r.est_minutes || 15,
  note: r.reasons?.[0] || '建议优先',
})))
const totalEstMinutes = computed(() => recommendations.value.reduce((s:number,r:any)=>s+(r.est_minutes||15),0))

// 基于画像动态生成今日洞察（替代原硬编码 insightText）
const insightText = computed(() => {
  const weak = profile.value?.weak_points || []
  const mastered = profile.value?.mastered_points || []
  if (weak.length > 0) {
    return `检测到 ${weak.length} 个薄弱知识点，今日优先攻克「${weak[0]}」效果更好`
  }
  if (mastered.length > 0) {
    return `已掌握 ${mastered.length} 个知识点，建议继续推进下一阶段学习`
  }
  return '建议先完成对话建档，系统将为你生成个性化学习建议'
})

const rankColors = ['#4f46e5','#6366f1','#7c3aed','#8b5cf6','#a78bfa','#818cf8','#a855f7','#c084fc']
// TODO: 接入真实知识聚类数据
const knowledgeClusters = [
  { topic:'进程', total:6, mastered:4, learning:2, weak:0 },
  { topic:'内存', total:5, mastered:1, learning:2, weak:2 },
  { topic:'文件', total:4, mastered:0, learning:1, weak:3 },
  { topic:'I/O', total:3, mastered:2, learning:1, weak:0 },
  { topic:'设备', total:2, mastered:0, learning:0, weak:2 },
  { topic:'虚拟化', total:2, mastered:0, learning:0, weak:2 },
]
// TODO: 接入真实学习进度数据
const mockProgress: Record<string, number> = { '系统调用':35, '中断与异常':0, '操作系统结构':100, '虚拟机与容器基础':20, '上下文切换':0, '线程模型':60, '进程间通信':0, '临界区问题':0 }

async function fetchAll() {
  loading.value=true; error.value=''
  // 画像查询：后端 GET /profile/{course_id} 基于登录用户鉴权，参数应为 course_id 而非 user_id
  try { const r=await api.get(`/profile/${COURSE_ID}`); profile.value=r.data } catch { error.value='画像数据加载失败' }
  try { const r=await api.get('/analytics/recommendations'); recommendations.value=(r.data.recommended||[]).map((x:any,i:number)=>({...x,priority:x.priority||Math.max(1,5-i),est_minutes:x.est_minutes||10+Math.floor(Math.random()*15),progress:mockProgress[x.title]??0})) } catch { if(!error.value) error.value='推荐数据加载失败' }
  try { const r=await api.get('/analytics/study-time', { params: { course_id: COURSE_ID } }); studyTime.value=r.data } catch { /* 学习时长可选，失败用默认 */ }
  try { const r=await api.get(`/courses/${COURSE_ID}/knowledge-points`); allKpTitles.value=(r.data||[]).map((k:any)=>k.title) } catch {}
  loading.value=false
}
onMounted(fetchAll)
</script>

<style scoped>
.breadcrumb { display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ep-text-muted);margin-bottom:20px; } .bread-sep { color:#cbd5e1; } .bread-current { color:var(--ep-text-secondary);font-weight:500; }

/* KPI cards */
.stats-grid { display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:24px; } .kpi-wide { grid-column:span 2; }
.kpi-card { background:var(--ep-bg-elevated);border-radius:var(--ep-radius-lg);border:1px solid var(--ep-border-light);box-shadow:var(--ep-shadow-xs);padding:20px 22px 16px;transition:all var(--ep-transition-smooth);position:relative;display:flex;flex-direction:column;gap:0; }
.kpi-card:hover { box-shadow:var(--ep-shadow-md);transform:translateY(-2px); }
.kpi-card.kpi-featured { border-color:#e0e7ff;background:linear-gradient(160deg,#fafaff 0%,#f5f3ff 100%); }
.kpi-top { margin-bottom:12px; }
.kpi-icon { width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,0.5); }
.kpi-body { flex:1; }
.kpi-unit { font-size:15px;font-weight:500;color:var(--ep-text-muted);margin-left:2px; }
.kpi-title { font-size:13px;font-weight:500;color:var(--ep-text-secondary);margin-bottom:10px; }
.kpi-bar { height:4px;border-radius:2px;background:#e5e7eb;overflow:hidden;margin-bottom:8px; }
.kpi-bar-fill { height:100%;border-radius:2px;background:var(--bar-color,#6366f1);transition:width 0.6s var(--ep-transition-smooth); }
.kpi-sub { font-size:11px;color:var(--ep-text-muted); }
.kpi-action { margin-top:auto;padding-top:10px;border-top:1px solid var(--ep-border-light);font-size:12px;font-weight:500;color:var(--ep-primary);cursor:pointer;display:flex;align-items:center;gap:4px;transition:color var(--ep-transition); }
.kpi-action:hover { color:var(--ep-primary-hover); }
.kpi-badge { position:absolute;top:-1px;right:20px;padding:2px 10px;border-radius:0 0 6px 6px;font-size:10px;font-weight:600;color:white;background:linear-gradient(135deg,#6366f1,#8b5cf6);z-index:2; }
.kpi-dots { display:flex;gap:4px;margin-top:6px; } .kpi-dot { width:5px;height:5px;border-radius:50%;background:#e2e8f0;transition:all var(--ep-transition); } .kpi-dot.on { background:#6366f1;box-shadow:0 0 4px rgba(99,102,241,0.4); }

/* Priority preview */
.kpi-sep { border-top:1px solid #ede9fe;margin:10px 0; }
.kpi-preview-head { font-size:10px;font-weight:600;color:var(--ep-text-secondary);margin-bottom:6px;display:flex;justify-content:space-between; } .kpi-preview-head span { font-weight:400;color:var(--ep-text-muted); }
.kpi-preview-list { display:flex;flex-direction:column;gap:4px;margin-bottom:6px; }
.kpi-preview-item { display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;background:rgba(255,255,255,0.7);border:1px solid transparent;cursor:pointer;transition:all var(--ep-transition); } .kpi-preview-item:hover { background:white;border-color:#ddd6fe; }
.kpi-preview-rank { width:18px;height:18px;border-radius:5px;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;color:white;flex-shrink:0; } .kpi-preview-rank.r0 { background:#ef4444; } .kpi-preview-rank.r1 { background:#f59e0b; }
.kpi-preview-icon { font-size:15px;flex-shrink:0; }
.kpi-preview-info { flex:1;min-width:0; } .kpi-preview-title { font-size:11px;font-weight:600;color:var(--ep-text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis; } .kpi-preview-meta { font-size:9px;color:var(--ep-text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }
.kpi-preview-min { font-size:10px;color:var(--ep-text-muted);font-family:monospace;flex-shrink:0; }
.kpi-preview-arrow { font-size:11px;color:#d1d5db;flex-shrink:0;transition:all var(--ep-transition); } .kpi-preview-item:hover .kpi-preview-arrow { color:var(--ep-primary); }
.kpi-preview-summary { font-size:9px;color:var(--ep-text-muted); } .kpi-preview-summary strong { color:var(--ep-text-secondary); }

/* Insight */
.kpi-insight { display:flex;align-items:flex-start;gap:8px;padding:8px 10px;margin-top:8px;border-radius:8px;background:linear-gradient(135deg,#fffbeb,#fff7ed);border:1px solid #fde68a; }
.kpi-insight-icon { font-size:15px;line-height:1;flex-shrink:0; }
.kpi-insight-title { font-size:10px;font-weight:600;color:#92400e;margin-bottom:1px; }
.kpi-insight-text { font-size:9px;color:#a16207;line-height:1.4; }

/* Today list */
.content-grid { display:block; }
.kpi-card { cursor:pointer; } .kpi-active { border-color:var(--ep-primary)!important;box-shadow:0 0 0 2px rgba(99,102,241,0.2),var(--ep-shadow-md)!important; }
.detail-panel { overflow:hidden; }
.swap-enter-active,.swap-leave-active { transition:all 0.25s cubic-bezier(0.16,1,0.3,1); }
.swap-enter-from { opacity:0;transform:translateY(12px); } .swap-leave-to { opacity:0;transform:translateY(-8px); }

@media (max-width:1024px) { .stats-grid { grid-template-columns:repeat(2,1fr); } }
@media (max-width:640px) { .stats-grid { grid-template-columns:1fr; } .kpi-wide { grid-column:span 1; } .page-container { padding:20px 16px; } }
</style>
