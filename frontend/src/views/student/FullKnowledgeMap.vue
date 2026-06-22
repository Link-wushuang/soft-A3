<template>
  <div class="page-container" style="max-width:1200px">
    <div class="page-header">
      <div>
        <h1 class="page-title">知识图谱</h1>
        <p class="page-subtitle">操作系统课程全部知识点聚类可视化</p>
      </div>
      <el-button @click="$router.back()" round>
        <el-icon style="margin-right:6px"><Back /></el-icon>返回
      </el-button>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <div class="map-stat"><span class="ms-num" style="color:#6366f1">{{ totalPoints }}</span><span class="ms-label">知识点</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#10b981">{{ masteredPoints }}</span><span class="ms-label">已掌握</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#f59e0b">{{ learningPoints }}</span><span class="ms-label">学习中</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#ef4444">{{ weakPoints }}</span><span class="ms-label">薄弱</span></div>
      <div class="map-stat"><span class="ms-num" style="color:#94a3b8">{{ clusters.length }}</span><span class="ms-label">主题聚类</span></div>
    </div>

    <!-- Full-size bubble map -->
    <div class="card">
      <div class="card-header">
        <div style="display:flex;align-items:center;gap:10px">
          <div style="width:30px;height:30px;border-radius:8px;background:#eef2ff;display:flex;align-items:center;justify-content:center">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="3" fill="#6366f1"/>
              <circle cx="6" cy="6" r="2" fill="#10b981"/>
              <circle cx="18" cy="7" r="2.5" fill="#f59e0b"/>
            </svg>
          </div>
          <span>知识聚类图谱</span>
        </div>
        <div class="legend-inline">
          <span class="li-item"><span class="li-dot" style="background:#10b981" />已掌握</span>
          <span class="li-item"><span class="li-dot" style="background:#f59e0b" />学习中</span>
          <span class="li-item"><span class="li-dot" style="background:#ef4444" />薄弱</span>
          <span class="li-item"><span class="li-dot" style="background:#e5e7eb" />未开始</span>
        </div>
      </div>
      <div class="card-body" style="padding:0">
        <div class="full-svg-wrap">
          <svg :viewBox="`0 0 ${FW} ${FH}`" class="full-svg">
            <defs>
              <radialGradient id="bg-glow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#6366f1" stop-opacity="0.04"/>
                <stop offset="100%" stop-color="transparent"/>
              </radialGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#bg-glow)"/>

            <!-- Center -->
            <circle :cx="FW/2" :cy="FH/2" r="38" fill="#6366f1" fill-opacity="0.05" stroke="#6366f1" stroke-opacity="0.2" stroke-dasharray="4 4"/>
            <text :x="FW/2" :y="FH/2 - 6" text-anchor="middle" font-size="14" fill="#6366f1" font-weight="700">操作系统</text>
            <text :x="FW/2" :y="FH/2 + 12" text-anchor="middle" font-size="10" fill="#94a3b8">学科中心</text>

            <!-- Connection lines -->
            <line v-for="n in fullNodes" :key="`l-${n.topic}`" :x1="FW/2" :y1="FH/2" :x2="n.x" :y2="n.y"
                  stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.5"/>

            <!-- Cluster bubbles -->
            <g v-for="n in fullNodes" :key="n.topic" class="bubble-group"
               @mouseenter="hoverTopic = n.topic" @mouseleave="hoverTopic = null">
              <!-- Glow -->
              <circle :cx="n.x" :cy="n.y" :r="n.r + 6"
                      :fill="colorOf(n)" opacity="0.08" style="filter:blur(4px)"/>
              <!-- Main bubble -->
              <circle :cx="n.x" :cy="n.y" :r="n.r"
                      :fill="colorOf(n)" :stroke="n.topicColor"
                      :stroke-width="hoverTopic === n.topic ? 2.5 : 1.5"
                      :opacity="hoverTopic && hoverTopic !== n.topic ? 0.3 : 1"
                      style="transition:all 0.25s"/>
              <!-- Topic name -->
              <text :x="n.x" :y="n.y + 3" text-anchor="middle" font-size="10" fill="#fff" font-weight="600"
                    style="pointer-events:none">{{ n.topic }}</text>
              <!-- Count badge -->
              <g v-if="n.total > 0">
                <circle :cx="n.x + n.r * 0.65" :cy="n.y - n.r * 0.65"
                        r="7" fill="white" :stroke="n.topicColor" stroke-width="1.5"/>
                <text :x="n.x + n.r * 0.65" :y="n.y - n.r * 0.65 + 3"
                      text-anchor="middle" font-size="9" :fill="n.topicColor" font-weight="700">{{ n.mastered }}</text>
              </g>

              <!-- Expanded detail on hover -->
              <g v-if="hoverTopic === n.topic">
                <rect :x="n.x - 70" :y="n.y - n.r - 50" width="140" height="44" rx="6" fill="#0f172a" opacity="0.92"/>
                <text :x="n.x" :y="n.y - n.r - 30" text-anchor="middle" font-size="11" fill="#fff" font-weight="600">
                  {{ n.topic }}
                </text>
                <text :x="n.x" :y="n.y - n.r - 16" text-anchor="middle" font-size="10" fill="#94a3b8">
                  {{ statusLabel(n) }} · {{ n.mastered }}/{{ n.total }} 掌握 · {{ n.learning }} 学习中 · {{ n.weak }} 薄弱
                </text>
              </g>
            </g>
          </svg>
        </div>
      </div>
    </div>

    <!-- Cluster detail cards -->
    <div class="cluster-cards" style="margin-top:24px">
      <div v-for="c in clusters" :key="c.topic" class="cluster-card card">
        <div class="cluster-card-header">
          <span class="cluster-topic-dot" :style="{background:TOPIC_HEX[c.topic]||'#6366f1'}" />
          <strong>{{ c.topic }}</strong>
          <span :class="['cluster-status', statusClass(c)]">{{ statusLabel(c) }}</span>
        </div>
        <div class="cluster-progress">
          <div class="cp-bar">
            <div class="cp-fill mastered" :style="{width: masteredPct(c)+'%'}" />
            <div class="cp-fill learning" :style="{width: learningPct(c)+'%',left:masteredPct(c)+'%'}" />
          </div>
          <div class="cp-numbers">
            <span class="cp-num green">已掌握 {{ c.mastered }}</span>
            <span class="cp-num amber">学习中 {{ c.learning }}</span>
            <span class="cp-num red">薄弱 {{ c.weak }}</span>
            <span class="cp-num gray">共 {{ c.total }} 个</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Back } from '@element-plus/icons-vue'

interface Cluster { topic:string; total:number; mastered:number; learning:number; weak:number }

// TODO: 接入真实知识聚类数据
const clusters: Cluster[] = [
  { topic:'进程', total:6, mastered:4, learning:2, weak:0 },
  { topic:'内存', total:5, mastered:1, learning:2, weak:2 },
  { topic:'文件', total:4, mastered:0, learning:1, weak:3 },
  { topic:'I/O', total:3, mastered:2, learning:1, weak:0 },
  { topic:'设备', total:2, mastered:0, learning:0, weak:2 },
  { topic:'虚拟化', total:2, mastered:0, learning:0, weak:2 },
]

const TOPIC_COLORS = ['#6366f1','#10b981','#f59e0b','#ec4899','#8b5cf6','#06b6d4']
const TOPIC_HEX: Record<string,string> = {}
clusters.forEach((c,i)=>{ TOPIC_HEX[c.topic] = TOPIC_COLORS[i%TOPIC_COLORS.length] })

const totalPoints = computed(() => clusters.reduce((s,c)=>s+c.total,0))
const masteredPoints = computed(() => clusters.reduce((s,c)=>s+c.mastered,0))
const learningPoints = computed(() => clusters.reduce((s,c)=>s+c.learning,0))
const weakPoints = computed(() => clusters.reduce((s,c)=>s+c.weak,0))

const FW = 720; const FH = 440
const hoverTopic = ref<string|null>(null)

const fullNodes = computed(() => {
  const cols = 3; const rows = 2
  const cw = FW / cols; const ch = FH / rows
  return clusters.map((c, i) => {
    const col = i % cols; const row = Math.floor(i / cols)
    return {
      ...c,
      x: col * cw + cw/2 + ((i%2?1:-1)*10),
      y: row * ch + ch/2 + ((i%3?1:-1)*12),
      r: 22 + Math.sqrt(c.total) * 7,
      topicColor: TOPIC_COLORS[i % TOPIC_COLORS.length],
    }
  })
})

function colorOf(c: Cluster): string {
  if (c.total===0||c.mastered===0) return '#e5e7eb'
  const r = c.mastered/c.total
  if (r>=0.8) return '#10b981'; if (r>=0.4) return '#f59e0b'; return '#ef4444'
}
function statusLabel(c: Cluster): string {
  if (c.total===0||c.mastered===0) return '未开始'
  const r = c.mastered/c.total
  if (r>=0.8) return '已掌握'; if (r>=0.4) return '学习中'; return '薄弱'
}
function statusClass(c: Cluster): string {
  if (c.total===0||c.mastered===0) return 'none'
  const r = c.mastered/c.total
  if (r>=0.8) return 'good'; if (r>=0.4) return 'mid'; return 'bad'
}
function masteredPct(c: Cluster) { return c.total?Math.round(c.mastered/c.total*100)+'%':'0%' }
function learningPct(c: Cluster) { return c.total?Math.round(c.learning/c.total*100)+'%':'0%' }
</script>

<style scoped>
.stats-row { display:flex;gap:24px;margin-bottom:24px; }
.map-stat { text-align:center; } .ms-num { font-size:28px;font-weight:800;display:block;line-height:1.1; } .ms-label { font-size:12px;color:var(--ep-text-muted);margin-top:4px;display:block; }

.legend-inline { display:flex;gap:12px;font-size:11px;color:var(--ep-text-muted); }
.li-item { display:flex;align-items:center;gap:4px; } .li-dot { width:6px;height:6px;border-radius:50%; }

.full-svg-wrap { background:linear-gradient(160deg,#fafbfc,#fff);border-radius:0 0 var(--ep-radius-lg) var(--ep-radius-lg);overflow:hidden; }
.full-svg { width:100%;height:auto;display:block;max-height:440px; }
.bubble-group { cursor:pointer; }

.cluster-cards { display:grid;grid-template-columns:repeat(3,1fr);gap:16px; }
.cluster-card { padding:18px 22px;overflow:hidden; }
.cluster-card-header { display:flex;align-items:center;gap:10px;margin-bottom:14px; }
.cluster-topic-dot { width:10px;height:10px;border-radius:50%;flex-shrink:0; }
.cluster-card-header strong { flex:1;font-size:14px; }
.cluster-status { font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px; }
.cluster-status.good { background:var(--ep-success-light);color:#059669; }
.cluster-status.mid { background:var(--ep-warning-light);color:#d97706; }
.cluster-status.bad { background:var(--ep-danger-light);color:#dc2626; }
.cluster-status.none { background:var(--ep-bg-soft);color:var(--ep-text-muted); }

.cluster-progress { }
.cp-bar { height:8px;border-radius:4px;background:#e5e7eb;position:relative;overflow:hidden;margin-bottom:10px; }
.cp-fill { height:100%;position:absolute;top:0;left:0; }
.cp-fill.mastered { background:#10b981;z-index:3;border-radius:4px 0 0 4px; }
.cp-fill.learning { background:#f59e0b;z-index:2; }
.cp-fill:last-child { border-radius:0 4px 4px 0; }
.cp-numbers { display:flex;gap:14px;font-size:11px;flex-wrap:wrap; }
.cp-num.green { color:#059669; } .cp-num.amber { color:#d97706; } .cp-num.red { color:#dc2626; } .cp-num.gray { color:var(--ep-text-muted); }

@media (max-width:768px) { .cluster-cards { grid-template-columns:1fr 1fr; } .stats-row { gap:12px;flex-wrap:wrap; } }
@media (max-width:480px) { .cluster-cards { grid-template-columns:1fr; } }
</style>
