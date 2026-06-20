<template>
  <div class="card profile-card">
    <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
      <span style="display:flex;align-items:center;gap:8px">
        <el-icon style="color:var(--ep-primary)"><User /></el-icon>
        学生画像
      </span>
      <el-tag :type="confidenceType" effect="light" size="small" round>
        {{ confidenceLabel }}置信度
      </el-tag>
    </div>
    <div class="card-body">
      <div class="dim-grid">
        <div v-for="dim in dimensions" :key="dim.key" class="dim-item">
          <div class="dim-icon" :style="{ background: dim.bg, color: dim.color }">
            <el-icon :size="16"><component :is="dim.icon" /></el-icon>
          </div>
          <div class="dim-content">
            <div class="dim-label">{{ dim.label }}</div>
            <div class="dim-value">
              <template v-if="Array.isArray(profile[dim.key])">
                <el-tag v-for="tag in profile[dim.key]" :key="tag" size="small" effect="light" round
                        style="margin:2px 4px 2px 0">{{ tag }}</el-tag>
                <span v-if="!profile[dim.key]?.length" class="dim-empty">暂无</span>
              </template>
              <template v-else>{{ profile[dim.key] || '—' }}</template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User, Aim, Reading, WarningFilled, SuccessFilled, Star, View, Timer } from '@element-plus/icons-vue'

const props = defineProps<{ profile: Record<string, any> }>()

const confidenceType = computed(() => {
  const c = props.profile.confidence
  if (c === 'high') return 'success'
  if (c === 'medium') return 'warning'
  return 'info'
})

const confidenceLabel = computed(() => {
  const c = props.profile.confidence
  if (c === 'high') return '高'
  if (c === 'medium') return '中'
  return '低'
})

const dimensions = [
  { key: 'base_level', label: '基础水平', icon: User, bg: '#eff6ff', color: '#2563eb' },
  { key: 'learning_goal', label: '学习目标', icon: Aim, bg: '#f5f3ff', color: '#7c3aed' },
  { key: 'knowledge_state', label: '知识状态', icon: Reading, bg: '#ecfdf5', color: '#10b981' },
  { key: 'weak_points', label: '薄弱知识点', icon: WarningFilled, bg: '#fef2f2', color: '#ef4444' },
  { key: 'mastered_points', label: '已掌握知识点', icon: SuccessFilled, bg: '#ecfdf5', color: '#10b981' },
  { key: 'learning_preference', label: '学习偏好', icon: Star, bg: '#fffbeb', color: '#f59e0b' },
  { key: 'cognitive_style', label: '认知风格', icon: View, bg: '#eff6ff', color: '#2563eb' },
  { key: 'time_budget', label: '时间预算', icon: Timer, bg: '#f5f3ff', color: '#7c3aed' },
]
</script>

<style scoped>
.profile-card {
  overflow: hidden;
}

.dim-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.dim-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: var(--ep-radius-md);
  background: var(--ep-bg-hover);
  transition: background var(--ep-transition);
}

.dim-item:hover {
  background: var(--ep-bg);
}

.dim-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.dim-content {
  flex: 1;
  min-width: 0;
}

.dim-label {
  font-size: 12px;
  color: var(--ep-text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.dim-value {
  font-size: 13px;
  color: var(--ep-text-primary);
  line-height: 1.5;
}

.dim-empty {
  color: var(--ep-text-muted);
  font-size: 12px;
}
</style>
