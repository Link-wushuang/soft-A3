<template>
  <div class="detail-root">
    <div class="td-head">
      <h2 class="detail-heading">本周学习统计</h2>
      <el-button type="primary" size="small" @click="$emit('openPlan')">制定学习计划</el-button>
    </div>

    <!-- Week table -->
    <div class="td-table-wrap">
      <table class="td-table">
        <thead><tr><th>日期</th><th>学习时长</th><th>完成知识点</th><th>练习正确率</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="d in weekRows" :key="d.date" :class="{today:d.isToday}">
            <td class="td-date">{{ d.date }}</td>
            <td><span class="td-bold">{{ d.minutes }} min</span></td>
            <td>{{ d.topics }}</td>
            <td><span :class="d.accuracy>=70?'td-green':'td-red'">{{ d.accuracy }}%</span></td>
            <td><span :class="['td-status',d.status]">{{ d.statusLabel }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Summary + suggestion -->
    <div class="td-footer">
      <div class="td-summary">
        <div class="tds-item">📊 本周总计 <strong>{{ totalMin }} min</strong></div>
        <div class="tds-item">🎯 日均 <strong>{{ avgMin }} min</strong></div>
        <div class="tds-item">✅ 完成 <strong>{{ totalTopics }}</strong> 个知识点</div>
      </div>
      <div class="td-sugg">⚡ {{ suggestion }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

defineEmits<{ openPlan: [] }>()

// TODO: 接入真实周数据
const weekRows = [
  { date:'周一 6/16', minutes:30, topics:2, accuracy:80, status:'good' as const, statusLabel:'达标', isToday:false },
  { date:'周二 6/17', minutes:50, topics:3, accuracy:75, status:'good' as const, statusLabel:'达标', isToday:false },
  { date:'周三 6/18', minutes:40, topics:2, accuracy:60, status:'warn' as const, statusLabel:'未达标', isToday:false },
  { date:'周四 6/19', minutes:75, topics:4, accuracy:85, status:'good' as const, statusLabel:'达标', isToday:false },
  { date:'周五 6/20', minutes:60, topics:3, accuracy:70, status:'good' as const, statusLabel:'达标', isToday:false },
  { date:'周六 6/21', minutes:95, topics:5, accuracy:90, status:'great' as const, statusLabel:'超额', isToday:false },
  { date:'周日 6/22', minutes:45, topics:2, accuracy:100, status:'good' as const, statusLabel:'进行中', isToday:true },
]
const totalMin = computed(() => weekRows.reduce((s,d)=>s+d.minutes,0))
const avgMin = computed(() => Math.round(totalMin.value/7))
const totalTopics = computed(() => weekRows.reduce((s,d)=>s+d.topics,0))

const suggestion = '本周前 3 天学习时长偏低，建议周末集中攻克薄弱点，重点复习「文件系统」和「内存管理」相关知识点。'
</script>

<style scoped>
.detail-root { } .detail-heading { font-size:17px;font-weight:700;margin:0;color:var(--ep-text-primary); }
.td-head { display:flex;justify-content:space-between;align-items:center;margin-bottom:20px; }

.td-table-wrap { overflow-x:auto;margin-bottom:16px;border-radius:10px;border:1px solid var(--ep-border-light); }
.td-table { width:100%;border-collapse:collapse;font-size:13px; } .td-table th { background:#f8fafc;font-size:11px;font-weight:600;color:var(--ep-text-muted);text-transform:uppercase;letter-spacing:0.04em;padding:10px 16px;text-align:left;border-bottom:1px solid var(--ep-border-light); }
.td-table td { padding:12px 16px;border-bottom:1px solid var(--ep-border-light);color:var(--ep-text-secondary); } .td-table tr:last-child td { border-bottom:none; } .td-table tr.today { background:#fafaff; } .td-table tr.today td { color:var(--ep-text-primary);font-weight:500; }
.td-date { font-weight:500;color:var(--ep-text-primary)!important; } .td-bold { font-weight:600;color:var(--ep-text-primary); } .td-green { color:#059669;font-weight:600; } .td-red { color:#dc2626;font-weight:600; }
.td-status { font-size:11px;font-weight:600;padding:2px 8px;border-radius:10px; } .td-status.good { background:var(--ep-success-light);color:#059669; } .td-status.warn { background:var(--ep-warning-light);color:#d97706; } .td-status.great { background:var(--ep-primary-light);color:var(--ep-primary); }

.td-footer { display:flex;justify-content:space-between;align-items:flex-start;gap:16px;padding-top:8px; }
.td-summary { display:flex;gap:20px;font-size:12px;color:var(--ep-text-secondary);flex-wrap:wrap; } .tds-item strong { color:var(--ep-text-primary); }
.td-sugg { font-size:12px;color:var(--ep-text-secondary);max-width:340px;line-height:1.5;text-align:right; }
@media (max-width:768px) { .td-footer { flex-direction:column; } .td-sugg { text-align:left;max-width:none; } }
</style>
