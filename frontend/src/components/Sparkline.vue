<template>
  <div class="sparkline" :style="{ width: width + 'px', height: height + 'px' }">
    <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
      <polyline
        :points="points"
        fill="none"
        :stroke="strokeColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <polygon
        v-if="showFill"
        :points="fillPoints"
        :fill="fillColor"
        opacity="0.15"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  data: number[]
  width?: number
  height?: number
  color?: string
  showFill?: boolean
}>(), {
  width: 80,
  height: 24,
  color: '#6366f1',
  showFill: true,
})

const strokeColor = computed(() => props.color)
const fillColor = computed(() => props.color)

const points = computed(() => {
  const { data, width, height } = props
  if (!data.length) return ''
  const max = Math.max(...data, 1)
  const min = Math.min(...data, 0)
  const range = max - min || 1
  const pad = 2
  const xStep = (width - pad * 2) / (data.length - 1 || 1)
  return data
    .map((v, i) => {
      const x = pad + i * xStep
      const y = height - pad - ((v - min) / range) * (height - pad * 2)
      return `${x},${y}`
    })
    .join(' ')
})

const fillPoints = computed(() => {
  const { data, width, height } = props
  if (!data.length) return ''
  const pts = points.value
  return `${2},${height} ${pts} ${width - 2},${height}`
})
</script>

<style scoped>
.sparkline { display: inline-block; vertical-align: middle; }
</style>
