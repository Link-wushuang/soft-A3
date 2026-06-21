<template>
  <div class="path-list">
    <div v-for="(node,i) in nodes" :key="node.id" class="path-node" @click="$emit('nodeClick',node)">
      <div class="node-indicator"><div :class="['node-dot',node.status]"><el-icon v-if="node.status==='completed'" :size="12"><Check /></el-icon><span v-else-if="node.status==='in_progress'" class="dot-inner pulse" /><span v-else class="dot-inner" /></div><div v-if="i<nodes.length-1" :class="['node-line',{completed:node.status==='completed'}]" /></div>
      <div :class="['node-card card',{active:node.status==='in_progress'}]"><div class="node-header"><span class="node-order">{{ i+1 }}</span><strong class="node-title">{{ node.knowledge_point_title||node.title }}</strong><span :class="['node-status',node.status]">{{ statusLabel(node.status) }}</span></div><p v-if="node.reason" class="node-reason">{{ node.reason }}</p></div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'; defineProps<{nodes:Array<{id:number;knowledge_point_title?:string;title?:string;status:string;reason:string}>}>(); defineEmits<{nodeClick:[node:any]}>()
function statusLabel(s:string) { if(s==='completed') return '已完成'; if(s==='in_progress') return '进行中'; return '待学习' }
</script>
<style scoped>
.path-list { display:flex;flex-direction:column; } .path-node { display:flex;gap:18px;cursor:pointer; }
.node-indicator { display:flex;flex-direction:column;align-items:center;width:26px;flex-shrink:0;padding-top:14px; }
.node-dot { width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;z-index:1;transition:all var(--ep-transition-smooth); }
.node-dot.completed { background:var(--ep-success);color:white;box-shadow:0 2px 8px rgba(16,185,129,0.3); }
.node-dot.in_progress { background:var(--ep-primary);box-shadow:0 0 0 4px rgba(99,102,241,0.15); }
.node-dot.pending { background:white;border:2px solid var(--ep-border); }
.dot-inner { width:8px;height:8px;border-radius:50%;background:white; } .dot-inner.pulse { animation:pulse 2s infinite; }
.node-line { width:2px;flex:1;min-height:8px;background:var(--ep-border-light);border-radius:1px;transition:background var(--ep-transition); } .node-line.completed { background:var(--ep-success); }
.node-card { flex:1;padding:16px 22px;margin-bottom:8px;transition:all var(--ep-transition-smooth); } .node-card:hover { transform:translateX(6px);box-shadow:var(--ep-shadow-md)!important; } .node-card.active { border-color:var(--ep-primary-lighter)!important;background:#fafaff;box-shadow:var(--ep-shadow-glow)!important; }
.node-header { display:flex;align-items:center;gap:10px; } .node-order { width:26px;height:26px;border-radius:8px;background:var(--ep-bg-soft);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:var(--ep-text-secondary);flex-shrink:0; } .node-card.active .node-order { background:var(--ep-primary-light);color:var(--ep-primary); }
.node-title { flex:1;font-size:14px;font-weight:600; }
.node-status { font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;flex-shrink:0; } .node-status.completed { background:var(--ep-success-light);color:#059669; } .node-status.in_progress { background:var(--ep-primary-light);color:var(--ep-primary); } .node-status.pending { background:var(--ep-bg-soft);color:var(--ep-text-muted); }
.node-reason { margin:10px 0 0;font-size:13px;color:var(--ep-text-secondary);padding-left:36px;line-height:1.6; }
@keyframes pulse { 0%,100%{ opacity:1;transform:scale(1); } 50%{ opacity:0.4;transform:scale(0.7); } }
</style>
