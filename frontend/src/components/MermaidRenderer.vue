<template>
  <div ref="container" class="mermaid-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import mermaid from 'mermaid'

const props = defineProps<{ code: string }>()
const container = ref<HTMLElement>()

mermaid.initialize({ startOnLoad: false, theme: 'default', securityLevel: 'loose' })

function cleanCode(raw: string): string {
  let s = raw.trim()
  // 去除 markdown 代码块包裹
  const fenceRe = /^```(?:mermaid)?\s*\n?([\s\S]*?)\n?\s*```$/
  const m = s.match(fenceRe)
  if (m) s = m[1].trim()
  return s
}

/** 对 Mermaid 节点文字中的特殊字符做转义，避免 mermaid 解析失败。
 *  Mermaid 节点标签如果含括号、方括号、引号等会被误认为语法符号。
 *  用双引号包裹标签可避免大部分问题。 */
function sanitizeMermaid(code: string): string {
  let s = code
  // 修正 graph TD 声明前可能的多余文字
  s = s.replace(/^[^g]*((?:graph|flowchart|mindmap|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|journey)\s+(?:TD|TB|BT|RL|LR))/i, '$1')
  // 节点标签中含特殊字符的，用双引号包裹：形如 A[文字] -> A["文字"]
  // 匹配 [内容] 和 (内容) 中含特殊字符的情况
  s = s.replace(/\[([^\]]*[()"\n<>][^\]]*)\]/g, (_, inner) => `["${inner.replace(/"/g, '#quot;')}"]`)
  s = s.replace(/\(([^)]*[\[\]"'\n<>][^)]*)\)/g, (_, inner) => `("${inner.replace(/"/g, '#quot;')}")`)
  return s
}

/** 清理 mermaid.render 失败时插入到 body 的错误提示元素 */
function cleanupMermaidErrorElements() {
  // mermaid 11.x 失败时会在 body 末尾插入 id 形如 dmermaid-xxxx 的错误 div
  const errorEls = document.querySelectorAll('body > div[id^="dmermaid"]')
  errorEls.forEach(el => el.remove())
}

async function render() {
  if (!container.value || !props.code) return
  const rawCode = cleanCode(props.code)
  const code = sanitizeMermaid(rawCode)
  try {
    const id = 'mermaid-' + Math.random().toString(36).slice(2, 8)
    const { svg } = await mermaid.render(id, code)
    container.value.innerHTML = svg
  } catch (err) {
    console.warn('Mermaid render failed, showing raw code:', err)
    cleanupMermaidErrorElements()
    // 尝试一次：把所有节点标签强制加引号后重试
    try {
      const id2 = 'mermaid-' + Math.random().toString(36).slice(2, 8)
      const forceQuoted = code.replace(/\[(.+?)\]/g, '["$1"]')
      const { svg } = await mermaid.render(id2, forceQuoted)
      container.value.innerHTML = svg
      return
    } catch {
      cleanupMermaidErrorElements()
    }
    // 最终降级：显示原始代码
    container.value.innerHTML = `<pre style="color:var(--ep-text-muted);background:var(--ep-bg);padding:16px;border-radius:10px;font-size:13px;white-space:pre-wrap;overflow-x:auto">${rawCode.replace(/</g, '&lt;')}</pre>`
  }
}

onMounted(render)
watch(() => props.code, render)
onBeforeUnmount(cleanupMermaidErrorElements)
</script>

<style scoped>
.mermaid-container {
  text-align: center;
  padding: 20px;
  background: var(--ep-bg-hover);
  border-radius: var(--ep-radius-md);
}
</style>
