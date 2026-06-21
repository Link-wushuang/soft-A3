<template>
  <div class="card profile-card">
    <div class="card-header profile-header">
      <div class="profile-header-left">
        <div class="profile-header-icon"><el-icon :size="16"><User /></el-icon></div><span>学生画像</span>
      </div>
      <span :class="['confidence-badge', profile.confidence]"><span class="confidence-dot" />{{ confidenceLabel }}置信度</span>
    </div>
    <div class="card-body">
      <div class="dim-grid">
        <div v-for="dim in dimensions" :key="dim.key" class="dim-item">
          <div class="dim-icon" :style="{ background: dim.bg, color: dim.color }"><el-icon :size="15"><component :is="dim.icon" /></el-icon></div>
          <div class="dim-content">
            <div class="dim-label">{{ dim.label }}</div>
            <div class="dim-value">
              <template v-if="Array.isArray(profile[dim.key])">
                <div v-if="profile[dim.key]?.length" class="dim-tags"><span v-for="tag in profile[dim.key]" :key="tag" class="dim-tag">{{ tag }}</span></div>
                <span v-else class="dim-empty">暂无</span>
              </template>
              <template v-else>{{ dimValue(dim.key) }}</template>
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
const confidenceLabel = computed(() => { const c = props.profile.confidence; if (c==='high') return '高'; if (c==='medium') return '中'; return '低' })

const LEVEL_MAP: Record<string,string> = { beginner:'初学者', medium:'中等', advanced:'进阶' }
const STYLE_MAP: Record<string,string> = { visual:'视觉型', verbal:'文字型', hands_on:'实操型' }
function dimValue(key: string) {
  const v = props.profile[key]
  if (v == null || v === '') return '—'
  if (key === 'base_level') return LEVEL_MAP[v] || v
  if (key === 'cognitive_style') return STYLE_MAP[v] || v
  return v
}
const dimensions = [
  { key:'base_level', label:'基础水平', icon:User, bg:'#eef2ff', color:'#6366f1' },
  { key:'learning_goal', label:'学习目标', icon:Aim, bg:'#f5f3ff', color:'#8b5cf6' },
  { key:'knowledge_state', label:'知识状态', icon:Reading, bg:'#ecfdf5', color:'#10b981' },
  { key:'weak_points', label:'薄弱知识点', icon:WarningFilled, bg:'#fef2f2', color:'#ef4444' },
  { key:'mastered_points', label:'已掌握知识点', icon:SuccessFilled, bg:'#ecfdf5', color:'#10b981' },
  { key:'learning_preference', label:'学习偏好', icon:Star, bg:'#fffbeb', color:'#f59e0b' },
  { key:'cognitive_style', label:'认知风格', icon:View, bg:'#eef2ff', color:'#6366f1' },
  { key:'time_budget', label:'时间预算', icon:Timer, bg:'#f5f3ff', color:'#8b5cf6' },
]
</script>

<style scoped>
.profile-card { overflow: hidden; }
.profile-header { display: flex; justify-content: space-between; align-items: center; }
.profile-header-left { display: flex; align-items: center; gap: 10px; }
.profile-header-icon { width: 30px; height: 30px; border-radius: 8px; background: var(--ep-primary-light); color: var(--ep-primary); display: flex; align-items: center; justify-content: center; }
.confidence-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.confidence-badge.high { background: var(--ep-success-light); color: #059669; }
.confidence-badge.medium { background: var(--ep-warning-light); color: #d97706; }
.confidence-badge.low { background: #f1f5f9; color: #64748b; }
.confidence-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.dim-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; }
.dim-item { display: flex; gap: 12px; padding: 14px; border-radius: var(--ep-radius-md); background: #f8fafc; border: 1px solid transparent; transition: all var(--ep-transition); }
.dim-item:hover { background: white; border-color: var(--ep-border); box-shadow: var(--ep-shadow-xs); }
.dim-icon { width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.dim-content { flex: 1; min-width: 0; }
.dim-label { font-size: 11px; color: var(--ep-text-secondary); margin-bottom: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }
.dim-value { font-size: 13px; color: var(--ep-text-primary); line-height: 1.5; font-weight: 500; }
.dim-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.dim-tag { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500; background: var(--ep-bg-soft); color: var(--ep-text-secondary); }
.dim-empty { color: var(--ep-text-muted); font-size: 12px; }
</style>
