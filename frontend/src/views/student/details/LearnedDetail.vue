<template>
  <div class="detail-root">
    <div class="ld-head">
      <h2 class="detail-heading">学习记录</h2>
      <div class="ld-filters">
        <button v-for="f in filters" :key="f.key" :class="['ld-fbtn',{on:activeFilter===f.key}]" @click="activeFilter=f.key">{{ f.label }}</button>
      </div>
    </div>

    <!-- Timeline -->
    <div class="ld-timeline">
      <div v-for="(item,i) in filteredLogs" :key="i" class="ld-item">
        <div class="ld-dot" :class="item.type" />
        <div v-if="i<filteredLogs.length-1" class="ld-line" />
        <div class="ld-card">
          <div class="ld-card-top">
            <span class="ld-type-badge" :class="item.type">{{ typeLabel(item.type) }}</span>
            <span class="ld-date">{{ item.date }}</span>
          </div>
          <div class="ld-title">{{ item.title }}</div>
          <div class="ld-desc">{{ item.desc }}</div>
          <button v-if="item.action" class="ld-action" @click="$emit('navigate',item.action)">{{ item.actionLabel }}</button>
        </div>
      </div>
      <div v-if="!filteredLogs.length" class="ld-empty">
        <el-empty description="暂无学习记录" :image-size="80" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

defineEmits<{ navigate: [path:string] }>()

const filters = [
  { key:'all', label:'全部' },
  { key:'learned', label:'已掌握' },
  { key:'exercise', label:'练习' },
]

const activeFilter = ref('all')

// TODO: 接入真实学习记录
const timeline = [
  { type:'mastered' as const, title:'系统调用', desc:'连续答对 3 题，自动标记为已掌握', date:'6/21 16:30', action:'/student/resources/3', actionLabel:'查看详情' },
  { type:'exercise' as const, title:'中断与异常 — 选择题', desc:'完成练习，正确率 75%', date:'6/21 15:10' },
  { type:'learned' as const, title:'操作系统结构', desc:'完成阅读 + 思维导图学习', date:'6/20 20:45' },
  { type:'exercise' as const, title:'进程概念与 PCB — 简答题', desc:'答错 1 题，标记薄弱：进程状态转换', date:'6/20 18:20', action:'/student/tutor', actionLabel:'去答疑' },
  { type:'learned' as const, title:'内核态与用户态', desc:'观看视频分镜 + 实操案例', date:'6/20 14:00' },
  { type:'mastered' as const, title:'操作系统目标与功能', desc:'完成阅读后自动标记', date:'6/19 10:00' },
]

function typeLabel(t:string) { const m:Record<string,string>={mastered:'已掌握',learned:'学习中',exercise:'练习'}; return m[t]||t }
const filteredLogs = computed(() => activeFilter.value==='all' ? timeline : timeline.filter(i=>i.type===activeFilter.value))
</script>

<style scoped>
.detail-root { } .detail-heading { font-size:17px;font-weight:700;margin:0;color:var(--ep-text-primary); }
.ld-head { display:flex;justify-content:space-between;align-items:center;margin-bottom:20px; }
.ld-filters { display:flex;gap:4px;padding:2px;background:#f1f5f9;border-radius:8px; }
.ld-fbtn { padding:5px 14px;border:none;background:none;border-radius:6px;font-size:12px;color:var(--ep-text-muted);cursor:pointer; } .ld-fbtn.on { background:white;color:var(--ep-text-primary);box-shadow:0 1px 2px rgba(0,0,0,0.05);font-weight:500; }

.ld-timeline { margin-left:12px; }
.ld-item { display:flex;gap:16px;position:relative;padding-bottom:6px; }
.ld-dot { width:12px;height:12px;border-radius:50%;flex-shrink:0;margin-top:14px;border:2px solid;z-index:1;position:relative;background:white; } .ld-dot.mastered { border-color:#10b981; } .ld-dot.exercise { border-color:#f59e0b; } .ld-dot.learned { border-color:#6366f1; }
.ld-line { position:absolute;left:6px;top:28px;bottom:4px;width:0;border-left:2px dashed #e2e8f0; }
.ld-card { flex:1;padding:12px 16px;background:#f8fafc;border-radius:10px;margin-bottom:12px;transition:all var(--ep-transition); } .ld-card:hover { background:#f1f5f9; }
.ld-card-top { display:flex;justify-content:space-between;align-items:center;margin-bottom:4px; }
.ld-type-badge { font-size:10px;font-weight:600;padding:1px 6px;border-radius:4px; } .ld-type-badge.mastered { background:var(--ep-success-light);color:#059669; } .ld-type-badge.exercise { background:var(--ep-warning-light);color:#d97706; } .ld-type-badge.learned { background:var(--ep-primary-light);color:var(--ep-primary); }
.ld-date { font-size:10px;color:var(--ep-text-muted); }
.ld-title { font-size:13px;font-weight:600;color:var(--ep-text-primary);margin-bottom:2px; }
.ld-desc { font-size:12px;color:var(--ep-text-secondary);line-height:1.5; }
.ld-action { margin-top:6px;padding:0;background:none;border:none;font-size:11px;color:var(--ep-primary);cursor:pointer; } .ld-action:hover { text-decoration:underline; }
.ld-empty { padding:40px 0; }
</style>
