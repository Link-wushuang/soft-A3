<template>
  <div class="page-container" style="max-width:1200px">
    <div class="page-header">
      <div>
        <h1 class="page-title">学习进度</h1>
        <p class="page-subtitle">操作系统全部知识点学习状态总览</p>
      </div>
      <el-button @click="$router.back()" round><el-icon style="margin-right:6px"><Back /></el-icon>返回</el-button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="map-stat"><span class="ms-num" style="color:#0f172a">{{ totalKp }}</span><span class="ms-label">知识点总数</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#10b981">{{ mastered.length }}</span><span class="ms-label">已掌握</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#ef4444">{{ weak.length }}</span><span class="ms-label">薄弱</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#94a3b8">{{ untouched.length }}</span><span class="ms-label">未学习</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#6366f1">{{ Math.round(mastered.length/Math.max(totalKp,1)*100) }}%</span><span class="ms-label">掌握率</span></div>
    </div>

    <!-- Full-size bubble scatter -->
    <div class="card">
      <div class="card-header">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:30px;height:30px;border-radius:8px;background:#ecfdf5;display:flex;align-items:center;justify-content:center">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="5" cy="5" r="3" fill="#10b981"/><circle cx="12" cy="6" r="2.5" fill="#f59e0b"/><circle cx="9" cy="11" r="3.5" fill="#ef4444"/>
            </svg>
          </div>
          <span>知识点分布图</span>
        </div>
        <div class="legend-inline">
          <span class="li-item"><span class="li-dot" style="background:#10b981"/>已掌握 {{ mastered.length }}</span>
          <span class="li-item"><span class="li-dot" style="background:#ef4444"/>薄弱 {{ weak.length }}</span>
          <span class="li-item"><span class="li-dot" style="background:#e5e7eb"/>未学习 {{ untouched.length }}</span>
        </div>
      </div>
      <div class="card-body" style="padding:0">
        <div class="full-svg-wrap">
          <svg :viewBox="`0 0 ${FW} ${FH}`" class="full-svg">
            <defs>
              <radialGradient id="pg-glow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#10b981" stop-opacity="0.03"/><stop offset="100%" stop-color="transparent"/>
              </radialGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#pg-glow)"/>

            <!-- Multiple orbit ellipses -->
            <ellipse :cx="FW/2" :cy="FH/2" :rx="FW*0.42" :ry="FH*0.4" fill="none" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="3 5"/>
            <ellipse :cx="FW/2" :cy="FH/2" :rx="FW*0.32" :ry="FH*0.30" fill="none" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="2 5"/>
            <ellipse :cx="FW/2" :cy="FH/2" :rx="FW*0.20" :ry="FH*0.18" fill="none" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="2 4"/>

            <!-- Center -->
            <circle :cx="FW/2" :cy="FH/2" r="26" fill="white" stroke="#d1d5db" stroke-width="1.2"/>
            <text :x="FW/2" :y="FH/2 - 4" text-anchor="middle" font-size="16" fill="#0f172a" font-weight="700">{{ totalKp }}</text>
            <text :x="FW/2" :y="FH/2 + 12" text-anchor="middle" font-size="9" fill="#94a3b8">知识点</text>

            <!-- Dots -->
            <g v-for="(d, i) in scatterDots" :key="i"
               @mouseenter="hoverIdx = i" @mouseleave="hoverIdx = null" style="cursor:pointer">
              <circle :cx="d.x" :cy="d.y" :r="d.r + 4"
                      :fill="dotColor(d.status, d.ci||0)" :opacity="hoverIdx===i ? 0.2 : 0.08" style="filter:blur(3px)"/>
              <circle :cx="d.x" :cy="d.y" :r="d.r"
                      :fill="dotColor(d.status, d.ci||0)"
                      :stroke="dotColor(d.status, d.ci||0)"
                      :stroke-width="hoverIdx===i ? 2 : 0.8"
                      :opacity="hoverIdx!==null && hoverIdx!==i ? 0.2 : 1"
                      style="transition:all 0.2s"/>
              <g v-if="hoverIdx === i">
                <rect :x="d.x - 52" :y="d.y - d.r - 24" width="104" height="20" rx="4" fill="#0f172a" opacity="0.9"/>
                <text :x="d.x" :y="d.y - d.r - 10" text-anchor="middle" font-size="10" fill="#fff">
                  {{ d.title.length>8 ? d.title.slice(0,8)+'...' : d.title }} · {{ STATUS_LABEL[d.status] }}
                </text>
              </g>
            </g>
          </svg>
        </div>
      </div>
    </div>

    <!-- Mastered / Weak lists -->
    <div class="two-col" style="margin-top:24px">
      <div class="card">
        <div class="card-header" style="font-size:14px;display:flex;align-items:center;gap:8px">
          <span style="width:8px;height:8px;border-radius:50%;background:#10b981" />已掌握知识点
        </div>
        <div class="card-body" style="padding:12px">
          <div class="tag-list">
            <span v-for="t in mastered" :key="t" class="tag good">{{ t }}</span>
          </div>
          <el-empty v-if="!mastered.length" description="暂无已掌握知识点" :image-size="60" />
        </div>
      </div>
      <div class="card">
        <div class="card-header" style="font-size:14px;display:flex;align-items:center;gap:8px">
          <span style="width:8px;height:8px;border-radius:50%;background:#ef4444" />薄弱知识点
        </div>
        <div class="card-body" style="padding:12px">
          <div class="tag-list">
            <span v-for="t in weak" :key="t" class="tag bad">{{ t }}</span>
          </div>
          <el-empty v-if="!weak.length" description="暂无薄弱知识点" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Back } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/index'

interface KpItem { title: string; status: 'mastered'|'weak'|'untouched'; x: number; y: number; r: number; ci?: number }

const auth = useAuthStore()
const totalKp = ref(40)
const mastered = ref<string[]>([])
const weak = ref<string[]>([])
const allKpTitles = ref<string[]>([])
const untouched = ref<string[]>([])

const MASTERED_HUES = ['#10b981','#059669','#14b8a6','#0d9488','#22c55e','#34d399','#06b6d4']
const WEAK_HUES = ['#ef4444','#f97316','#e11d48','#dc2626','#ea580c','#fb923c','#f43f5e']
const UNTOUCHED_HUES = ['#cbd5e1','#94a3b8','#b0bec5','#9ca3af','#bdbdbd']
function dotColor(status:string, idx:number):string {
  if (status==='mastered') return MASTERED_HUES[idx%MASTERED_HUES.length]
  if (status==='weak') return WEAK_HUES[idx%WEAK_HUES.length]
  return UNTOUCHED_HUES[idx%UNTOUCHED_HUES.length]
}
const STATUS_LABEL: Record<string,string> = { mastered:'已掌握', weak:'薄弱', untouched:'未学习' }

const FW = 720; const FH = 400
const hoverIdx = ref<number|null>(null)

const scatterDots = computed(() => {
  const all: KpItem[] = []
  let mi=0; let wi=0; let ui=0
  mastered.value.forEach(t => all.push({ title:t, status:'mastered', x:0, y:0, r:0 }))
  weak.value.forEach(t => all.push({ title:t, status:'weak', x:0, y:0, r:0 }))
  untouched.value.forEach(t => all.push({ title:t, status:'untouched', x:0, y:0, r:0 }))
  const seed = 42
  return all.map((item, i) => {
    const angle = (i / all.length) * Math.PI * 2 - Math.PI / 2
    const orbit = 40 + (i % 4) * 42 + Math.floor(i / 12) * 36
    const cx = FW/2 + Math.cos(angle + (i * 0.3)) * (orbit * 0.95)
    const cy = FH/2 + Math.sin(angle + (i * 0.3)) * (orbit * 0.70)
    const base = item.status === 'untouched' ? 5 : item.status === 'weak' ? 8 : 10
    let ci: number
    if (item.status==='mastered') { ci=mi; mi++ }
    else if (item.status==='weak') { ci=wi; wi++ }
    else { ci=ui; ui++ }
    return { ...item, x: cx, y: cy, r: base + (i % 5) * 1.2, ci }
  })
})

// TODO: 接入真实学习进度数据
async function loadData() {
  try {
    const userId = auth.user?.id
    if (userId) {
      const r = await api.get(`/profile/${userId}`)
      mastered.value = r.data.mastered_points || []
      weak.value = r.data.weak_points || []
    }
    const kr = await api.get('/courses/1/knowledge-points')
    allKpTitles.value = (kr.data||[]).map((k:any)=>k.title)
    const done = new Set([...mastered.value, ...weak.value])
    untouched.value = allKpTitles.value.filter(t => !done.has(t))
    totalKp.value = allKpTitles.value.length
  } catch { /* use defaults */ }
}
loadData()
</script>

<style scoped>
.stats-row { display:flex;gap:28px;margin-bottom:24px; }
.map-stat { text-align:center; } .ms-num { font-size:28px;font-weight:800;display:block;line-height:1.1; } .ms-label { font-size:12px;color:var(--ep-text-muted);margin-top:4px;display:block; }

.legend-inline { display:flex;gap:14px;font-size:11px;color:var(--ep-text-muted); }
.li-item { display:flex;align-items:center;gap:4px; } .li-dot { width:6px;height:6px;border-radius:50%; }

.full-svg-wrap { background:linear-gradient(160deg,#fafbfc,#fff);border-radius:0 0 var(--ep-radius-lg) var(--ep-radius-lg);overflow:hidden; }
.full-svg { width:100%;height:auto;display:block;max-height:400px; }

.two-col { display:grid;grid-template-columns:1fr 1fr;gap:20px; }
.tag-list { display:flex;flex-wrap:wrap;gap:6px; }
.tag { padding:4px 12px;border-radius:6px;font-size:12px;font-weight:500; }
.tag.good { background:var(--ep-success-light);color:#059669; }
.tag.bad { background:var(--ep-danger-light);color:#dc2626; }

@media (max-width:768px) { .two-col { grid-template-columns:1fr; } .stats-row { gap:12px;flex-wrap:wrap; } }
</style>
