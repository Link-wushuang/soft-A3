<template>
  <div class="detail-root">
    <h2 class="detail-heading">知识图谱详情</h2>

    <div class="mastery-grid">
      <div class="mastery-bubbles">
        <div class="mb-title">📈 掌握率趋势</div>
        <div ref="trendRef" class="mb-chart" />
      </div>
      <div class="mastery-weak">
        <div class="mw-title">⚠️ 薄弱点 Top 5</div>
        <div v-if="weakList.length" class="mw-list">
          <div v-for="(w,i) in weakList" :key="w.name" class="mw-item">
            <span class="mw-rank" :class="'r'+i">{{ i+1 }}</span>
            <div class="mw-info">
              <div class="mw-name">{{ w.name }}</div>
              <div class="mw-bar"><div class="mw-bar-fill" :style="{width:w.rate+'%',background:w.color}" /></div>
            </div>
            <span class="mw-pct">{{ w.rate }}%</span>
            <el-button size="small" type="primary" link @click="$emit('goTutor',w.name)">去学习</el-button>
          </div>
        </div>
        <el-empty v-else description="暂无薄弱点" :image-size="60" />
      </div>
    </div>

    <div class="mastery-stats">
      <div class="ms-card green"><span class="ms-num">{{ stats.mastered }}</span><span class="ms-label">已掌握</span></div>
      <div class="ms-card amber"><span class="ms-num">{{ stats.learning }}</span><span class="ms-label">学习中</span></div>
      <div class="ms-card red"><span class="ms-num">{{ stats.weak }}</span><span class="ms-label">薄弱</span></div>
      <div class="ms-card gray"><span class="ms-num">{{ stats.untouched }}</span><span class="ms-label">未学习</span></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

defineEmits<{ goTutor: [name:string] }>()

const trendRef = ref<HTMLElement>()
let chart: echarts.ECharts|null = null

// TODO: 接入真实数据
const weakList = [
  { name:'文件系统链接分配', rate:35, color:'#ef4444' },
  { name:'内存分页分段', rate:42, color:'#f97316' },
  { name:'进程间通信', rate:48, color:'#f59e0b' },
  { name:'中断与异常', rate:55, color:'#f59e0b' },
  { name:'虚拟内存管理', rate:60, color:'#f59e0b' },
]
const stats = { mastered:7, learning:5, weak:6, untouched:22 }

function renderChart() {
  if (!trendRef.value) return
  chart = echarts.init(trendRef.value)
  chart.setOption({
    tooltip:{trigger:'axis',backgroundColor:'rgba(255,255,255,0.96)',borderColor:'#e2e8f0',textStyle:{color:'#0f172a',fontSize:12}},
    xAxis:{type:'category',data:['6/15','6/16','6/17','6/18','6/19','6/20','6/21'],axisLabel:{fontSize:10,color:'#94a3b8'},axisLine:{lineStyle:{color:'#e2e8f0'}}},
    yAxis:{type:'value',min:0,max:100,axisLabel:{formatter:'{value}%',fontSize:10,color:'#94a3b8'},splitLine:{lineStyle:{color:'#f1f5f9',type:'dashed'}}},
    series:[{type:'line',smooth:true,data:[0,5,12,15,22,28,35],areaStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(99,102,241,0.15)'},{offset:1,color:'rgba(99,102,241,0)'}])},itemStyle:{color:'#6366f1'},lineStyle:{width:2.5},symbolSize:5}],
    grid:{left:45,right:20,bottom:30,top:20},
  })
}

onMounted(()=>{ renderChart(); window.addEventListener('resize',()=>chart?.resize()) })
onUnmounted(()=>{ chart?.dispose() })
</script>

<style scoped>
.detail-root { }
.detail-heading { font-size:17px;font-weight:700;margin:0 0 20px;color:var(--ep-text-primary); }
.mastery-grid { display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px; }
.mastery-bubbles { background:#f8fafc;border-radius:12px;padding:16px; } .mb-title { font-size:13px;font-weight:600;color:var(--ep-text-primary);margin-bottom:12px; } .mb-chart { height:200px; }
.mastery-weak { background:#f8fafc;border-radius:12px;padding:16px; } .mw-title { font-size:13px;font-weight:600;color:var(--ep-text-primary);margin-bottom:12px; }
.mw-list { display:flex;flex-direction:column;gap:10px; } .mw-item { display:flex;align-items:center;gap:10px; }
.mw-rank { width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:white;flex-shrink:0; }
.mw-rank.r0 { background:#ef4444; } .mw-rank.r1 { background:#f97316; } .mw-rank.r2 { background:#f59e0b; } .mw-rank.r3 { background:#f59e0b; } .mw-rank.r4 { background:#f59e0b; }
.mw-info { flex:1;min-width:0; } .mw-name { font-size:12px;color:var(--ep-text-primary);font-weight:500;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis; }
.mw-bar { height:4px;border-radius:2px;background:#e5e7eb;overflow:hidden; } .mw-bar-fill { height:100%;border-radius:2px;transition:width 0.6s; }
.mw-pct { font-size:11px;color:var(--ep-text-muted);width:32px;text-align:right;flex-shrink:0; }

.mastery-stats { display:grid;grid-template-columns:repeat(4,1fr);gap:12px; }
.ms-card { text-align:center;padding:16px;border-radius:12px; } .ms-card.green { background:var(--ep-success-light); } .ms-card.amber { background:var(--ep-warning-light); } .ms-card.red { background:var(--ep-danger-light); } .ms-card.gray { background:#f1f5f9; }
.ms-num { display:block;font-size:24px;font-weight:700;line-height:1; } .ms-card.green .ms-num{color:#059669;} .ms-card.amber .ms-num{color:#d97706;} .ms-card.red .ms-num{color:#dc2626;} .ms-card.gray .ms-num{color:#64748b;}
.ms-label { display:block;font-size:11px;color:var(--ep-text-muted);margin-top:4px; }

@media (max-width:768px) { .mastery-grid { grid-template-columns:1fr; } .mastery-stats { grid-template-columns:repeat(2,1fr); } }
</style>
