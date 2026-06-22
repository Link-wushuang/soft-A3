<template>
  <div class="page-container" style="max-width:800px">
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:12px">
        <button class="back-btn" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <div>
          <h1 class="page-title">知识点练习</h1>
          <p class="page-subtitle">完成练习后系统将自动评估并更新学习画像</p>
        </div>
      </div>
    </div>

    <div v-if="evalSummary" class="card eval-summary">
      <div class="card-body">
        <div class="eval-header">
          <el-icon :size="20" style="color:var(--ep-primary)"><TrendCharts /></el-icon>
          <span style="font-weight:600;font-size:15px">练习评估报告</span>
        </div>
        <div class="eval-stats">
          <div class="eval-stat">
            <div class="eval-stat-value">{{ evalSummary.totalAnswered }}</div>
            <div class="eval-stat-label">已作答</div>
          </div>
          <div class="eval-stat">
            <div class="eval-stat-value" style="color:var(--ep-success)">{{ evalSummary.correctCount }}</div>
            <div class="eval-stat-label">正确</div>
          </div>
          <div class="eval-stat">
            <div class="eval-stat-value" style="color:var(--ep-danger)">{{ evalSummary.wrongCount }}</div>
            <div class="eval-stat-label">错误</div>
          </div>
          <div class="eval-stat">
            <div class="eval-stat-value" style="color:var(--ep-warning)">{{ evalSummary.accuracy }}%</div>
            <div class="eval-stat-label">正确率</div>
          </div>
        </div>
        <div v-if="profileUpdates.length" class="profile-updates-list">
          <div class="profile-updates-header">
            <el-icon style="color:var(--ep-primary)"><Refresh /></el-icon>
            <span>画像动态更新记录</span>
          </div>
          <div v-for="(upd, i) in profileUpdates" :key="i" class="profile-update-item">
            <el-icon :size="14" style="color:var(--ep-primary);flex-shrink:0"><InfoFilled /></el-icon>
            <span>{{ upd }}</span>
          </div>
        </div>
      </div>
    </div>

    <el-skeleton v-if="loading" :rows="6" animated />
    <div v-else-if="!exercises.length" class="card">
      <div class="card-body" style="text-align:center;padding:60px 40px">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none" style="margin-bottom:20px">
          <rect width="56" height="56" rx="14" fill="#fffbeb"/>
          <path d="M22 22H34M22 28H30M22 34H34" stroke="#f59e0b" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3 style="margin:0 0 8px;font-size:18px">该知识点暂无练习题</h3>
        <p style="color:var(--ep-text-secondary);margin:0;font-size:14px">
          请先生成学习资源以获得练习题
        </p>
      </div>
    </div>
    <div v-else class="exercise-list">
      <ExerciseCard v-for="(ex, i) in exercises" :key="ex.id"
        :exercise="ex"
        :index="i + 1"
        :result="results[ex.id]"
        @submit="submitAnswer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, TrendCharts, Refresh, InfoFilled } from '@element-plus/icons-vue'
import api from '../../api/index'
import ExerciseCard from '../../components/ExerciseCard.vue'

const route = useRoute()
const kpId = Number(route.params.knowledgePointId)
const exercises = ref<any[]>([])
const loading = ref(true)
const results = reactive<Record<number, any>>({})
const profileUpdates = ref<string[]>([])

const evalSummary = computed(() => {
  const answered = Object.values(results)
  if (!answered.length) return null
  const correct = answered.filter((r: any) => r.evaluation?.is_correct).length
  return {
    totalAnswered: answered.length,
    correctCount: correct,
    wrongCount: answered.length - correct,
    accuracy: Math.round(correct / answered.length * 100),
  }
})

onMounted(async () => {
  try {
    const res = await api.get('/exercises', { params: { knowledge_point_id: kpId } })
    exercises.value = res.data
  } catch {
    ElMessage.error('加载练习题失败')
  }
  loading.value = false
})

async function submitAnswer(exerciseId: number, answer: string) {
  try {
    const res = await api.post(`/exercises/${exerciseId}/submit`, { user_answer: answer })
    results[exerciseId] = res.data
    if (res.data.profile_updated && res.data.reflection?.change_reason) {
      profileUpdates.value.push(res.data.reflection.change_reason)
    }
  } catch {
    ElMessage.error('提交失败')
  }
}
</script>

<style scoped>
.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.eval-summary {
  margin-bottom: 20px;
}

.eval-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.eval-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.eval-stat {
  text-align: center;
  padding: 12px;
  background: var(--ep-bg-hover);
  border-radius: var(--ep-radius-md);
}

.eval-stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--ep-text-primary);
}

.eval-stat-label {
  font-size: 12px;
  color: var(--ep-text-secondary);
  margin-top: 4px;
}

.profile-updates-list {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--ep-border-light);
}

.profile-updates-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--ep-text-primary);
  margin-bottom: 10px;
}

.profile-update-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--ep-primary-light);
  border-radius: var(--ep-radius-sm);
  font-size: 13px;
  color: var(--ep-primary);
  margin-bottom: 6px;
}
</style>
