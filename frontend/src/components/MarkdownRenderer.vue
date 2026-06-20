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
.markdown-body {
  line-height: 1.8;
  font-size: 14px;
  color: var(--ep-text-primary);
}

.markdown-body :deep(h1) {
  font-size: 22px;
  font-weight: 700;
  margin: 24px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--ep-border-light);
}

.markdown-body :deep(h2) {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 10px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px;
}

.markdown-body :deep(p) {
  margin: 8px 0;
}

.markdown-body :deep(code) {
  background: var(--ep-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Menlo', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  color: var(--ep-danger);
}

.markdown-body :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px 20px;
  border-radius: var(--ep-radius-md);
  overflow-x: auto;
  margin: 12px 0;
  font-size: 13px;
  line-height: 1.6;
}

.markdown-body :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
  margin: 8px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(blockquote) {
  margin: 12px 0;
  padding: 10px 16px;
  border-left: 3px solid var(--ep-primary);
  background: var(--ep-primary-light);
  border-radius: 0 var(--ep-radius-sm) var(--ep-radius-sm) 0;
  color: var(--ep-text-secondary);
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 13px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid var(--ep-border);
  padding: 8px 12px;
  text-align: left;
}

.markdown-body :deep(th) {
  background: var(--ep-bg-hover);
  font-weight: 600;
}

.markdown-body :deep(strong) {
  font-weight: 600;
  color: var(--ep-text-primary);
}
</style>
