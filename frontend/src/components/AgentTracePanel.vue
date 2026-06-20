<template>
  <div class="card trace-panel">
    <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
      <span>智能体进度</span>
      <span class="trace-count">{{ completedCount }}/{{ traces.length }}</span>
    </div>
    <div class="card-body" style="padding:14px 18px">
      <div v-for="(trace, i) in traces" :key="trace.agent_name" class="trace-item">
        <div class="trace-line">
          <div :class="['trace-dot', trace.status]">
            <div v-if="trace.status === 'running'" class="dot-pulse"></div>
          </div>
          <div v-if="i < traces.length - 1" :class="['trace-connector', { done: isCompleted(trace.status) }]"></div>
        </div>
        <div class="trace-info">
          <div class="trace-name">{{ agentLabels[trace.agent_name] || trace.agent_name }}</div>
          <div class="trace-meta">
            <span v-if="trace.status === 'running'" class="status-running">运行中...</span>
            <span v-else-if="trace.status === 'success'" class="status-success">{{ trace.duration_ms }}ms</span>
            <span v-else-if="trace.status === 'failed'" class="status-failed">失败</span>
            <span v-else class="status-wait">等待中</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ traces: Array<{ agent_name: string; status: string; duration_ms?: number }> }>()

const completedCount = computed(() => props.traces.filter(t => t.status === 'success' || t.status === 'failed').length)

function isCompleted(status: string) {
  return status === 'success' || status === 'failed'
}

const agentLabels: Record<string, string> = {
  ProfileAgent: '画像分析',
  KnowledgeAgent: '知识检索',
  PathPlannerAgent: '路径规划',
  LectureAgent: '讲解生成',
  MindMapAgent: '思维导图',
  ExerciseAgent: '练习生成',
  CaseAgent: '案例生成',
  ExtendedReadingAgent: '拓展阅读',
  VideoStoryboardAgent: '视频分镜',
  VerifierAgent: '事实验证',
  ContentGuardAgent: '安全审核',
  EvaluationAgent: '评估分析',
  ReflectionAgent: '反思更新',
}
</script>

<style scoped>
.trace-panel {
  position: sticky;
  top: 32px;
}

.trace-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--ep-primary);
  background: var(--ep-primary-light);
  padding: 2px 10px;
  border-radius: 10px;
}

.trace-item {
  display: flex;
  gap: 12px;
  position: relative;
}

.trace-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.trace-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
  flex-shrink: 0;
  z-index: 1;
}

.trace-dot.pending {
  background: var(--ep-border);
}

.trace-dot.running {
  background: var(--ep-primary);
}

.trace-dot.success {
  background: var(--ep-success);
}

.trace-dot.failed {
  background: var(--ep-danger);
}

.dot-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid var(--ep-primary);
  animation: pulse 1.5s infinite;
}

.trace-connector {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: var(--ep-border-light);
  transition: background var(--ep-transition);
}

.trace-connector.done {
  background: var(--ep-success);
}

.trace-info {
  padding-bottom: 16px;
  flex: 1;
}

.trace-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--ep-text-primary);
  line-height: 1;
  margin-top: -1px;
}

.trace-meta {
  font-size: 12px;
  margin-top: 4px;
}

.status-running {
  color: var(--ep-primary);
  animation: pulse 1.5s infinite;
}

.status-success {
  color: var(--ep-success);
}

.status-failed {
  color: var(--ep-danger);
}

.status-wait {
  color: var(--ep-text-muted);
}
</style>
