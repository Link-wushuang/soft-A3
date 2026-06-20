<template>
  <div :class="['safety-badge', badgeClass]">
    <el-icon :size="12"><component :is="icon" /></el-icon>
    <span>{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { SuccessFilled, WarningFilled, CircleCloseFilled, Loading } from '@element-plus/icons-vue'

const props = defineProps<{ status: string; warnings?: string[] }>()

const hasWarnings = computed(() => props.warnings && props.warnings.length > 0)

const badgeClass = computed(() => {
  if (props.status === 'blocked') return 'blocked'
  if (hasWarnings.value) return 'warning'
  if (props.status === 'passed') return 'passed'
  return 'pending'
})

const icon = computed(() => {
  if (props.status === 'blocked') return CircleCloseFilled
  if (hasWarnings.value) return WarningFilled
  if (props.status === 'passed') return SuccessFilled
  return Loading
})

const label = computed(() => {
  if (props.status === 'blocked') return '已过滤'
  if (hasWarnings.value) return '有警告'
  if (props.status === 'passed') return '已验证'
  return '待验证'
})
</script>

<style scoped>
.safety-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.safety-badge.passed {
  background: var(--ep-success-light);
  color: var(--ep-success);
}

.safety-badge.warning {
  background: var(--ep-warning-light);
  color: var(--ep-warning);
}

.safety-badge.blocked {
  background: var(--ep-danger-light);
  color: var(--ep-danger);
}

.safety-badge.pending {
  background: var(--ep-bg);
  color: var(--ep-text-muted);
}
</style>
