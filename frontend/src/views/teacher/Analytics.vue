<template>
  <el-container style="padding:24px;max-width:1400px;margin:0 auto">
    <el-header style="height:auto;padding:16px 0">
      <h1 style="margin:0">数据分析</h1>
    </el-header>
    <el-main v-loading="loading">
      <el-row :gutter="16" style="margin-bottom:24px">
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align:center">
              <div style="font-size:28px;font-weight:700;color:#409eff">{{ data.total_students }}</div>
              <div style="color:#909399;margin-top:4px">学生总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align:center">
              <div style="font-size:28px;font-weight:700;color:#67c23a">{{ data.total_answers }}</div>
              <div style="color:#909399;margin-top:4px">答题总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align:center">
              <div style="font-size:28px;font-weight:700;color:#e6a23c">{{ data.overall_correctness_rate }}%</div>
              <div style="color:#909399;margin-top:4px">整体正确率</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align:center">
              <div style="font-size:28px;font-weight:700;color:#909399">{{ data.total_resources }}</div>
              <div style="color:#909399;margin-top:4px">资源总数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-card>
            <template #header>薄弱知识点分布</template>
            <div ref="mistakeChartRef" style="height:350px" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>资源类型分布</template>
            <div ref="resourceChartRef" style="height:350px" />
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top:16px">
        <el-col :span="12">
          <el-card>
            <template #header>正确率趋势</template>
            <div ref="rateChartRef" style="height:350px" />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>薄弱知识点列表</template>
            <el-tag
              v-for="wp in data.weak_points_summary"
              :key="wp"
              type="danger"
              style="margin:4px"
            >{{ wp }}</el-tag>
            <el-empty v-if="!data.weak_points_summary.length" description="暂无数据" />
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import api from '../../api/index'

interface MistakeTag {
  tag: string
  count: number
}

interface TeacherSummary {
  total_students: number
  total_answers: number
  overall_correctness_rate: number
  total_resources: number
  resource_type_counts: Record<string, number>
  top_mistake_tags: MistakeTag[]
  correctness_rate_trend: Array<{
    date: string
    correctness_rate: number
    total_answers: number
  }>
  weak_points_summary: string[]
}

const loading = ref(false)
const data = ref<TeacherSummary>({
  total_students: 0,
  total_answers: 0,
  overall_correctness_rate: 0,
  total_resources: 0,
  resource_type_counts: {},
  top_mistake_tags: [],
  correctness_rate_trend: [],
  weak_points_summary: [],
})

const mistakeChartRef = ref<HTMLElement>()
const resourceChartRef = ref<HTMLElement>()
const rateChartRef = ref<HTMLElement>()

function renderMistakeChart() {
  if (!mistakeChartRef.value) return
  const chart = echarts.init(mistakeChartRef.value)
  const tags = data.value.top_mistake_tags
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: tags.map(t => t.tag),
      axisLabel: { rotate: 30 },
    },
    yAxis: { type: 'value', name: '次数' },
    series: [{
      type: 'bar',
      data: tags.map(t => t.count),
      itemStyle: { color: '#f56c6c' },
    }],
    grid: { left: 50, right: 20, bottom: 60, top: 20 },
  })
}

function renderResourceChart() {
  if (!resourceChartRef.value) return
  const chart = echarts.init(resourceChartRef.value)
  const counts = data.value.resource_type_counts
  const pieData = Object.entries(counts).map(([name, value]) => ({ name, value }))
  if (!pieData.length) {
    pieData.push({ name: '暂无数据', value: 0 })
  }
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: pieData,
      label: { formatter: '{b}: {c}' },
    }],
  })
}

function renderRateChart() {
  if (!rateChartRef.value) return
  const chart = echarts.init(rateChartRef.value)
  const trend = data.value.correctness_rate_trend
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: trend.map(item => item.date),
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { formatter: '{value}%' },
    },
    series: [{
      type: 'line',
      smooth: true,
      data: trend.map(item => item.correctness_rate),
      areaStyle: {},
      itemStyle: { color: '#409eff' },
    }],
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
