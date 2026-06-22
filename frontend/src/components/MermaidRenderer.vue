<template>
  <div ref="container" class="mermaid-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{ code: string }>()
const container = ref<HTMLElement>()

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' })

function cleanCode(raw: string): string {
  let s = raw.trim()
  const fenceRe = /^```(?:mermaid)?\s*\n?([\s\S]*?)\n?\s*```$/
  const m = s.match(fenceRe)
  if (m) s = m[1].trim()
  return s
}

async function render() {
  if (!container.value || !props.code) return
  const code = cleanCode(props.code)
  try {
    const id = 'mermaid-' + Math.random().toString(36).slice(2, 8)
    const { svg } = await mermaid.render(id, code)
    container.value.innerHTML = svg
  } catch (err) {
    console.warn('Mermaid render failed:', err)
    container.value.innerHTML = `<pre style="color:var(--ep-text-muted);background:var(--ep-bg);padding:16px;border-radius:10px;font-size:13px;white-space:pre-wrap">${code}</pre>`
  }
}

onMounted(render)
watch(() => props.code, render)
</script>

<style scoped>
.mermaid-container {
  text-align: center;
  padding: 20px;
  background: var(--ep-bg-hover);
  border-radius: var(--ep-radius-md);
}
</style>
