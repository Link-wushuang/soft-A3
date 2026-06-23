<template>
  <div class="attention-grid">
    <!-- Inactive students -->
    <div class="attn-card" @click="navigate('inactive')">
      <div class="attn-header">
        <span class="attn-icon-wrap" style="background:#fef2f2;color:#ef4444"><el-icon :size="18"><WarningFilled /></el-icon></span>
        <span class="attn-label">🔴 {{ inactiveData.label }}</span>
      </div>
      <div class="attn-body">
        <div class="attn-value">{{ inactiveData.value }}<span class="attn-unit">人</span></div>
        <div class="attn-avatars">
          <div v-for="(s, i) in inactiveData.students.slice(0, 5)" :key="s.id" class="attn-avatar" :title="s.name + ' · ' + s.detail">{{ s.name.charAt(0) }}</div>
          <div v-if="inactiveData.students.length > 5" class="attn-avatar overflow">+{{ inactiveData.students.length - 5 }}</div>
        </div>
      </div>
    </div>

    <!-- Low score -->
    <div class="attn-card" @click="navigate('low_score')">
      <div class="attn-header">
        <span class="attn-icon-wrap" style="background:#fffbeb;color:#f59e0b"><el-icon :size="18"><TrendCharts /></el-icon></span>
        <span class="attn-label">🟡 {{ lowScoreData.label }}</span>
      </div>
      <div class="attn-body">
        <div class="attn-value">{{ lowScoreData.value }}<span class="attn-unit">人</span></div>
        <div class="attn-student-list">
          <div v-for="s in lowScoreData.students.slice(0, 3)" :key="s.id" class="attn-student-row">
            <span class="as-name">{{ s.name }}</span>
            <span class="as-detail">{{ s.detail }}</span>
          </div>
          <div v-if="lowScoreData.students.length > 3" class="attn-more">+{{ lowScoreData.students.length - 3 }} 人</div>
        </div>
      </div>
    </div>

    <!-- Top improvers -->
    <div class="attn-card" @click="navigate('improving')">
      <div class="attn-header">
        <span class="attn-icon-wrap" style="background:#ecfdf5;color:#10b981"><el-icon :size="18"><Top /></el-icon></span>
        <span class="attn-label">🟢 {{ improvingData.label }}</span>
      </div>
      <div class="attn-body">
        <div class="attn-value">{{ improvingData.value }}<span class="attn-unit">人</span></div>
        <div class="attn-student-list">
          <div v-for="s in improvingData.students" :key="s.id" class="attn-student-row">
            <span class="as-name">{{ s.name }}</span>
            <span class="as-detail as-up">{{ s.detail }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { WarningFilled, TrendCharts, Top } from '@element-plus/icons-vue'
import type { AttentionItem } from '../../api/teacher/analytics'

const props = defineProps<{ data: AttentionItem[] }>()

const router = useRouter()

const inactiveData = computed(() => props.data.find(d => d.type === 'inactive') || { type: 'inactive', label: '一周未登录', value: 0, students: [] })
const lowScoreData = computed(() => props.data.find(d => d.type === 'low_score') || { type: 'low_score', label: '连续3次低于60分', value: 0, students: [] })
const improvingData = computed(() => props.data.find(d => d.type === 'improving') || { type: 'improving', label: '进步最快 Top 3', value: 0, students: [] })

function navigate(filter: string) {
  router.push(`/teacher/students?filter=${filter}`)
}
</script>

<style scoped>
.attention-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.attn-card { background: var(--ep-bg-elevated); border-radius: var(--ep-radius-lg); border: 1px solid var(--ep-border-light); box-shadow: var(--ep-shadow-xs); padding: 20px; cursor: pointer; transition: all var(--ep-transition-smooth); }
.attn-card:hover { box-shadow: var(--ep-shadow-lg); transform: translateY(-2px); border-color: var(--ep-primary-lighter); }
.attn-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.attn-icon-wrap { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.attn-label { font-size: 13px; font-weight: 600; color: var(--ep-text-primary); }
.attn-body { padding-left: 0; }
.attn-value { font-size: 28px; font-weight: 700; color: var(--ep-text-primary); line-height: 1.2; margin-bottom: 8px; }
.attn-unit { font-size: 14px; font-weight: 500; color: var(--ep-text-muted); margin-left: 2px; }
.attn-avatars { display: flex; gap: 6px; flex-wrap: wrap; }
.attn-avatar { width: 30px; height: 30px; border-radius: 8px; background: linear-gradient(135deg, #fecaca, #fca5a5); color: #991b1b; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; }
.attn-avatar.overflow { background: #f3f4f6; color: var(--ep-text-muted); font-size: 10px; }
.attn-student-list { display: flex; flex-direction: column; gap: 4px; }
.attn-student-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; }
.as-name { font-weight: 500; color: var(--ep-text-primary); }
.as-detail { color: var(--ep-text-muted); font-size: 11px; }
.as-up { color: #10b981; font-weight: 600; }
.attn-more { font-size: 11px; color: var(--ep-text-muted); padding-top: 2px; }

@media (max-width: 1024px) { .attention-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .attention-grid { grid-template-columns: 1fr; } }
</style>
