<template>
  <div class="storyboard-preview">
    <div class="preview-stage" :style="stageStyle">
      <transition name="scene-fade" mode="out-in">
        <div class="scene-visual" :key="currentIndex">
          <p class="visual-text">{{ currentScene?.visual }}</p>
        </div>
      </transition>
      <div class="narration-bar">
        <p>{{ currentScene?.narration }}</p>
      </div>
      <div v-if="currentScene?.animation" class="animation-hint">
        <span class="pulse-dot" />
        <span>{{ currentScene.animation }}</span>
      </div>
    </div>

    <div class="controls">
      <button class="ctrl-btn" @click="prev" :disabled="currentIndex === 0">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
      </button>
      <button class="ctrl-btn play-btn" @click="togglePlay">
        <svg v-if="!playing" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
      </button>
      <button class="ctrl-btn" @click="next" :disabled="currentIndex === scenes.length - 1">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
      </button>
      <span class="scene-counter">{{ currentIndex + 1 }} / {{ scenes.length }}</span>
    </div>

    <div class="timeline">
      <div
        v-for="(scene, i) in scenes"
        :key="scene.scene_id"
        class="timeline-seg"
        :class="{ active: i === currentIndex, done: i < currentIndex }"
        :style="{ flex: scene.duration_sec }"
        @click="goTo(i)"
      >
        <span class="seg-label">{{ scene.duration_sec }}s</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'

interface Scene {
  scene_id: number
  duration_sec: number
  visual: string
  narration: string
  animation?: string
}

const props = defineProps<{ scenes: Scene[] }>()

const currentIndex = ref(0)
const playing = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null

const currentScene = computed(() => props.scenes[currentIndex.value])

const GRADIENTS = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
  'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
]

const stageStyle = computed(() => ({
  background: GRADIENTS[currentIndex.value % GRADIENTS.length],
}))

function goTo(i: number) {
  currentIndex.value = i
  if (playing.value) scheduleNext()
}

function prev() {
  if (currentIndex.value > 0) goTo(currentIndex.value - 1)
}

function next() {
  if (currentIndex.value < props.scenes.length - 1) goTo(currentIndex.value + 1)
  else stopPlay()
}

function togglePlay() {
  playing.value ? stopPlay() : startPlay()
}

function startPlay() {
  playing.value = true
  scheduleNext()
}

function stopPlay() {
  playing.value = false
  if (timer) { clearTimeout(timer); timer = null }
}

function scheduleNext() {
  if (timer) clearTimeout(timer)
  const dur = (currentScene.value?.duration_sec || 5) * 1000
  timer = setTimeout(() => {
    if (currentIndex.value < props.scenes.length - 1) {
      currentIndex.value++
      scheduleNext()
    } else {
      stopPlay()
    }
  }, dur)
}

onBeforeUnmount(stopPlay)
</script>

<style scoped>
.storyboard-preview {
  border-radius: var(--ep-radius-md);
  overflow: hidden;
  border: 1px solid var(--ep-border-light);
}

.preview-stage {
  position: relative;
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px 40px;
  overflow: hidden;
}

.scene-visual {
  text-align: center;
}

.visual-text {
  font-size: 18px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  line-height: 1.6;
  margin: 0;
}

.narration-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 14px 24px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(6px);
}

.narration-bar p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.92);
  line-height: 1.6;
}

.animation-hint {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 20px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.7); }
}

.controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--ep-bg);
  border-top: 1px solid var(--ep-border-light);
  border-bottom: 1px solid var(--ep-border-light);
}

.ctrl-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--ep-border);
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--ep-text-secondary);
  transition: all 0.15s;
}

.ctrl-btn:hover:not(:disabled) {
  border-color: var(--ep-primary);
  color: var(--ep-primary);
}

.ctrl-btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.play-btn {
  width: 42px;
  height: 42px;
  background: var(--ep-primary);
  border-color: var(--ep-primary);
  color: white;
}

.play-btn:hover:not(:disabled) {
  color: white;
  opacity: 0.9;
}

.scene-counter {
  font-size: 13px;
  color: var(--ep-text-muted);
  margin-left: 4px;
}

.timeline {
  display: flex;
  height: 28px;
  gap: 2px;
  padding: 4px 8px;
  background: var(--ep-bg);
}

.timeline-seg {
  border-radius: 4px;
  background: var(--ep-border-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.timeline-seg.active {
  background: var(--ep-primary);
}

.timeline-seg.done {
  background: var(--ep-primary-light);
}

.seg-label {
  font-size: 10px;
  color: var(--ep-text-muted);
}

.timeline-seg.active .seg-label {
  color: white;
  font-weight: 600;
}

.scene-fade-enter-active,
.scene-fade-leave-active {
  transition: opacity 0.35s ease;
}

.scene-fade-enter-from,
.scene-fade-leave-to {
  opacity: 0;
}
</style>
