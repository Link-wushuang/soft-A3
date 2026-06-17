<template>
  <div class="markdown-body" v-html="rendered"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{ content: string }>()
const md = new MarkdownIt({ html: false, linkify: true })
const rendered = computed(() => md.render(props.content || ''))
</script>

<style scoped>
.markdown-body { line-height: 1.7; }
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) { margin-top: 16px; }
.markdown-body :deep(code) { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
.markdown-body :deep(pre) { background: #f5f5f5; padding: 12px; border-radius: 6px; overflow-x: auto; }
</style>
