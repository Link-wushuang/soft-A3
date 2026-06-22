<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft, Close } from '@element-plus/icons-vue'

interface TopicItem {
  id: string; title: string; category: string
  difficulty: 'easy'|'medium'|'hard'; status: 'unmastered'|'mastered'
  recommendedMinutes: number; masteredCount: number; totalCount: number
  recommended?: boolean; reason?: string
}

const props = defineProps<{ modelValue: boolean; remainingMinutes: number; topics: TopicItem[] }>()
const emit = defineEmits<{ (e:'update:modelValue',v:boolean):void; (e:'start',plan:{selectedIds:string[],mode:string}):void }>()

const selectedIds = ref<string[]>([])
const showTemplateInput = ref(false)
const templateName = ref('')
const templateSaved = ref(false)

function saveTemplate() {
  if (!templateName.value) return
  // TODO: 调用 store / 接口保存模板
  console.log('保存模板:', { name: templateName.value, topics: selectedIds.value, mode: mode.value })
  templateSaved.value = true
  setTimeout(() => { templateSaved.value = false }, 2000)
  showTemplateInput.value = false
  templateName.value = ''
}
const mode = ref<'focus'|'casual'|'pomodoro'>('focus')
const reminderMin = ref(25)
const difficulty = ref<'adaptive'|'challenge'|'review'>('adaptive')

const totalMinutes = computed(() => props.topics.filter(t=>selectedIds.value.includes(t.id)).reduce((s,t)=>s+t.recommendedMinutes,0))
const overflow = computed(() => totalMinutes.value - props.remainingMinutes)
const maxBar = computed(() => Math.max(...props.topics.map(t=>t.recommendedMinutes)))

function toggleTopic(id:string) { const i=selectedIds.value.indexOf(id); if(i>=0) selectedIds.value.splice(i,1); else selectedIds.value.push(id) }
function close() { emit('update:modelValue',false) }
function start() { emit('start',{selectedIds:selectedIds.value,mode:mode.value}); close() }

function diffColor(d:string) { return d==='hard'?'hard':d==='medium'?'medium':'easy' }
function diffText(d:string) { return {easy:'简单',medium:'中等',hard:'困难'}[d]||d }
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="modelValue" class="drawer-overlay" @click="close" />
    </Transition>
    <Transition name="slide">
      <aside v-if="modelValue" class="drawer-panel" @click.stop>
        <header class="drawer-header">
          <button class="drawer-back" @click="close"><el-icon :size="18"><ArrowLeft /></el-icon></button>
          <h2 class="drawer-title">制定今日学习计划</h2>
          <span class="drawer-time">17:30</span>
          <button class="drawer-x" @click="close"><el-icon :size="16"><Close /></el-icon></button>
        </header>

        <div class="drawer-body">
          <!-- Summary -->
          <div class="drawer-summary">
            <div class="ds-item"><div class="ds-num">{{ remainingMinutes }}</div><div class="ds-label">剩余分钟</div></div>
            <div class="ds-item ds-border"><div class="ds-num">{{ selectedIds.length }}</div><div class="ds-label">已选主题</div></div>
            <div class="ds-item"><div class="ds-num" :class="overflow>0?'red':''">{{ totalMinutes }}</div><div class="ds-label">预计分钟</div></div>
          </div>

          <!-- Topics -->
          <section>
            <h3 class="dsec-title">📚 推荐主题 <span class="dsec-hint">基于你的画像</span></h3>
            <label v-for="t in topics" :key="t.id" class="topic-row" :class="{checked:selectedIds.includes(t.id)}">
              <input type="checkbox" :checked="selectedIds.includes(t.id)" @change="toggleTopic(t.id)" class="topic-check" />
              <div class="topic-body">
                <div class="topic-head">
                  <span class="topic-name">{{ t.title }}</span>
                  <span class="topic-min">{{ t.recommendedMinutes }} min</span>
                </div>
                <div class="topic-meta">
                  <span>{{ t.category }}</span>
                  <span :class="['topic-diff', diffColor(t.difficulty)]">{{ diffText(t.difficulty) }}</span>
                  <span>已掌握 {{ t.masteredCount }}/{{ t.totalCount }}</span>
                </div>
                <div class="topic-bar"><div class="topic-bar-fill" :style="{width:(t.masteredCount/t.totalCount*100)+'%'}" /></div>
                <div v-if="t.recommended" class="topic-reason">💡 {{ t.reason }}</div>
              </div>
            </label>
          </section>

          <!-- Time allocation -->
          <section style="margin-top:20px">
            <h3 class="dsec-title">⏱ 时间分配</h3>
            <div class="alloc-box">
              <div v-for="t in topics.filter(x=>selectedIds.includes(x.id))" :key="'a-'+t.id" class="alloc-row">
                <span class="alloc-name">{{ t.title }}</span>
                <div class="alloc-track"><div class="alloc-fill" :style="{width:(t.recommendedMinutes/maxBar*100)+'%'}" /></div>
                <span class="alloc-min">{{ t.recommendedMinutes }}min</span>
              </div>
              <div class="alloc-total">
                <span>合计 {{ totalMinutes }} / {{ remainingMinutes }} min</span>
                <span v-if="overflow>0" class="red">超出 {{ overflow }} min</span>
                <span v-else class="green">还可加 {{ remainingMinutes - totalMinutes }} min</span>
              </div>
            </div>
          </section>

          <!-- Preferences -->
          <section style="margin-top:20px">
            <h3 class="dsec-title">⚙ 学习偏好</h3>
            <div class="pref-box">
              <div class="pref-row">
                <span class="pref-label">学习模式</span>
                <div class="pref-tabs">
                  <button v-for="m in ['focus','casual','pomodoro']" :key="m" @click="mode=m as any"
                          :class="['pref-tab',{on:mode===m}]">{{ {focus:'专注',casual:'轻松',pomodoro:'番茄'}[m] }}</button>
                </div>
              </div>
              <div class="pref-row">
                <span class="pref-label">休息提醒</span>
                <div class="pref-select-wrap">
                  <span class="pref-select-label">每</span>
                  <select v-model.number="reminderMin" class="pref-select">
                    <option :value="15">15</option><option :value="25">25</option><option :value="45">45</option>
                  </select>
                  <span class="pref-select-label">分钟</span>
                </div>
              </div>
              <div class="pref-row">
                <span class="pref-label">难度</span>
                <div class="pref-tabs">
                  <button v-for="d in ['adaptive','challenge','review']" :key="d" @click="difficulty=d as any"
                          :class="['pref-tab',{on:difficulty===d}]">{{ {adaptive:'自适应',challenge:'挑战',review:'巩固'}[d] }}</button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Template save popover -->
        <Transition name="slide-up">
          <div v-if="showTemplateInput" class="template-popover">
            <div class="tp-row">
              <span class="tp-icon">💾</span>
              <input v-model="templateName" placeholder="如：每日复习计划" class="tp-input"
                     @keyup.enter="saveTemplate" ref="tpInputRef" />
              <button class="tp-btn-cancel" @click="showTemplateInput = false">取消</button>
              <button :disabled="!templateName" class="tp-btn-save" :class="{dimmed:!templateName}" @click="saveTemplate">保存</button>
            </div>
          </div>
        </Transition>

        <!-- Saved toast -->
        <Transition name="slide-up">
          <div v-if="templateSaved" class="template-toast">✅ 模板已保存</div>
        </Transition>

        <footer class="drawer-footer">
          <button class="df-cancel" @click="close">取消</button>
          <div class="df-right">
            <button class="df-save" @click="showTemplateInput = !showTemplateInput">保存为模板</button>
            <button :disabled="selectedIds.length===0||overflow>0" :class="['df-start',{dimmed:selectedIds.length===0||overflow>0}]" @click="start">启动学习计划 ▶</button>
          </div>
        </footer>
      </aside>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-overlay { position:fixed;inset:0;z-index:2000;background:rgba(15,23,42,0.4);backdrop-filter:blur(4px); }
.drawer-panel { position:fixed;right:0;top:0;bottom:0;width:480px;max-width:90vw;z-index:2001;background:white;display:flex;flex-direction:column;box-shadow:-8px 0 30px rgba(0,0,0,0.08); }
.drawer-header { display:flex;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid var(--ep-border-light); }
.drawer-back { background:none;border:none;color:var(--ep-text-muted);cursor:pointer;padding:4px;border-radius:6px; } .drawer-back:hover { color:var(--ep-text-primary);background:var(--ep-bg-hover); }
.drawer-title { flex:1;font-size:15px;font-weight:600;color:var(--ep-text-primary);margin:0; }
.drawer-time { font-size:11px;color:var(--ep-text-muted); }
.drawer-x { background:none;border:none;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:var(--ep-text-muted);cursor:pointer; } .drawer-x:hover { background:var(--ep-bg-hover);color:var(--ep-text-primary); }
.drawer-body { flex:1;overflow-y:auto;padding:20px; }

.drawer-summary { display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;padding:12px;border-radius:12px;background:#f8fafc;margin-bottom:24px; }
.ds-item { text-align:center; } .ds-item.ds-border { border-left:1px solid #e2e8f0;border-right:1px solid #e2e8f0; }
.ds-num { font-size:20px;font-weight:700;color:var(--ep-text-primary); } .ds-num.red { color:#ef4444; }
.ds-label { font-size:10px;color:var(--ep-text-muted);margin-top:2px; }

.dsec-title { font-size:13px;font-weight:600;color:var(--ep-text-primary);margin:0 0 12px; }
.dsec-hint { font-size:10px;font-weight:400;color:var(--ep-text-muted); }

.topic-row { display:flex;align-items:flex-start;gap:10px;padding:12px;border-radius:12px;border:2px solid var(--ep-border-light);cursor:pointer;transition:all var(--ep-transition);margin-bottom:8px; } .topic-row:hover { border-color:#cbd5e1; } .topic-row.checked { border-color:#c7d2fe;background:#fafaff; }
.topic-check { margin-top:2px;width:16px;height:16px;accent-color:#6366f1; }
.topic-body { flex:1;min-width:0; }
.topic-head { display:flex;justify-content:space-between;margin-bottom:2px; } .topic-name { font-weight:500;color:var(--ep-text-primary);font-size:13px; } .topic-min { font-size:11px;color:var(--ep-text-muted); }
.topic-meta { display:flex;gap:8px;font-size:10px;color:var(--ep-text-muted);margin-bottom:6px; }
.topic-diff { padding:1px 6px;border-radius:4px;font-size:9px;font-weight:600; } .topic-diff.easy { background:var(--ep-success-light);color:#059669; } .topic-diff.medium { background:var(--ep-warning-light);color:#d97706; } .topic-diff.hard { background:var(--ep-danger-light);color:#dc2626; }
.topic-bar { height:3px;border-radius:2px;background:#e5e7eb;overflow:hidden; } .topic-bar-fill { height:100%;border-radius:2px;background:#6366f1; }
.topic-reason { font-size:10px;color:var(--ep-primary);margin-top:4px; }

.alloc-box { background:#f8fafc;border-radius:12px;padding:12px; }
.alloc-row { display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:11px; } .alloc-row:last-of-type { margin-bottom:0; }
.alloc-name { width:64px;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ep-text-primary); }
.alloc-track { flex:1;height:6px;border-radius:3px;background:#e5e7eb;overflow:hidden; } .alloc-fill { height:100%;border-radius:3px;background:linear-gradient(90deg,#6366f1,#8b5cf6); }
.alloc-min { width:40px;text-align:right;color:var(--ep-text-muted);flex-shrink:0; }
.alloc-total { display:flex;justify-content:space-between;padding-top:10px;border-top:1px solid #e2e8f0;margin-top:8px;font-size:10px;color:var(--ep-text-muted); } .alloc-total .red { color:#ef4444;font-weight:500; } .alloc-total .green { color:#10b981;font-weight:500; }

.pref-box { background:#f8fafc;border-radius:12px;padding:12px; }
.pref-row { display:flex;align-items:center;justify-content:space-between;margin-bottom:10px; } .pref-row:last-child { margin-bottom:0; }
.pref-label { font-size:11px;color:var(--ep-text-secondary); }
.pref-tabs { display:flex;gap:2px;padding:2px;background:white;border-radius:8px;border:1px solid #e2e8f0; } .pref-tab { padding:4px 12px;font-size:11px;border:none;background:none;border-radius:6px;color:var(--ep-text-muted);cursor:pointer; } .pref-tab.on { background:var(--ep-primary);color:white; }
.pref-select-wrap { display:flex;align-items:center;gap:4px; } .pref-select-label { font-size:11px;color:var(--ep-text-muted); } .pref-select { font-size:11px;padding:4px 8px;border-radius:6px;border:1px solid #e2e8f0;background:white;color:var(--ep-text-primary); }

.drawer-footer { padding:14px 20px;border-top:1px solid var(--ep-border-light);display:flex;justify-content:space-between;align-items:center;position:relative; }
.df-cancel { background:none;border:none;font-size:13px;color:var(--ep-text-muted);cursor:pointer; } .df-cancel:hover { color:var(--ep-text-primary); }
.df-right { display:flex;gap:8px; }
.df-save { padding:7px 14px;font-size:11px;border:1px solid #e2e8f0;border-radius:8px;background:white;color:var(--ep-text-secondary);cursor:pointer; } .df-save:hover { background:var(--ep-bg-hover); }
.df-start { padding:8px 18px;font-size:13px;font-weight:500;border:none;border-radius:8px;background:var(--ep-primary);color:white;cursor:pointer;box-shadow:0 2px 8px rgba(99,102,241,0.3); } .df-start:hover { background:var(--ep-primary-hover); } .df-start.dimmed { background:#e2e8f0;color:#94a3b8;cursor:not-allowed;box-shadow:none; }

.template-popover { position:absolute;bottom:100%;left:20px;right:20px;margin-bottom:8px;padding:12px;background:white;border:1px solid #c7d2fe;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);z-index:10; }
.tp-row { display:flex;align-items:center;gap:8px; }
.tp-icon { font-size:16px;flex-shrink:0; }
.tp-input { flex:1;padding:6px 8px;font-size:12px;border:none;border-bottom:2px solid #e2e8f0;outline:none;background:transparent;color:var(--ep-text-primary);transition:border-color 0.2s; } .tp-input:focus { border-bottom-color:var(--ep-primary); }
.tp-btn-cancel { background:none;border:none;font-size:11px;color:var(--ep-text-muted);cursor:pointer;padding:4px 8px; } .tp-btn-cancel:hover { color:var(--ep-text-primary); }
.tp-btn-save { padding:5px 14px;font-size:11px;border:none;border-radius:6px;background:var(--ep-primary);color:white;cursor:pointer; } .tp-btn-save.dimmed { background:#e2e8f0;color:#94a3b8;cursor:not-allowed; }

.template-toast { position:absolute;bottom:70px;left:50%;transform:translateX(-50%);padding:6px 16px;background:#10b981;color:white;font-size:11px;font-weight:500;border-radius:8px;z-index:20;white-space:nowrap;box-shadow:0 2px 8px rgba(16,185,129,0.3); }

.fade-enter-active,.fade-leave-active { transition:opacity 0.25s; } .fade-enter-from,.fade-leave-to { opacity:0; }
.slide-enter-active,.slide-leave-active { transition:transform 0.3s cubic-bezier(0.16,1,0.3,1); } .slide-enter-from,.slide-leave-to { transform:translateX(100%); }
.slide-up-enter-active,.slide-up-leave-active { transition:all 0.25s ease-out; } .slide-up-enter-from,.slide-up-leave-to { opacity:0;transform:translateY(10px); }
</style>
