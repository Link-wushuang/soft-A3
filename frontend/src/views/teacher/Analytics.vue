<template>
  <div class="page-container" style="max-width:1400px">
    <div class="page-header">
      <div>
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">全局学习数据概览与趋势分析</p>
      </div>
    </div>

    <div v-loading="loading">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon" style="background:#eff6ff;color:#2563eb">
            <el-icon :size="22"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ data.total_students }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#ecfdf5;color:#10b981">
            <el-icon :size="22"><EditPen /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ data.total_answers }}</div>
            <div class="stat-label">答题总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fffbeb;color:#f59e0b">
            <el-icon :size="22"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ data.overall_correctness_rate }}%</div>
            <div class="stat-label">整体正确率</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#f5f3ff;color:#7c3aed">
            <el-icon :size="22"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ data.total_resources }}</div>
            <div class="stat-label">资源总数</div>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="card">
          <div class="card-header">薄弱知识点分布</div>
          <div class="card-body">
            <div ref="mistakeChartRef" style="height:320px" />
          </div>
        </div>
        <div class="card">
          <div class="card-header">资源类型分布</div>
          <div class="card-body">
            <div ref="resourceChartRef" style="height:320px" />
          </div>
        </div>
      </div>

      <div class="charts-grid" style="margin-top:20px">
        <div class="card">
          <div class="card-header">正确率趋势</div>
          <div class="card-body">
            <div ref="rateChartRef" style="height:320px" />
          </div>
        </div>
        <div class="card">
          <div class="card-header" style="display:flex;align-items:center;gap:8px">
            <el-icon style="color:var(--ep-danger)"><WarningFilled /></el-icon>
            薄弱知识点列表
          </div>
          <div class="card-body">
            <div v-if="data.weak_points_summary.length" class="weak-list">
              <div v-for="(wp, i) in data.weak_points_summary" :key="wp" class="weak-item">
                <span class="weak-num">{{ i + 1 }}</span>
                <span>{{ wp }}</span>
              </div>
            </div>
            <el-empty v-else description="暂无数据" :image-size="80" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { User, EditPen, TrendCharts, Document, WarningFilled } from '@element-plus/icons-vue'
import api from '../../api/index'

interface MistakeTag { tag: string; count: number }

interface TeacherSummary {
  total_students: number
  total_answers: number
  overall_correctness_rate: number
  total_resources: number
  resource_type_counts: Record<string, number>
  top_mistake_tags: MistakeTag[]
  correctness_rate_trend: Array<{ date: string; correctness_rate: number; total_answers: number }>
  weak_points_summary: string[]
}

const loading = ref(false)
const data = ref<TeacherSummary>({
  total_students: 0, total_answers: 0, overall_correctness_rate: 0, total_resources: 0,
  resource_type_counts: {}, top_mistake_tags: [], correctness_rate_trend: [], weak_points_summary: [],
})

const mistakeChartRef = ref<HTMLElement>()
const resourceChartRef = ref<HTMLElement>()
const rateChartRef = ref<HTMLElement>()

function renderMistakeChart() {
  if (!mistakeChartRef.value) return
  const chart = echarts.init(mistakeChartRef.value)
  const tags = data.value.top_mistake_tags
  chart.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#1e293b' } },
    xAxis: { type: 'category', data: tags.map(t => t.tag), axisLabel: { rotate: 30, fontSize: 11 }, axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'value', name: '次数', splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLine: { show: false } },
    series: [{ type: 'bar', data: tags.map(t => t.count), itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, barMaxWidth: 40 }],
    grid: { left: 50, right: 20, bottom: 60, top: 30 },
  })
}

function renderResourceChart() {
  if (!resourceChartRef.value) return
  const chart = echarts.init(resourceChartRef.value)
  const counts = data.value.resource_type_counts
  const colors = ['#2563eb', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#64748b']
  const pieData = Object.entries(counts).map(([name, value], i) => ({ name, value, itemStyle: { color: colors[i % colors.length] } }))
  if (!pieData.length) pieData.push({ name: '暂无数据', value: 0, itemStyle: { color: '#e2e8f0' } })
  chart.setOption({
    tooltip: { trigger: 'item', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#1e293b' } },
    legend: { bottom: 0, textStyle: { fontSize: 11 } },
    series: [{ type: 'pie', radius: ['45%', '72%'], data: pieData, label: { formatter: '{b}: {c}', fontSize: 11 }, itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 } }],
  })
}

function renderRateChart() {
  if (!rateChartRef.value) return
  const chart = echarts.init(rateChartRef.value)
  const trend = data.value.correctness_rate_trend
  chart.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#1e293b' } },
    xAxis: { type: 'category', data: trend.map(i => i.date), axisLine: { lineStyle: { color: '#e2e8f0' } } },
    yAxis: { type: 'value', min: 0, max: 100, axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: '#f1f5f9' } }, axisLine: { show: false } },
    series: [{ type: 'line', smooth: true, data: trend.map(i => i.correctness_rate), areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(37,99,235,0.15)' }, { offset: 1, color: 'rgba(37,99,235,0)' }]) }, itemStyle: { color: '#2563eb' }, lineStyle: { width: 2 }, symbolSize: 6 }],
    grid: { left: 50, right: 20, bottom: 40, top: 30 },
  })
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/analytics/teacher-summary')
    data.value = res.data
    await nextTick()
    renderMistakeChart()
    renderResourceChart()
    renderRateChart()
  } catch {
    ElMessage.error('获取分析数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.weak-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weak-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--ep-bg-hover);
  border-radius: var(--ep-radius-sm);
  font-size: 14px;
}

.weak-num {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--ep-danger-light);
  color: var(--ep-danger);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
</style>
