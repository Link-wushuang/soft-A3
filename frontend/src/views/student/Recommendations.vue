<template>
  <div class="page-container" style="max-width:1200px">
    <div class="page-header">
      <div><h1 class="page-title">全部推荐</h1><p class="page-subtitle">基于你的学习画像智能匹配的推荐内容</p></div>
      <el-button @click="$router.back()" round><el-icon style="margin-right:6px"><Back /></el-icon>返回</el-button>
    </div>

    <el-skeleton v-if="loading" :rows="8" animated />

    <div v-else-if="error" class="card" style="border-color:#fecaca">
      <div class="card-body" style="text-align:center;padding:48px">
        <p style="color:var(--ep-text-secondary);margin:0 0 16px">{{ error }}</p>
        <el-button type="primary" @click="load">重新加载</el-button>
      </div>
    </div>

    <div v-else class="card">
      <div class="card-header">
        <div style="display:flex;align-items:center;gap:8px">
          <span style="font-size:15px">📋</span> 共 {{ list.length }} 项推荐
        </div>
      </div>
      <div class="card-body" style="padding:0">
        <div v-if="!list.length" style="text-align:center;padding:60px;color:var(--ep-text-muted)">
          <p>暂无推荐，请先完成对话建档</p>
        </div>
        <div v-for="(rec, i) in list" :key="rec.knowledge_point_id" class="rec-item"
             @click="$router.push(`/student/resources/${rec.knowledge_point_id}`)">
          <div class="rec-rank" :style="{background:rankColors[i%rankColors.length]}">{{ i+1 }}</div>
          <div class="rec-info">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-sub">{{ rec.chapter }}</div>
            <div class="rec-meta">
              <span :class="['rc-chip', rec.difficulty]">{{ diffLabel(rec.difficulty) }}</span>
              <span v-for="r in rec.reasons" :key="r" class="rc-tag">{{ r }}</span>
            </div>
          </div>
          <el-button type="primary" size="small" round @click.stop="$router.push(`/student/resources/${rec.knowledge_point_id}`)">
            开始学习
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Back } from '@element-plus/icons-vue'
import api from '../../api/index'

const list = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const rankColors = ['#4f46e5','#6366f1','#7c3aed','#8b5cf6','#a78bfa','#818cf8','#a855f7','#c084fc']

function diffLabel(d:string) { if(d==='easy') return '简单'; if(d==='hard') return '困难'; return '中等' }

async function load() {
  loading.value = true; error.value = ''
  try {
    const r = await api.get('/analytics/recommendations', { params: { course_id: 1 } })
    list.value = r.data.recommended || []
  } catch { error.value = '推荐数据加载失败' }
  loading.value = false
}

onMounted(load)
</script>

<style scoped>
.rec-item { display:flex;align-items:center;gap:14px;padding:16px 24px;border-bottom:1px solid var(--ep-border-light);cursor:pointer;transition:all var(--ep-transition); }
.rec-item:last-child { border-bottom:none; } .rec-item:hover { background:#fafbfc; }
.rec-rank { width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;flex-shrink:0; }
.rec-info { flex:1;min-width:0; }
.rec-title { font-size:15px;font-weight:600;color:var(--ep-text-primary);margin-bottom:2px; }
.rec-sub { font-size:11px;color:var(--ep-text-muted);margin-bottom:6px; }
.rec-meta { display:flex;align-items:center;gap:6px;flex-wrap:wrap; }
.rc-chip { display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.03em; }
.rc-chip.easy { background:var(--ep-success-light);color:#059669; } .rc-chip.hard { background:var(--ep-danger-light);color:#dc2626; } .rc-chip.medium { background:var(--ep-warning-light);color:#d97706; }
.rc-tag { display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:500;background:#f1f5f9;color:var(--ep-text-muted); }
</style>
