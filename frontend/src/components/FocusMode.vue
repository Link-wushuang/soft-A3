<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

interface TopicItem { id: string; title: string; plannedMinutes: number }

const props = defineProps<{ topics: TopicItem[] }>()
const emit = defineEmits<{ (e:'exit'):void; (e:'complete',result:{totalMinutes:number,completedCount:number}):void }>()

const currentIndex = ref(0)
const elapsedSeconds = ref(0)
const isPaused = ref(false)
const completedIds = ref<string[]>([])

const current = computed(() => props.topics[currentIndex.value])
const progress = computed(() => Math.round((elapsedSeconds.value / 60 / current.value.plannedMinutes) * 100))

const timeLeft = computed(() => {
  const total = current.value.plannedMinutes * 60
  const left = Math.max(0, total - elapsedSeconds.value)
  return `${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`
})

let timer: number | null = null
function startTimer() {
  if (timer) return
  timer = window.setInterval(() => { if (!isPaused.value) elapsedSeconds.value++ }, 1000)
}
startTimer()

function pause() { isPaused.value = true }
function resume() { isPaused.value = false }
function skip() { next() }
function complete() { completedIds.value.push(current.value.id); next() }
function next() {
  if (currentIndex.value < props.topics.length - 1) { currentIndex.value++; elapsedSeconds.value = 0 }
  else finish()
}
function finish() {
  if (timer) { clearInterval(timer); timer = null }
  emit('complete', { totalMinutes: completedIds.value.length * 20, completedCount: completedIds.value.length })
}
function exit() {
  if (confirm('确定退出当前学习？进度将不会保存。')) {
    if (timer) clearInterval(timer)
    emit('exit')
  }
}
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<template>
  <Teleport to="body">
    <Transition name="zoom">
      <div v-if="topics.length" class="focus-root">
        <header class="focus-header">
          <div class="focus-top">
            <div class="focus-top-left">
              <button class="focus-x" @click="exit">✕</button>
              <div>
                <div class="focus-title">{{ current.title }}</div>
                <div class="focus-meta">第 {{ currentIndex + 1 }} / {{ topics.length }} 项</div>
              </div>
            </div>
            <div class="focus-timer">
              <span class="focus-time-num">{{ timeLeft }}</span>
              <span class="focus-time-of">/ {{ current.plannedMinutes }}:00</span>
            </div>
          </div>
          <div class="focus-progress-bar">
            <div class="focus-progress-fill" :style="{width:progress+'%'}" />
          </div>
        </header>

        <main class="focus-main">
          <div class="focus-content">
            <div class="focus-mode-label">📚 讲解模式</div>
            <h2 class="focus-heading">{{ current.title }}</h2>
            <div class="focus-text">
              <p>这里是 {{ current.title }} 的讲解内容...</p>
              <p>实际接入时换成视频、文章、题目等内容组件。</p>
            </div>
          </div>
        </main>

        <footer class="focus-footer">
          <div class="focus-footer-left">
            <button class="focus-btn-ghost">📝 笔记</button>
            <button class="focus-btn-ghost">❓ 提问</button>
          </div>
          <div class="focus-footer-right">
            <button class="focus-btn" @click="isPaused ? resume() : pause()">
              {{ isPaused ? '▶ 继续' : '⏸ 暂停' }}
            </button>
            <button class="focus-btn" @click="skip">⏭ 跳过</button>
            <button class="focus-btn-done" @click="complete">✓ 完成 →</button>
          </div>
        </footer>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.focus-root { position:fixed;inset:0;z-index:3000;background:#0f172a;display:flex;flex-direction:column;color:#e2e8f0; }
.focus-header { padding:20px 32px;border-bottom:1px solid rgba(255,255,255,0.06); }
.focus-top { display:flex;align-items:center;justify-content:space-between;margin-bottom:16px; }
.focus-top-left { display:flex;align-items:center;gap:14px; }
.focus-x { width:32px;height:32px;border-radius:50%;border:none;background:rgba(255,255,255,0.06);color:#94a3b8;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px; } .focus-x:hover { background:rgba(255,255,255,0.12);color:white; }
.focus-title { font-size:15px;font-weight:600;color:#f1f5f9; }
.focus-meta { font-size:11px;color:#64748b;margin-top:2px; }
.focus-timer { display:flex;align-items:baseline;gap:6px; }
.focus-time-num { font-size:32px;font-weight:700;font-family:'Menlo','Monaco','Consolas',monospace;font-variant-numeric:tabular-nums;color:#f1f5f9;letter-spacing:-0.02em; }
.focus-time-of { font-size:13px;color:#64748b; }

.focus-progress-bar { height:3px;border-radius:2px;background:rgba(255,255,255,0.06);overflow:hidden; }
.focus-progress-fill { height:100%;border-radius:2px;background:linear-gradient(90deg,#6366f1,#8b5cf6);transition:width 1s linear; }

.focus-main { flex:1;display:flex;align-items:center;justify-content:center;padding:32px;overflow-y:auto; }
.focus-content { width:100%;max-width:720px;background:rgba(255,255,255,0.04);border-radius:16px;padding:40px;border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(12px); }
.focus-mode-label { text-align:center;color:#64748b;font-size:13px;margin-bottom:20px; }
.focus-heading { font-size:28px;font-weight:700;text-align:center;margin:0 0 28px;color:#f1f5f9; }
.focus-text { color:#94a3b8;line-height:1.8;font-size:15px; }
.focus-text p { margin:0 0 12px; }

.focus-footer { padding:16px 32px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center; }
.focus-footer-left { display:flex;gap:8px; }
.focus-footer-right { display:flex;gap:8px; }
.focus-btn-ghost { padding:8px 14px;border:none;border-radius:8px;background:transparent;color:#94a3b8;font-size:13px;cursor:pointer; } .focus-btn-ghost:hover { background:rgba(255,255,255,0.06);color:white; }
.focus-btn { padding:10px 18px;border:none;border-radius:8px;background:rgba(255,255,255,0.08);color:#cbd5e1;font-size:13px;cursor:pointer; } .focus-btn:hover { background:rgba(255,255,255,0.14);color:white; }
.focus-btn-done { padding:10px 22px;border:none;border-radius:8px;background:#10b981;color:white;font-size:13px;font-weight:600;cursor:pointer;box-shadow:0 4px 14px rgba(16,185,129,0.3); } .focus-btn-done:hover { background:#059669; }

.zoom-enter-active { transition:all 0.4s cubic-bezier(0.16,1,0.3,1); } .zoom-leave-active { transition:all 0.2s ease-in; }
.zoom-enter-from { opacity:0;transform:scale(0.95); } .zoom-leave-to { opacity:0;transform:scale(1.05); }

@media (max-width:640px) {
  .focus-header { padding:14px 16px; } .focus-main { padding:16px; } .focus-footer { padding:12px 16px; }
  .focus-time-num { font-size:24px; } .focus-heading { font-size:22px; } .focus-content { padding:24px; }
  .focus-footer-right { gap:4px; } .focus-btn,.focus-btn-done { padding:8px 14px;font-size:12px; }
}
</style>
