<template>
  <div class="detail-root">
    <div class="td-head">
      <h2 class="detail-heading">今日推荐学习</h2>
      <span class="td-badge">{{ recommendations.length }} 项</span>
    </div>

    <div v-if="!recommendations.length" class="td-empty">
      <el-empty description="暂无推荐" :image-size="80" />
    </div>

    <div v-else class="td-list">
      <div v-for="(rec, i) in recommendations" :key="rec.knowledge_point_id" class="td-item"
           @click="$emit('goResource', rec.knowledge_point_id)">
        <div class="td-rank" :style="{background:rankColors[i]}">{{ i+1 }}</div>
        <div class="td-info">
          <div class="td-row1"><span class="td-title">{{ rec.title }}</span><span class="td-est">约 {{ rec.est_minutes||15 }} 分钟</span></div>
          <div class="td-progress" v-if="rec.progress !== undefined">
            <div class="td-progress-track"><div :class="['td-progress-fill',{done:rec.progress>=100}]" :style="{width:rec.progress+'%'}" /></div>
            <span :class="['td-progress-text',{done:rec.progress>=100}]">
              <template v-if="rec.progress>=100">已完成 <el-icon :size="12"><Check /></el-icon></template>
              <template v-else>{{ rec.progress }}%</template>
            </span>
          </div>
          <div class="td-meta">
            <span :class="['dd-chip',rec.difficulty]">{{ diffLabel(rec.difficulty) }}</span>
            <span v-for="r in rec.reasons" :key="r" class="dd-tag">{{ r }}</span>
            <span class="dd-chapter">{{ rec.chapter }}</span>
          </div>
        </div>
        <el-button type="primary" size="small" round @click.stop="$emit('goResource', rec.knowledge_point_id)">开始学习</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'

defineProps<{
  recommendations: any[]
  rankColors: string[]
}>()

defineEmits<{ goResource: [id:number] }>()

function diffLabel(d:string) { if(d==='easy') return '简单'; if(d==='hard') return '困难'; return '中等' }
</script>

<style scoped>
.detail-root { } .detail-heading { font-size:17px;font-weight:700;margin:0;color:var(--ep-text-primary); }
.td-head { display:flex;justify-content:space-between;align-items:center;margin-bottom:16px; }
.td-badge { font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px;background:var(--ep-bg-soft);color:var(--ep-text-muted); }
.td-empty { padding:40px; }

.td-list { }
.td-item { display:flex;align-items:center;gap:14px;padding:14px 18px;border-radius:12px;cursor:pointer;transition:all var(--ep-transition);margin-bottom:6px; } .td-item:hover { background:#fafbfc; }
.td-rank { width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;flex-shrink:0; }
.td-info { flex:1;min-width:0; }
.td-row1 { display:flex;align-items:baseline;gap:12px;margin-bottom:4px; } .td-title { font-size:15px;font-weight:600;color:var(--ep-text-primary); }
.td-est { font-size:11px;color:var(--ep-text-muted);flex-shrink:0; }
.td-progress { display:flex;align-items:center;gap:8px;margin-bottom:6px; }
.td-progress-track { flex:1;height:4px;border-radius:2px;background:#e5e7eb;overflow:hidden;min-width:0; } .td-progress-fill { height:100%;border-radius:2px;background:#6366f1;transition:width 0.5s; } .td-progress-fill.done { background:#10b981; }
.td-progress-text { font-size:11px;font-weight:500;color:var(--ep-text-muted);white-space:nowrap;display:flex;align-items:center;gap:3px; } .td-progress-text.done { color:#059669; }
.td-meta { display:flex;align-items:center;gap:8px;flex-wrap:wrap; }
.dd-chip { display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.03em; } .dd-chip.easy { background:var(--ep-success-light);color:#059669; } .dd-chip.medium { background:var(--ep-warning-light);color:#d97706; } .dd-chip.hard { background:var(--ep-danger-light);color:#dc2626; }
.dd-tag { display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:500;background:#f1f5f9;color:var(--ep-text-muted); }
.dd-chapter { font-size:11px;color:var(--ep-text-muted); }
</style>
