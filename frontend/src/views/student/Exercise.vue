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
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import api from '../../api/index'
import ExerciseCard from '../../components/ExerciseCard.vue'

const route = useRoute()
const kpId = Number(route.params.knowledgePointId)
const exercises = ref<any[]>([])
const loading = ref(true)
const results = reactive<Record<number, any>>({})

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
  } catch {
    ElMessage.error('提交失败')
  }
}
</script>

<style scoped>
.back-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--ep-radius-sm);
  border: 1px solid var(--ep-border);
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--ep-transition);
  color: var(--ep-text-secondary);
}

.back-btn:hover {
  border-color: var(--ep-primary);
  color: var(--ep-primary);
}

.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
