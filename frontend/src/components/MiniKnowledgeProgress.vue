<script setup lang="ts">
import { computed, ref } from 'vue'

interface KpItem { title: string; status: 'mastered' | 'learning' | 'weak' | 'untouched' }

const props = defineProps<{ total: number; mastered: string[]; weak: string[]; untouched: string[] }>()

const W = 260; const H = 140

const MASTERED_HUES = ['#10b981','#059669','#14b8a6','#0d9488','#22c55e','#34d399','#06b6d4']
const WEAK_HUES = ['#ef4444','#f97316','#e11d48','#dc2626','#ea580c','#fb923c','#f43f5e']
const UNTOUCHED_HUES = ['#cbd5e1','#94a3b8','#b0bec5','#9ca3af','#bdbdbd','#a8a29e','#c0c8d4']

function dotColor(status: string, idx: number): string {
  if (status === 'mastered') return MASTERED_HUES[idx % MASTERED_HUES.length]
  if (status === 'weak') return WEAK_HUES[idx % WEAK_HUES.length]
  return UNTOUCHED_HUES[idx % UNTOUCHED_HUES.length]
}

const STATUS_LABEL: Record<string, string> = {
  mastered: '已掌握', learning: '学习中', weak: '薄弱', untouched: '未学习',
}

const hoverId = ref<number | null>(null)

const dots = computed(() => {
  const all: KpItem[] = []
  let mi = 0; let wi = 0; let ui = 0
  props.mastered.forEach(t => all.push({ title: t, status: 'mastered' }))
  props.weak.forEach(t => all.push({ title: t, status: 'weak' }))
  props.untouched.forEach(t => all.push({ title: t, status: 'untouched' }))
  return all.map((item, i) => {
    let colorIdx: number
    if (item.status === 'mastered') { colorIdx = mi; mi++ }
    else if (item.status === 'weak') { colorIdx = wi; wi++ }
    else { colorIdx = ui; ui++ }
    const angle = (i / all.length) * Math.PI * 2 - Math.PI / 2
    const orbit = 36 + (i % 3) * 18 + Math.floor(i / 8) * 16
    const cx = W / 2 + Math.cos(angle) * orbit
    const cy = H / 2 + Math.sin(angle) * orbit * 0.75
    return { ...item, x: cx, y: cy, r: item.status === 'untouched' ? 6 : 8 + (i % 5) * 0.6, id: i, ci: colorIdx }
  })
})

const counts = computed(() => ({
  mastered: props.mastered.length,
  weak: props.weak.length,
  untouched: props.untouched.length,
}))
</script>

<template>
  <div class="mkp">
    <div class="mkp-header">
      <div class="mkp-icon">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="5" cy="5" r="3" fill="#10b981"/><circle cx="11" cy="4" r="2.2" fill="#14b8a6"/>
          <circle cx="9" cy="11" r="3.5" fill="#f97316"/><circle cx="13" cy="12" r="2.5" fill="#e11d48"/>
          <circle cx="5" cy="13" r="2.5" fill="#94a3b8"/>
        </svg>
      </div>
      <div>
        <div class="mkp-num">{{ mastered.length + weak.length }}<span class="mkp-unit">个</span></div>
        <div class="mkp-label">已学知识点</div>
      </div>
    </div>

    <div class="mkp-svg-wrap">
      <svg :viewBox="`0 0 ${W} ${H}`" class="mkp-svg">
        <!-- Orbit rings -->
        <ellipse :cx="W/2" :cy="H/2" rx="54" ry="40" fill="none" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="2 3"/>
        <ellipse :cx="W/2" :cy="H/2" rx="36" ry="27" fill="none" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="2 4"/>

        <!-- Center: total count -->
        <circle :cx="W/2" :cy="H/2" r="16" fill="white" stroke="#e2e8f0" stroke-width="1"/>
        <text :x="W/2" :y="H/2 - 2" text-anchor="middle" font-size="11" fill="#0f172a" font-weight="700">{{ total }}</text>
        <text :x="W/2" :y="H/2 + 10" text-anchor="middle" font-size="7" fill="#94a3b8">总计</text>

        <!-- Dots -->
        <g v-for="d in dots" :key="d.id"
           @mouseenter="hoverId = d.id" @mouseleave="hoverId = null"
           style="cursor:pointer">
          <circle :cx="d.x" :cy="d.y" :r="d.r + 3"
                  :fill="dotColor(d.status, d.ci)" opacity="0.15"
                  :style="{ filter: 'blur(2px)', opacity: hoverId === d.id ? 0.3 : 0.15 }"/>
          <circle :cx="d.x" :cy="d.y" :r="d.r"
                  :fill="dotColor(d.status, d.ci)"
                  :stroke="dotColor(d.status, d.ci)"
                  :stroke-width="hoverId === d.id ? 2 : 0.8"
                  :opacity="hoverId !== null && hoverId !== d.id ? 0.25 : 1"
                  style="transition:all 0.2s"/>

          <g v-if="hoverId === d.id">
            <rect :x="d.x - 45" :y="d.y - d.r - 22" width="90" height="18" rx="4" fill="#0f172a" opacity="0.9"/>
            <text :x="d.x" :y="d.y - d.r - 9" text-anchor="middle" font-size="9" fill="#fff">
              {{ d.title.length > 6 ? d.title.slice(0, 6) + '...' : d.title }} · {{ STATUS_LABEL[d.status] }}
            </text>
          </g>
        </g>
      </svg>
    </div>

    <div class="mkp-footer">
      <span class="mkf-item"><span class="mkf-dot" style="background:#10b981"/>已掌握 {{ counts.mastered }}</span>
      <span class="mkf-item"><span class="mkf-dot" style="background:#ef4444"/>薄弱 {{ counts.weak }}</span>
      <span class="mkf-item"><span class="mkf-dot" style="background:#e5e7eb"/>未学习 {{ counts.untouched }}</span>
    </div>
    <div class="mkp-sub">共 {{ total }} 个知识点</div>

  </div>
</template>

<style scoped>
.mkp { font-size:12px; }
.mkp-header { display:flex;align-items:center;gap:10px;margin-bottom:8px; }
.mkp-icon { width:36px;height:36px;border-radius:8px;background:#ecfdf5;display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.mkp-num { font-size:24px;font-weight:800;line-height:1;letter-spacing:-0.03em;color:var(--ep-text-primary); }
.mkp-unit { font-size:14px;font-weight:500;color:var(--ep-text-muted);margin-left:2px; }
.mkp-label { font-size:11px;color:var(--ep-text-secondary);margin-top:2px; }
.mkp-svg-wrap { border-radius:12px;background:linear-gradient(135deg,#f8fafc,#fff);border:1px solid #f1f5f9;overflow:hidden; }
.mkp-svg { width:100%;height:140px;display:block; }
.mkp-footer { display:flex;gap:12px;margin-top:6px;font-size:10px;color:var(--ep-text-muted); }
.mkf-item { display:flex;align-items:center;gap:3px; } .mkf-dot { width:6px;height:6px;border-radius:50%; }
.mkp-sub { font-size:10px;color:var(--ep-text-muted);margin-top:2px; }
</style>
