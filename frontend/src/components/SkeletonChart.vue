<template>
  <div class="skeleton-chart" :class="'shape-' + shape">
    <div class="skeleton-inner">
      <template v-if="shape === 'bar'">
        <div v-for="i in 7" :key="i" class="sk-bar" :style="{ height: (30 + Math.random() * 70) + '%' }" />
      </template>
      <template v-else-if="shape === 'pie'">
        <div class="sk-ring" />
      </template>
      <template v-else-if="shape === 'line'">
        <div class="sk-line-wrap">
          <svg class="sk-line-svg" viewBox="0 0 400 100" preserveAspectRatio="none">
            <polyline points="0,60 60,45 120,55 180,30 240,40 300,20 360,25 400,35"
              fill="none" stroke="#e2e8f0" stroke-width="3" stroke-linecap="round" />
          </svg>
        </div>
      </template>
      <template v-else-if="shape === 'list'">
        <div v-for="i in 5" :key="i" class="sk-row">
          <div class="sk-cell short" />
          <div class="sk-cell mid" />
          <div class="sk-cell long" />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ shape: 'bar' | 'pie' | 'line' | 'list' }>()
</script>

<style scoped>
.skeleton-chart { width: 100%; height: 320px; background: var(--ep-bg-elevated); border-radius: var(--ep-radius-lg); overflow: hidden; }
.skeleton-inner { padding: 24px; display: flex; align-items: flex-end; gap: 12px; height: 100%; animation: skPulse 1.5s ease-in-out infinite; }
@keyframes skPulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }

/* bar */
.sk-bar { flex: 1; background: linear-gradient(180deg, #e2e8f0, #f1f5f9); border-radius: 6px 6px 0 0; min-height: 20px; }

/* pie */
.sk-ring { width: 200px; height: 200px; border-radius: 50%; margin: auto; background: conic-gradient(#e2e8f0 0% 30%, #f1f5f9 30% 55%, #e2e8f0 55% 80%, #f1f5f9 80% 100%); }
.shape-pie .skeleton-inner { align-items: center; justify-content: center; }

/* line */
.sk-line-wrap { flex: 1; display: flex; align-items: center; }
.sk-line-svg { width: 100%; height: 100px; }

/* list */
.shape-list .skeleton-inner { flex-direction: column; gap: 10px; }
.sk-row { display: flex; gap: 12px; width: 100%; align-items: center; }
.sk-cell { height: 12px; border-radius: 6px; background: #e2e8f0; }
.sk-cell.short { width: 24px; flex-shrink: 0; }
.sk-cell.mid { width: 40%; }
.sk-cell.long { flex: 1; }
</style>
