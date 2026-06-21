<script setup lang="ts">
import { computed, ref } from 'vue'

interface Cluster {
  topic: string
  total: number
  mastered: number
  learning: number
  weak: number
}

const props = defineProps<{
  subject: string
  overallPercent: number
  clusters: Cluster[]
}>()

const W = 280
const H = 160
const TOPIC_COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4']

const hoverId = ref<string | null>(null)

const nodes = computed(() => {
  const cols = 3
  const cellW = W / cols
  const cellH = H / 2
  return props.clusters.map((c, i) => {
    const col = i % cols
    const row = Math.floor(i / cols)
    return {
      ...c,
      x: col * cellW + cellW / 2 + ((i % 2 ? 1 : -1) * 6),
      y: row * cellH + cellH / 2 + ((i % 3 ? 1 : -1) * 5),
      r: 8 + Math.sqrt(c.total) * 3.2,
      topicColor: TOPIC_COLORS[i % TOPIC_COLORS.length],
    }
  })
})

function colorOf(c: Cluster): string {
  if (c.total === 0 || c.mastered === 0) return '#e5e7eb'
  const rate = c.mastered / c.total
  if (rate >= 0.8) return '#10b981'
  if (rate >= 0.4) return '#f59e0b'
  return '#ef4444'
}

function statusOf(c: Cluster): string {
  if (c.total === 0 || c.mastered === 0) return '未开始'
  const rate = c.mastered / c.total
  if (rate >= 0.8) return '已掌握'
  if (rate >= 0.4) return '学习中'
  return '薄弱'
}

const totalPoints = computed(() => props.clusters.reduce((s, c) => s + c.total, 0))
const masteredPoints = computed(() => props.clusters.reduce((s, c) => s + c.mastered, 0))
</script>

<template>
  <div class="mini-kmap">
    <div class="kmap-header">
      <div class="kmap-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="3" fill="#6366f1"/>
          <circle cx="6" cy="6" r="2" fill="#10b981"/>
          <circle cx="18" cy="7" r="2.5" fill="#f59e0b"/>
          <circle cx="8" cy="17" r="2.2" fill="#ec4899"/>
          <circle cx="17" cy="15" r="2.8" fill="#8b5cf6"/>
        </svg>
      </div>
      <div>
        <div class="kmap-pct">{{ overallPercent }}%</div>
        <div class="kmap-label">总掌握率</div>
      </div>
    </div>

    <div class="kmap-svg-wrap">
      <svg :viewBox="`0 0 ${W} ${H}`" class="kmap-svg">
        <circle :cx="W/2" :cy="H/2" r="22"
                fill="#6366f1" fill-opacity="0.06"
                stroke="#6366f1" stroke-opacity="0.15"
                stroke-dasharray="3 3" />
        <text :x="W/2" :y="H/2 - 2" text-anchor="middle"
              font-size="10" fill="#6366f1" font-weight="600">{{ subject }}</text>
        <text :x="W/2" :y="H/2 + 10" text-anchor="middle"
              font-size="8" fill="#94a3b8">学科中心</text>

        <line v-for="n in nodes" :key="`l-${n.topic}`"
              :x1="W/2" :y1="H/2" :x2="n.x" :y2="n.y"
              stroke="#cbd5e1" stroke-width="1" stroke-dasharray="2 3"
              :opacity="hoverId && hoverId !== n.topic ? 0.2 : 0.6" />

        <g v-for="n in nodes" :key="n.topic"
           @mouseenter="hoverId = n.topic"
           @mouseleave="hoverId = null"
           style="cursor:pointer">
          <circle :cx="n.x" :cy="n.y" :r="n.r + 2"
                  :fill="colorOf(n)" :opacity="0.2" style="filter:blur(2px)" />
          <circle :cx="n.x" :cy="n.y" :r="n.r"
                  :fill="colorOf(n)" :stroke="n.topicColor"
                  :stroke-width="hoverId === n.topic ? 2 : 1.2"
                  :opacity="hoverId && hoverId !== n.topic ? 0.35 : 1"
                  style="transition:all 0.2s" />
          <text :x="n.x" :y="n.y + 3" text-anchor="middle"
                font-size="9" fill="#fff" font-weight="600"
                style="pointer-events:none">{{ n.topic }}</text>

          <g v-if="n.total > 0">
            <circle :cx="n.x + n.r * 0.7" :cy="n.y - n.r * 0.7"
                    r="6" fill="white"
                    :stroke="n.topicColor" stroke-width="1.2" />
            <text :x="n.x + n.r * 0.7" :y="n.y - n.r * 0.7 + 3"
                  text-anchor="middle" font-size="8"
                  :fill="n.topicColor" font-weight="700">{{ n.mastered }}</text>
          </g>
        </g>

        <g v-if="hoverId">
          <template v-for="n in nodes" :key="`tip-${n.topic}`">
            <g v-if="n.topic === hoverId">
              <rect :x="n.x - 50" :y="n.y - n.r - 28"
                    width="100" height="20" rx="4" fill="#0f172a" />
              <text :x="n.x" :y="n.y - n.r - 14"
                    text-anchor="middle" font-size="10" fill="#fff">
                {{ n.topic }} · {{ statusOf(n) }} {{ n.mastered }}/{{ n.total }}
              </text>
            </g>
          </template>
        </g>
      </svg>
    </div>

    <div class="kmap-legend">
      <span class="legend-item"><span class="legend-dot bg-emerald-500" />已掌握</span>
      <span class="legend-item"><span class="legend-dot bg-amber-500" />学习中</span>
      <span class="legend-item"><span class="legend-dot bg-red-500" />薄弱</span>
      <span class="legend-item"><span class="legend-dot bg-slate-300" />未开始</span>
    </div>
    <div class="kmap-summary">
      {{ clusters.length }} 主题 · {{ totalPoints }} 知识点 · 已掌握 {{ masteredPoints }}/{{ totalPoints }}
    </div>

  </div>
</template>

<style scoped>
.mini-kmap { font-size:12px; }
.kmap-header { display:flex;align-items:center;gap:10px;margin-bottom:10px; }
.kmap-icon { width:36px;height:36px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.kmap-pct { font-size:24px;font-weight:800;line-height:1;letter-spacing:-0.03em;color:var(--ep-text-primary); }
.kmap-label { font-size:11px;color:var(--ep-text-secondary);margin-top:2px; }
.kmap-svg-wrap { border-radius:12px;background:linear-gradient(135deg,#f8fafc,#fff);border:1px solid #f1f5f9;overflow:hidden; }
.kmap-svg { width:100%;height:160px;display:block; }
.kmap-legend { display:flex;align-items:center;gap:10px;margin-top:8px;font-size:10px;color:var(--ep-text-muted); }
.legend-item { display:flex;align-items:center;gap:3px; }
.legend-dot { width:6px;height:6px;border-radius:50%;flex-shrink:0; }
.legend-dot.bg-emerald-500 { background:#10b981; } .legend-dot.bg-amber-500 { background:#f59e0b; } .legend-dot.bg-red-500 { background:#ef4444; } .legend-dot.bg-slate-300 { background:#cbd5e1; }
.kmap-summary { font-size:10px;color:var(--ep-text-muted);margin-top:4px; }
</style>
