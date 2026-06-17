<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header style="display:flex;align-items:center;height:auto;padding:16px 0;gap:12px">
      <el-button :icon="ArrowLeft" @click="$router.back()" circle />
      <h1 style="margin:0">知识点练习</h1>
    </el-header>
    <el-main>
      <el-skeleton v-if="loading" :rows="6" animated />
      <el-empty v-else-if="!exercises.length" description="该知识点暂无练习题" />
      <div v-else>
        <ExerciseCard v-for="ex in exercises" :key="ex.id"
          :exercise="ex"
          :result="results[ex.id]"
          @submit="submitAnswer" />
      </div>
    </el-main>
  </el-container>
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
