<template>
  <div class="path-list">
    <div v-for="(node, i) in nodes" :key="node.id" class="path-node" @click="$emit('nodeClick', node)">
      <div class="node-indicator">
        <div :class="['node-dot', node.status]">
          <el-icon v-if="node.status === 'completed'" :size="12"><Check /></el-icon>
          <span v-else-if="node.status === 'in_progress'" class="dot-inner pulse"></span>
          <span v-else class="dot-inner"></span>
        </div>
        <div v-if="i < nodes.length - 1" :class="['node-line', { completed: node.status === 'completed' }]"></div>
      </div>
      <div :class="['node-card card', { active: node.status === 'in_progress' }]">
        <div class="node-header">
          <span class="node-order">{{ i + 1 }}</span>
          <strong class="node-title">{{ node.knowledge_point_title || node.title }}</strong>
          <el-tag :type="statusType(node.status)" size="small" effect="light" round>
            {{ statusLabel(node.status) }}
          </el-tag>
        </div>
        <p v-if="node.reason" class="node-reason">{{ node.reason }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'

defineProps<{ nodes: Array<{ id: number; knowledge_point_title?: string; title?: string; status: string; reason: string }> }>()
defineEmits<{ nodeClick: [node: any] }>()

function statusType(s: string) {
  if (s === 'completed') return 'success'
  if (s === 'in_progress') return 'primary'
  return 'info'
}

function statusLabel(s: string) {
  if (s === 'completed') return '已完成'
  if (s === 'in_progress') return '进行中'
  return '待学习'
}
</script>

<style scoped>
.path-list {
  display: flex;
  flex-direction: column;
}

.path-node {
  display: flex;
  gap: 16px;
  cursor: pointer;
}

.node-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24px;
  flex-shrink: 0;
  padding-top: 18px;
}

.node-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
  transition: all var(--ep-transition);
}

.node-dot.completed {
  background: var(--ep-success);
  color: white;
}

.node-dot.in_progress {
  background: var(--ep-primary);
}

.node-dot.pending {
  background: var(--ep-bg);
  border: 2px solid var(--ep-border);
}

.dot-inner {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
}

.dot-inner.pulse {
  animation: pulse 1.5s infinite;
}

.node-line {
  width: 2px;
  flex: 1;
  min-height: 12px;
  background: var(--ep-border-light);
  transition: background var(--ep-transition);
}

.node-line.completed {
  background: var(--ep-success);
}

.node-card {
  flex: 1;
  padding: 16px 20px;
  margin-bottom: 10px;
  transition: all var(--ep-transition);
}

.node-card:hover {
  transform: translateX(4px);
  box-shadow: var(--ep-shadow-md) !important;
}

.node-card.active {
  border-color: var(--ep-primary) !important;
  background: var(--ep-primary-light);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.node-order {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--ep-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--ep-text-secondary);
  flex-shrink: 0;
}

.node-title {
  flex: 1;
  font-size: 14px;
}

.node-reason {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--ep-text-secondary);
  padding-left: 34px;
}
</style>
