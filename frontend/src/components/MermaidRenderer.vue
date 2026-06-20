<template>
  <div ref="container" class="mermaid-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{ code: string }>()
const container = ref<HTMLElement>()

mermaid.initialize({ startOnLoad: false, theme: 'default' })

async function render() {
  if (!container.value || !props.code) return
  try {
    const { svg } = await mermaid.render('mermaid-' + Date.now(), props.code)
    container.value.innerHTML = svg
  } catch {
    container.value.innerHTML = `<pre style="color:var(--ep-text-muted);background:var(--ep-bg);padding:16px;border-radius:10px;font-size:13px;white-space:pre-wrap">${props.code}</pre>`
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
