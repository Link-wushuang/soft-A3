<script setup lang="ts">
import { computed } from 'vue'

interface DayData { date: string; minutes: number; isToday?: boolean }

const props = defineProps<{
  dailyBudgetMinutes: number
  todayMinutes: number
  weeklyData: DayData[]
  suggestion?: string
}>()

const remaining = computed(() => Math.max(0, props.dailyBudgetMinutes - props.todayMinutes))
const percent = computed(() => Math.min(100, Math.round((props.todayMinutes / props.dailyBudgetMinutes) * 100)))

const SIZE = 130; const STROKE = 11
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const dashOffset = computed(() => CIRCUMFERENCE * (1 - percent.value / 100))

const weekTotalMinutes = computed(() => props.weeklyData.reduce((s, d) => s + d.minutes, 0))

function formatMin(min: number): string {
  if (min < 60) return `${min} min`
  const h = Math.floor(min / 60)
  const m = min % 60
  return m > 0 ? `${h}h${m}min` : `${h}h`
}

const barMax = computed(() => Math.max(props.dailyBudgetMinutes * 1.5, ...props.weeklyData.map(d => d.minutes)))

const emit = defineEmits<{ plan: [] }>()
</script>

<template>
  <div class="tbc">
    <!-- Header -->
    <div class="tbc-header">
      <div class="tbc-hicon">⏰</div>
      <div>
        <div class="tbc-title">时间预算</div>
        <div class="tbc-subtitle">每天 {{ formatMin(dailyBudgetMinutes) }}</div>
      </div>
    </div>

    <!-- Ring -->
    <div class="tbc-ring-wrap">
      <div class="tbc-ring" :style="{width:SIZE+'px',height:SIZE+'px'}">
        <svg :width="SIZE" :height="SIZE" style="transform:rotate(-90deg)">
          <circle :cx="SIZE/2" :cy="SIZE/2" :r="RADIUS" fill="none" stroke="#fef3c7" :stroke-width="STROKE"/>
          <circle :cx="SIZE/2" :cy="SIZE/2" :r="RADIUS" fill="none" stroke="url(#tbcGrad)"
                  :stroke-width="STROKE" stroke-linecap="round"
                  :stroke-dasharray="CIRCUMFERENCE" :stroke-dashoffset="dashOffset"
                  style="transition:stroke-dashoffset 0.8s cubic-bezier(0.25,0.46,0.45,0.94)"/>
          <defs>
            <linearGradient id="tbcGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#fb923c"/>
            </linearGradient>
          </defs>
        </svg>
        <div class="tbc-ring-center">
          <div class="tbc-ring-num">{{ todayMinutes }}</div>
          <div class="tbc-ring-unit">/ {{ dailyBudgetMinutes }} min</div>
          <div class="tbc-ring-pct">{{ percent }}%</div>
        </div>
      </div>
    </div>

    <!-- Today status -->
    <div class="tbc-today">
      今日已学 <strong>{{ formatMin(todayMinutes) }}</strong>
      <template v-if="remaining > 0">
        · 还能学 <strong class="tbc-remain">{{ formatMin(remaining) }}</strong>
      </template>
      <template v-else>
        · <span class="tbc-done">🎉 今日达标</span>
      </template>
    </div>

    <!-- Weekly bars -->
    <div class="tbc-week">
      <div class="tbc-week-head">
        <span>本周</span>
        <span class="tbc-week-total">共 {{ formatMin(weekTotalMinutes) }}</span>
      </div>
      <div class="tbc-bars">
        <div v-for="d in weeklyData" :key="d.date" class="tbc-bar-col" :title="`${d.date}: ${d.minutes} min`">
          <div class="tbc-bar-track">
            <div class="tbc-bar-fill"
                 :class="d.isToday ? 'today' : ''"
                 :style="{height: `${Math.max(3,(d.minutes/barMax)*100)}%`}"/>
          </div>
          <span class="tbc-bar-label" :class="{today: d.isToday}">{{ d.date }}</span>
        </div>
      </div>
    </div>

    <!-- Suggestion -->
    <div v-if="suggestion" class="tbc-sugg">⚡ {{ suggestion }}</div>

    <!-- Action -->
  </div>
</template>

<style scoped>
.tbc { padding:4px 0; }
.tbc-header { display:flex;align-items:center;gap:10px;margin-bottom:10px; }
.tbc-hicon { width:36px;height:36px;border-radius:8px;background:#fffbeb;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:18px; }
.tbc-title { font-size:13px;font-weight:600;color:var(--ep-text-primary); }
.tbc-subtitle { font-size:10px;color:var(--ep-text-muted);margin-top:1px; }

.tbc-ring-wrap { display:flex;justify-content:center;margin:4px 0 8px; }
.tbc-ring { position:relative; }
.tbc-ring-center { position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center; }
.tbc-ring-num { font-size:30px;font-weight:800;line-height:1;color:var(--ep-text-primary);letter-spacing:-0.03em; }
.tbc-ring-unit { font-size:9px;color:var(--ep-text-muted);margin-top:2px; }
.tbc-ring-pct { font-size:10px;font-weight:600;color:#f59e0b;margin-top:2px; }

.tbc-today { text-align:center;font-size:11px;color:var(--ep-text-secondary);margin-bottom:10px; }
.tbc-today strong { color:var(--ep-text-primary); }
.tbc-remain { color:#f59e0b; }
.tbc-done { color:#10b981;font-weight:600; }

.tbc-week { background:#f8fafc;border-radius:10px;padding:10px 8px 6px;margin-bottom:8px; }
.tbc-week-head { display:flex;justify-content:space-between;font-size:9px;color:var(--ep-text-muted);margin-bottom:6px; }
.tbc-week-total { font-weight:600;color:var(--ep-text-secondary); }
.tbc-bars { display:flex;align-items:flex-end;justify-content:space-between;gap:2px;height:46px; }
.tbc-bar-col { flex:1;display:flex;flex-direction:column;align-items:center;gap:3px; }
.tbc-bar-track { flex:1;width:100%;display:flex;align-items:flex-end; }
.tbc-bar-fill { width:100%;border-radius:3px 3px 0 0;background:#cbd5e1;transition:height 0.5s ease;min-height:2px; }
.tbc-bar-fill.today { background:linear-gradient(to top,#f59e0b,#fb923c); }
.tbc-bar-col:hover .tbc-bar-fill:not(.today) { background:#94a3b8; }
.tbc-bar-label { font-size:8px;color:var(--ep-text-muted);line-height:1; } .tbc-bar-label.today { color:#f59e0b;font-weight:700; }

.tbc-sugg { font-size:10px;color:var(--ep-text-secondary);margin-bottom:6px;display:flex;align-items:flex-start;gap:4px;line-height:1.4; }
</style>
