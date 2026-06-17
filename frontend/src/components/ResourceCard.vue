<template>
  <el-card shadow="hover" class="resource-card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>{{ typeLabel }}</span>
        <SafetyBadge :status="resource.safety_status || 'pending'" :warnings="resource.warnings" />
      </div>
    </template>
    <MarkdownRenderer v-if="isMarkdown" :content="displayContent" />
    <MermaidRenderer v-else-if="resource.resource_type === 'mindmap'" :code="displayContent" />
    <pre v-else style="white-space:pre-wrap;font-size:14px">{{ displayContent }}</pre>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import MermaidRenderer from './MermaidRenderer.vue'
import SafetyBadge from './SafetyBadge.vue'

const props = defineProps<{ resource: any }>()

const TYPE_LABELS: Record<string, string> = {
  lecture: '个性化讲解', mindmap: '知识思维导图', exercise: '分层练习题',
  case: '实操案例', extended_reading: '拓展阅读', video_storyboard: '视频分镜脚本',
}
const typeLabel = computed(() => TYPE_LABELS[props.resource.resource_type] || props.resource.resource_type)
const isMarkdown = computed(() => props.resource.content_format === 'markdown' || props.resource.resource_type === 'lecture')

const displayContent = computed(() => {
  const c = props.resource.content
  if (typeof c === 'string') {
    try { return JSON.stringify(JSON.parse(c), null, 2) } catch { return c }
  }
  return JSON.stringify(c, null, 2)
})
</script>

<style scoped>
.resource-card { margin-bottom: 16px; }
</style>
