<template>
  <el-card>
    <template #header>智能体执行进度 ({{ completedCount }}/{{ traces.length }})</template>
    <el-steps direction="vertical" :active="completedCount" finish-status="success">
      <el-step v-for="trace in traces" :key="trace.agent_name"
        :title="trace.agent_name"
        :status="stepStatus(trace.status)"
        :description="trace.duration_ms ? `${trace.duration_ms}ms` : '等待中...'" />
    </el-steps>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ traces: Array<{ agent_name: string; status: string; duration_ms?: number }> }>()

const completedCount = computed(() => props.traces.filter(t => t.status === 'success' || t.status === 'failed').length)

function stepStatus(status: string) {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'error'
  if (status === 'running') return 'process'
  return 'wait'
}
</script>
