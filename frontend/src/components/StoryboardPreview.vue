<template>
  <div class="video-player" :class="{ fullscreen: isFullscreen }" ref="playerRef">
    <div class="stage" @click="togglePlay">
      <!-- SVG scene or text fallback -->
      <div class="scene-wrap" :key="currentIndex">
        <div v-if="isSvgScene" class="svg-stage" v-html="sanitizedVisual" />
        <div v-else class="text-stage">
          <div class="text-bg" :style="{ background: GRADIENTS[currentIndex % GRADIENTS.length] }">
            <div class="text-shapes"><div v-for="i in 6" :key="i" class="shape" :class="'s'+i" /></div>
          </div>
          <div class="text-body">
            <div class="scene-badge">场景 {{ currentIndex + 1 }}</div>
            <p class="visual-text">{{ currentScene?.visual }}</p>
          </div>
        </div>
      </div>

      <!-- Narration subtitle -->
      <div class="subtitle" v-if="currentScene?.narration">
        <p>{{ currentScene.narration }}</p>
      </div>

      <!-- Animation indicator -->
      <div v-if="currentScene?.animation" class="anim-pill">
        <span class="anim-dot" /><span>{{ currentScene.animation }}</span>
      </div>

      <!-- Play/pause flash -->
      <transition name="fade-quick">
        <div v-if="showIcon" class="center-icon">
          <svg v-if="playing" width="36" height="36" viewBox="0 0 24 24" fill="white"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          <svg v-else width="36" height="36" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
        </div>
      </transition>
    </div>

    <!-- Player chrome -->
    <div class="chrome">
      <div class="progress-track" @mousedown="startSeek" ref="trackRef">
        <div class="progress-fill" :style="{ width: progress + '%' }">
          <div class="progress-thumb" />
        </div>
      </div>
      <div class="bar">
        <div class="bar-left">
          <button class="cb" @click.stop="togglePlay">
            <svg v-if="!playing" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
          </button>
          <button class="cb" @click.stop="prev" :disabled="currentIndex===0">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
          </button>
          <button class="cb" @click.stop="next" :disabled="currentIndex===scenes.length-1">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M16 18h2V6h-2zM5.5 12l8.5 6V6z" transform="scale(-1,1) translate(-24,0)"/></svg>
          </button>
          <span class="time">{{ fmtTime(elapsed) }} / {{ fmtTime(totalDur) }}</span>
        </div>
        <div class="bar-right">
          <span class="scene-num">{{ currentIndex+1 }}/{{ scenes.length }}</span>
          <button class="cb" @click.stop="toggleFs" title="全屏">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path v-if="!isFullscreen" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
              <path v-else d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount, watch } from 'vue'

interface Scene { scene_id: number; duration_sec: number; visual: string; narration: string; animation?: string }
const props = defineProps<{ scenes: Scene[] }>()

const currentIndex = ref(0)
const playing = ref(false)
const isFullscreen = ref(false)
const showIcon = ref(false)
const elapsed = ref(0)
const playerRef = ref<HTMLElement>()
const trackRef = ref<HTMLElement>()
let timer: ReturnType<typeof setInterval> | null = null
let iconTimer: ReturnType<typeof setTimeout> | null = null

const GRADIENTS = [
  'linear-gradient(135deg,#1e1b4b,#312e81,#4338ca)',
  'linear-gradient(135deg,#0c4a6e,#0369a1,#0ea5e9)',
  'linear-gradient(135deg,#134e4a,#0f766e,#14b8a6)',
  'linear-gradient(135deg,#4a1d96,#6d28d9,#a78bfa)',
]

const currentScene = computed(() => props.scenes[currentIndex.value])
const totalDur = computed(() => props.scenes.reduce((s, sc) => s + sc.duration_sec, 0))

const isSvgScene = computed(() => {
  const v = currentScene.value?.visual || ''
  return v.trim().startsWith('<svg')
})

function sanitizeSvg(raw: string): string {
  let s = raw.replace(/<script[\s\S]*?<\/script>/gi, '')
  s = s.replace(/\bon\w+\s*=/gi, 'data-removed=')
  s = s.replace(/javascript\s*:/gi, 'removed:')
  return s
}

const sanitizedVisual = computed(() => sanitizeSvg(currentScene.value?.visual || ''))

const progress = computed(() => {
  if (!totalDur.value) return 0
  let before = 0
  for (let i = 0; i < currentIndex.value; i++) before += props.scenes[i].duration_sec
  const dur = currentScene.value?.duration_sec || 1
  return ((before + dur * Math.min(elapsed.value / dur, 1)) / totalDur.value) * 100
})

function fmtTime(s: number) { const m = Math.floor(s / 60); return `${m}:${Math.floor(s % 60).toString().padStart(2, '0')}` }

function togglePlay() {
  playing.value ? pause() : play()
  showIcon.value = true
  if (iconTimer) clearTimeout(iconTimer)
  iconTimer = setTimeout(() => { showIcon.value = false }, 500)
}

function play() { playing.value = true; elapsed.value = 0; tick() }
function pause() { playing.value = false; if (timer) { clearInterval(timer); timer = null } }

function tick() {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    elapsed.value += 0.1
    const dur = currentScene.value?.duration_sec || 5
    if (elapsed.value >= dur) {
      if (currentIndex.value < props.scenes.length - 1) { currentIndex.value++; elapsed.value = 0 }
      else { pause(); elapsed.value = dur }
    }
  }, 100)
}

function prev() { if (currentIndex.value > 0) { currentIndex.value--; elapsed.value = 0; if (playing.value) tick() } }
function next() { if (currentIndex.value < props.scenes.length - 1) { currentIndex.value++; elapsed.value = 0; if (playing.value) tick() } else pause() }

function startSeek(e: MouseEvent) {
  seekFromEvent(e)
  const onMove = (ev: MouseEvent) => seekFromEvent(ev)
  const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function seekFromEvent(e: MouseEvent) {
  if (!trackRef.value) return
  const rect = trackRef.value.getBoundingClientRect()
  const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width))
  const target = pct * totalDur.value
  let acc = 0
  for (let i = 0; i < props.scenes.length; i++) {
    if (acc + props.scenes[i].duration_sec > target) { currentIndex.value = i; elapsed.value = target - acc; if (playing.value) tick(); return }
    acc += props.scenes[i].duration_sec
  }
}

function toggleFs() {
  if (!playerRef.value) return
  if (!document.fullscreenElement) { playerRef.value.requestFullscreen?.(); isFullscreen.value = true }
  else { document.exitFullscreen?.(); isFullscreen.value = false }
}

watch(() => props.scenes, () => { currentIndex.value = 0; elapsed.value = 0; pause() })
onBeforeUnmount(() => { if (timer) clearInterval(timer); if (iconTimer) clearTimeout(iconTimer) })
</script>

<style scoped>
.video-player { border-radius: var(--ep-radius-md); overflow: hidden; border: 1px solid var(--ep-border-light); background: #0f172a; }
.video-player.fullscreen { border-radius: 0; border: none; }

.stage { position: relative; aspect-ratio: 16/9; cursor: pointer; overflow: hidden; }

/* SVG rendering */
.scene-wrap { width: 100%; height: 100%; position: absolute; inset: 0; }
.svg-stage { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: #0f172a; }
.svg-stage :deep(svg) { width: 100%; height: 100%; display: block; }

/* Text fallback */
.text-stage { width: 100%; height: 100%; position: relative; display: flex; align-items: center; justify-content: center; }
.text-bg { position: absolute; inset: 0; }
.text-shapes { position: absolute; inset: 0; }
.shape { position: absolute; border-radius: 50%; opacity: 0.1; background: white; animation: fl 12s ease-in-out infinite; }
.s1 { width: 100px; height: 100px; top: -20px; right: -10px; animation-duration: 10s; }
.s2 { width: 60px; height: 60px; bottom: 15%; left: 8%; animation-duration: 14s; animation-delay: -3s; }
.s3 { width: 40px; height: 40px; top: 35%; right: 18%; border-radius: 6px; animation-duration: 11s; animation-delay: -5s; }
.s4 { width: 120px; height: 120px; bottom: -30px; right: 25%; opacity: 0.05; animation-duration: 16s; }
.s5 { width: 25px; height: 25px; top: 22%; left: 22%; animation-duration: 9s; animation-delay: -7s; }
.s6 { width: 50px; height: 50px; bottom: 28%; right: 10%; border-radius: 6px; animation-duration: 13s; animation-delay: -4s; }
@keyframes fl { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }

.text-body { position: relative; z-index: 2; text-align: center; padding: 24px 40px; max-width: 85%; animation: ti .5s ease-out; }
@keyframes ti { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.scene-badge { display: inline-block; padding: 4px 14px; border-radius: 20px; background: rgba(255,255,255,0.15); font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 16px; }
.visual-text { font-size: 20px; font-weight: 700; color: white; line-height: 1.7; text-shadow: 0 2px 12px rgba(0,0,0,0.3); margin: 0; }

/* Overlays */
.subtitle { position: absolute; bottom: 0; left: 0; right: 0; z-index: 3; padding: 14px 24px; background: linear-gradient(transparent, rgba(0,0,0,0.75)); }
.subtitle p { margin: 0; font-size: 14px; color: rgba(255,255,255,0.92); line-height: 1.65; text-align: center; text-shadow: 0 1px 4px rgba(0,0,0,0.5); }

.anim-pill { position: absolute; top: 12px; right: 12px; z-index: 3; display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 20px; background: rgba(0,0,0,0.4); backdrop-filter: blur(6px); font-size: 11px; color: rgba(255,255,255,0.85); }
.anim-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; animation: pulse 1.4s infinite; }
@keyframes pulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.6); } }

.center-icon { position: absolute; inset: 0; z-index: 5; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.25); }
.fade-quick-enter-active, .fade-quick-leave-active { transition: opacity 0.2s; }
.fade-quick-enter-from, .fade-quick-leave-to { opacity: 0; }

/* Chrome */
.chrome { background: #1e293b; }
.progress-track { height: 4px; background: rgba(255,255,255,0.1); cursor: pointer; position: relative; transition: height 0.15s; }
.progress-track:hover { height: 6px; }
.progress-fill { height: 100%; background: var(--ep-primary); position: relative; transition: width 0.1s linear; border-radius: 0 2px 2px 0; }
.progress-thumb { position: absolute; right: -5px; top: 50%; transform: translateY(-50%); width: 10px; height: 10px; border-radius: 50%; background: white; opacity: 0; transition: opacity 0.15s; box-shadow: 0 0 4px rgba(0,0,0,0.4); }
.progress-track:hover .progress-thumb { opacity: 1; }

.bar { display: flex; justify-content: space-between; align-items: center; padding: 6px 12px 8px; }
.bar-left, .bar-right { display: flex; align-items: center; gap: 4px; }
.cb { background: none; border: none; color: #94a3b8; cursor: pointer; padding: 6px; border-radius: 6px; display: flex; align-items: center; justify-content: center; transition: color 0.15s, background 0.15s; }
.cb:hover:not(:disabled) { color: white; background: rgba(255,255,255,0.08); }
.cb:disabled { opacity: 0.3; cursor: default; }
.time { font-size: 12px; color: #94a3b8; font-variant-numeric: tabular-nums; margin-left: 8px; }
.scene-num { font-size: 11px; color: #64748b; padding: 2px 8px; background: rgba(255,255,255,0.06); border-radius: 4px; }
</style>
