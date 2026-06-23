<template>
  <div class="page-container" style="max-width:1400px">
    <!-- Header with time filter -->
    <div class="page-header">
      <div>
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">全局学习数据概览与趋势分析</p>
      </div>
      <div class="header-right">
        <div class="time-filter">
          <button
            v-for="opt in timeOptions"
            :key="opt.key"
            :class="['tf-btn', { active: currentRange === opt.key }]"
            @click="switchRange(opt.key)"
          >{{ opt.label }}</button>
        </div>
        <el-button @click="fetchData" :loading="loading" round>
          <el-icon style="margin-right:6px"><Refresh /></el-icon>刷新数据
        </el-button>
      </div>
    </div>

    <!-- Custom date picker -->
    <div v-if="currentRange === 'custom'" class="custom-date-bar">
      <span class="cd-label">自定义时间范围：</span>
      <el-date-picker
        v-model="customDateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        :shortcuts="dateShortcuts"
        @change="onCustomDateChange"
      />
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading">
      <div class="stats-grid">
        <el-skeleton v-for="i in 4" :key="i" animated style="padding:24px;border-radius:var(--ep-radius-lg);background:var(--ep-bg-elevated)">
          <template #template><el-skeleton-item variant="text" style="width:50%" /><el-skeleton-item variant="text" style="width:30%;margin-top:10px" /><el-skeleton-item variant="text" style="width:80%;height:24px;margin-top:8px" /></template>
        </el-skeleton>
      </div>
      <div class="charts-grid">
        <SkeletonChart shape="bar" />
        <SkeletonChart shape="pie" />
      </div>
      <div class="charts-grid" style="margin-top:20px">
        <SkeletonChart shape="line" />
        <SkeletonChart shape="list" />
      </div>
    </div>

    <!-- Empty state: no data at all -->
    <div v-else-if="isEmpty" class="card" style="border-color:var(--ep-primary-lighter);background:var(--ep-primary-light)">
      <div class="card-body" style="text-align:center;padding:60px">
        <div class="empty-state-icon" style="background:var(--ep-primary-lighter)"><el-icon :size="28" style="color:var(--ep-primary)"><DataAnalysis /></el-icon></div>
        <p class="empty-state-title">还没有数据</p>
        <p class="empty-state-desc">发布第一次作业后，这里将展示班级学习数据分析</p>
        <el-button type="primary" @click="$router.push('/teacher/knowledge')">去发布第一次作业</el-button>
      </div>
    </div>

    <!-- Main content -->
    <div v-else>
      <!-- KPI cards with sparklines -->
      <div class="stats-grid">
        <div class="stat-card kpi-enhanced">
          <div class="stat-icon" style="background:#eef2ff;color:#6366f1"><el-icon :size="24"><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ kpiData.students.value }}</div>
            <div class="stat-label">学生总数</div>
            <div class="stat-spark"><Sparkline :data="kpiData.students.trend" :color="'#6366f1'" /></div>
            <div class="stat-delta" :class="kpiData.students.deltaDirection">
              <span class="delta-arrow">{{ deltaIcon(kpiData.students.deltaDirection) }}</span>
              <span>{{ kpiData.students.deltaLabel }}</span>
            </div>
          </div>
        </div>
        <div class="stat-card kpi-enhanced">
          <div class="stat-icon" style="background:#ecfdf5;color:#10b981"><el-icon :size="24"><EditPen /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ kpiData.answers.value }}</div>
            <div class="stat-label">答题总数</div>
            <div class="stat-spark"><Sparkline :data="kpiData.answers.trend" :color="'#10b981'" /></div>
            <div class="stat-delta" :class="kpiData.answers.deltaDirection">
              <span class="delta-arrow">{{ deltaIcon(kpiData.answers.deltaDirection) }}</span>
              <span>{{ kpiData.answers.deltaLabel }}</span>
            </div>
          </div>
        </div>
        <div class="stat-card kpi-enhanced">
          <div class="stat-icon" style="background:#fffbeb;color:#f59e0b"><el-icon :size="24"><TrendCharts /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ kpiData.correctness.value }}%</div>
            <div class="stat-label">整体正确率</div>
            <div class="stat-spark"><Sparkline :data="kpiData.correctness.trend" :color="'#f59e0b'" /></div>
            <div class="stat-delta" :class="kpiData.correctness.deltaDirection">
              <span class="delta-arrow">{{ deltaIcon(kpiData.correctness.deltaDirection) }}</span>
              <span>{{ kpiData.correctness.deltaLabel }}</span>
            </div>
          </div>
        </div>
        <div class="stat-card kpi-enhanced">
          <div class="stat-icon" style="background:#f5f3ff;color:#8b5cf6"><el-icon :size="24"><Document /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ kpiData.resources.value }}</div>
            <div class="stat-label">资源总数</div>
            <div class="stat-spark"><Sparkline :data="kpiData.resources.trend" :color="'#8b5cf6'" /></div>
            <div class="stat-delta" :class="kpiData.resources.deltaDirection">
              <span class="delta-arrow">{{ deltaIcon(kpiData.resources.deltaDirection) }}</span>
              <span>{{ kpiData.resources.deltaLabel }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Attention-needed cards -->
      <AttentionCards :data="attentionData" style="margin-bottom:20px" />

      <!-- Charts row 1 -->
      <div class="charts-grid">
        <div class="card chart-card">
          <div class="card-header">
            <div class="chart-header-left"><div class="chart-dot" style="background:#ef4444" />薄弱知识点分布</div>
          </div>
          <div class="card-body">
            <div ref="mistakeChartRef" class="chart-box" />
          </div>
        </div>
        <div class="card chart-card">
          <div class="card-header">
            <div class="chart-header-left"><div class="chart-dot" style="background:#6366f1" />资源类型分布</div>
          </div>
          <div class="card-body">
            <div ref="resourceChartRef" class="chart-box" />
          </div>
        </div>
      </div>

      <!-- Charts row 2 -->
      <div class="charts-grid" style="margin-top:20px">
        <div class="card chart-card">
          <div class="card-header">
            <div class="chart-header-left"><div class="chart-dot" style="background:#10b981" />正确率趋势</div>
          </div>
          <div class="card-body">
            <!-- Zero state for trend chart -->
            <div v-if="isTrendZero" class="chart-zero">
              <p class="cz-text">当前时间段没有数据</p>
              <el-button size="small" text type="primary" @click="switchRange('all')">查看全部时间</el-button>
            </div>
            <div v-else ref="rateChartRef" class="chart-box" />
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <div class="chart-header-left"><div class="chart-dot" style="background:#ef4444" />薄弱知识点列表</div>
          </div>
          <div class="card-body">
            <div v-if="weakPoints.length === 0" class="chart-zero" style="text-align:center;padding:30px">
              <p class="cz-text" style="font-size:18px">🎉 班级掌握率都不错</p>
              <p style="color:var(--ep-text-muted);font-size:13px">当前时间段没有薄弱知识点</p>
            </div>
            <div v-else class="weak-list">
              <div v-for="(wp, i) in weakPoints" :key="wp" class="weak-item">
                <span class="weak-rank" :class="i < 3 ? 'top' : ''">{{ i + 1 }}</span>
                <span class="weak-text">{{ wp }}</span>
                <span class="weak-actions">
                  <el-button size="small" text type="primary" @click="mockAction('薄弱原因分析', wp)"><el-icon><Search /></el-icon>薄弱原因分析</el-button>
                  <el-button size="small" text type="warning" @click="mockAction('推荐练习', wp)"><el-icon><EditPen /></el-icon>推荐练习</el-button>
                  <el-button size="small" text type="danger" @click="mockAction('布置给学生', wp)"><el-icon><Promotion /></el-icon>布置给学生</el-button>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Demo badge -->
      <div v-if="isDemo" class="demo-badge">📊 演示数据 — 切换时间范围可查看筛选效果</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { User, EditPen, TrendCharts, Document, Refresh, Search, Promotion } from '@element-plus/icons-vue'
import api from '../../api/index'
import { getDemoData, getDemoAttention, fetchAnalytics, type KPIData, type AttentionItem } from '../../api/teacher/analytics'
import Sparkline from '../../components/Sparkline.vue'
import SkeletonChart from '../../components/SkeletonChart.vue'
import AttentionCards from './AttentionCards.vue'

// --- state ---
const route = useRoute()
const router = useRouter()
const loading = ref(true)
const isDemo = computed(() => route.query.demo === '1')

interface MT { tag: string; count: number }
interface TS {
  total_students: number; total_answers: number; overall_correctness_rate: number
  total_resources: number; resource_type_counts: Record<string, number>
  top_mistake_tags: MT[]
  correctness_rate_trend: Array<{ date: string; correctness_rate: number; total_answers: number }>
  weak_points_summary: string[]
}

const rawData = ref<TS>({ total_students: 0, total_answers: 0, overall_correctness_rate: 0, total_resources: 0, resource_type_counts: {}, top_mistake_tags: [], correctness_rate_trend: [], weak_points_summary: [] })
const attentionData = ref<AttentionItem[]>([])

// --- time filter ---
const timeOptions = [
  { key: 'today', label: '今日' },
  { key: 'week', label: '本周' },
  { key: 'month', label: '本月' },
  { key: 'semester', label: '本学期' },
  { key: 'custom', label: '📅 自定义' },
]
const currentRange = ref<string>('week')
const customDateRange = ref<[string, string] | null>(null)
const dateShortcuts = [
  { text: '最近一周', value: (() => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 7); return [s, e] })() },
  { text: '最近一个月', value: (() => { const e = new Date(); const s = new Date(); s.setMonth(s.getMonth() - 1); return [s, e] })() },
  { text: '最近三个月', value: (() => { const e = new Date(); const s = new Date(); s.setMonth(s.getMonth() - 3); return [s, e] })() },
]

function switchRange(key: string) {
  currentRange.value = key
  const q: Record<string, string> = { range: key }
  if (isDemo.value) q.demo = '1'
  router.replace({ query: q })
  if (key !== 'custom') {
    customDateRange.value = null
    fetchData()
  }
}

function onCustomDateChange(val: [string, string] | null) {
  if (val && val.length === 2) fetchData()
}

// --- delta helper ---
function deltaIcon(dir: string) { if (dir === 'up') return '↑'; if (dir === 'down') return '↓'; return '—' }

// --- mock action ---
function mockAction(action: string, target: string) {
  ElMessage.info(`「${action}：${target}」功能开发中，敬请期待`)
}

// --- compose KPI with trend data ---
function buildKpi(key: string, value: number, defaultTrend: number[], defaultDelta: number, defaultDirection: 'up'|'down'|'flat', defaultLabel: string): KPIData {
  return { value, trend: defaultTrend, delta: defaultDelta, deltaDirection: defaultDirection, deltaLabel: defaultLabel }
}

const kpiData = computed(() => {
  const d = rawData.value
  if (isDemo.value) {
    const demo = getDemoData()
    return demo.kpi
  }
  return {
    students: buildKpi('students', d.total_students, [40, 40, 41, 41, 42, 42, d.total_students], 0, 'flat', '人数稳定'),
    answers: buildKpi('answers', d.total_answers, [0, 0, 0, 0, 0, 0, d.total_answers], 0, 'flat', '—'),
    correctness: buildKpi('correctness', d.overall_correctness_rate, [0, 0, 0, 0, 0, 0, d.overall_correctness_rate], 0, 'flat', '—'),
    resources: buildKpi('resources', d.total_resources, [0, 0, 0, 0, 0, 0, d.total_resources], 0, 'flat', '—'),
  }
})

const weakPoints = computed(() => rawData.value.weak_points_summary || [])
const isEmpty = computed(() => !loading.value && rawData.value.total_answers === 0 && rawData.value.total_students === 0 && !isDemo.value)
const isTrendZero = computed(() => rawData.value.correctness_rate_trend.length === 0 || rawData.value.correctness_rate_trend.every(x => x.total_answers === 0))

// --- charts ---
const mistakeChartRef = ref<HTMLElement>()
const resourceChartRef = ref<HTMLElement>()
const rateChartRef = ref<HTMLElement>()
const charts: echarts.ECharts[] = []

function disposeCharts() { charts.forEach(c => c.dispose()); charts.length = 0 }
function onResize() { charts.forEach(c => c.resize()) }
const CC = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#64748b']

function renderMistakeChart() {
  if (!mistakeChartRef.value) return
  const c = echarts.init(mistakeChartRef.value); charts.push(c)
  const t = rawData.value.top_mistake_tags
  c.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#0f172a', fontSize: 13 }, axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: t.map(x => x.tag), axisLabel: { rotate: 30, fontSize: 11, color: '#64748b' }, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false } },
    yAxis: { type: 'value', name: '次数', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLine: { show: false }, axisTick: { show: false }, nameTextStyle: { color: '#94a3b8', fontSize: 11 } },
    series: [{ type: 'bar', data: t.map((x, i) => ({ value: x.count, itemStyle: { color: CC[i % CC.length], borderRadius: [6, 6, 0, 0] } })), barMaxWidth: 44 }],
    grid: { left: 50, right: 20, bottom: 60, top: 30 },
  })
}

function renderResourceChart() {
  if (!resourceChartRef.value) return
  const c = echarts.init(resourceChartRef.value); charts.push(c)
  const tl: Record<string, string> = { lecture: '个性化讲解', mindmap: '思维导图', exercise: '练习题', case: '实操案例', extended_reading: '拓展阅读', video_storyboard: '视频分镜' }
  const pd = Object.entries(rawData.value.resource_type_counts).map(([n, v], i) => ({ name: tl[n] || n, value: v, itemStyle: { color: CC[i % CC.length], borderRadius: 4, borderColor: '#fff', borderWidth: 2 } }))
  if (!pd.length) pd.push({ name: '暂无数据', value: 0, itemStyle: { color: '#e2e8f0', borderRadius: 4, borderColor: '#fff', borderWidth: 2 } })
  c.setOption({
    tooltip: { trigger: 'item', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#0f172a', fontSize: 13 }, formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 11, color: '#64748b' }, itemWidth: 8, itemHeight: 8, itemGap: 16 },
    series: [{ type: 'pie', radius: ['48%', '76%'], center: ['50%', '46%'], data: pd, label: { formatter: '{b}\n{d}%', fontSize: 11, color: '#64748b', lineHeight: 16 } }],
  })
}

function renderRateChart() {
  if (!rateChartRef.value || isTrendZero.value) return
  const c = echarts.init(rateChartRef.value); charts.push(c)
  const t = rawData.value.correctness_rate_trend
  c.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#0f172a', fontSize: 13 } },
    xAxis: { type: 'category', data: t.map(i => i.date), axisLabel: { fontSize: 11, color: '#64748b' }, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisTick: { show: false } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%', fontSize: 11, color: '#64748b' }, splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLine: { show: false }, axisTick: { show: false } },
    series: [{
      type: 'line', smooth: true, data: t.map(i => i.correctness_rate),
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(99,102,241,0.12)' }, { offset: 1, color: 'rgba(99,102,241,0)' }]) },
      itemStyle: { color: '#6366f1' }, lineStyle: { width: 2.5, color: '#6366f1' }, symbolSize: 5, symbol: 'circle',
    }],
    grid: { left: 50, right: 20, bottom: 40, top: 30 },
  })
}

function renderAllCharts() {
  if (loading.value || isEmpty.value) return
  nextTick(() => { renderMistakeChart(); renderResourceChart(); renderRateChart() })
}

// --- data fetch ---
async function fetchData() {
  loading.value = true
  try {
    if (isDemo.value) {
      // demo mode
      const demo = getDemoData()
      rawData.value = demo
      attentionData.value = getDemoAttention()
    } else {
      const params: Record<string, string> = {}
      if (currentRange.value !== 'all') params.period = currentRange.value
      if (currentRange.value === 'custom' && customDateRange.value && customDateRange.value.length === 2) {
        params.period = 'custom'
        params.start_date = customDateRange.value[0]
        params.end_date = customDateRange.value[1]
      }
      const [summaryRes, attentionRes] = await Promise.all([
        fetchAnalytics(params),
        import('../../api/teacher/analytics').then(m => m.getAttentionNeeded()),
      ])
      rawData.value = summaryRes.data
      attentionData.value = attentionRes.data
    }
    await nextTick()
    disposeCharts()
    renderAllCharts()
  } catch {
    ElMessage.error('获取分析数据失败')
  } finally {
    loading.value = false
  }
}

// --- lifecycle ---
onMounted(() => {
  const qRange = route.query.range as string
  if (qRange && timeOptions.some(t => t.key === qRange)) currentRange.value = qRange
  fetchData()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => { window.removeEventListener('resize', onResize); disposeCharts() })
</script>

<style scoped>
/* header */
.header-right { display: flex; align-items: center; gap: 16px; }

/* time filter */
.time-filter { display: flex; background: var(--ep-bg-soft); border-radius: 10px; padding: 3px; gap: 1px; }
.tf-btn { padding: 7px 16px; border: none; background: transparent; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--ep-text-secondary); cursor: pointer; transition: all var(--ep-transition); white-space: nowrap; }
.tf-btn:hover { color: var(--ep-text-primary); }
.tf-btn.active { background: var(--ep-bg-elevated); color: var(--ep-primary); box-shadow: var(--ep-shadow-xs); }

/* custom date */
.custom-date-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; padding: 12px 16px; background: var(--ep-bg-soft); border-radius: var(--ep-radius-md); }
.cd-label { font-size: 13px; color: var(--ep-text-secondary); font-weight: 500; }

/* stats */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart-card { overflow: hidden; }
.chart-header-left { display: flex; align-items: center; gap: 10px; }
.chart-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.chart-box { height: 320px; }

/* KPI enhanced */
.kpi-enhanced .stat-info { display: flex; flex-direction: column; }
.kpi-enhanced .stat-spark { margin-top: 4px; }
.kpi-enhanced .stat-delta { font-size: 12px; margin-top: 4px; display: flex; align-items: center; gap: 3px; font-weight: 500; }
.stat-delta.up { color: #10b981; }
.stat-delta.down { color: #ef4444; }
.stat-delta.flat { color: #94a3b8; }
.delta-arrow { font-size: 13px; font-weight: 700; }

/* zero state */
.chart-zero { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 200px; }
.cz-text { font-size: 14px; color: var(--ep-text-muted); margin: 0 0 12px; }

/* weak list */
.weak-list { display: flex; flex-direction: column; gap: 8px; }
.weak-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: #f8fafc; border-radius: var(--ep-radius-md); transition: all var(--ep-transition); }
.weak-item:hover { background: white; box-shadow: var(--ep-shadow-xs); }
.weak-rank { width: 26px; height: 26px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; background: var(--ep-bg-soft); color: var(--ep-text-muted); flex-shrink: 0; }
.weak-rank.top { background: var(--ep-danger-light); color: #dc2626; }
.weak-text { font-size: 14px; color: var(--ep-text-primary); font-weight: 500; flex: 1; min-width: 0; }
.weak-actions { display: flex; gap: 4px; flex-shrink: 0; }

/* demo badge */
.demo-badge { text-align: center; padding: 10px; margin-top: 12px; background: #fffbeb; border: 1px solid #fde68a; border-radius: var(--ep-radius-md); font-size: 12px; color: #92400e; }

@media (max-width: 1024px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .stats-grid { grid-template-columns: 1fr; } .page-container { padding: 20px 16px; } .header-right { flex-wrap: wrap; } }
</style>
