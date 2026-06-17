<template>
  <el-card shadow="hover" class="resource-card">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>{{ typeLabel }}</span>
        <SafetyBadge :status="resource.safety_status || 'pending'" :warnings="resource.warnings" />
      </div>
    </template>

    <!-- 个性化讲解：Markdown 渲染 -->
    <MarkdownRenderer v-if="resource.resource_type === 'lecture'" :content="textContent" />

    <!-- 思维导图：Mermaid 渲染 -->
    <MermaidRenderer v-else-if="resource.resource_type === 'mindmap'" :code="textContent" />

    <!-- 练习题：结构化展示 -->
    <div v-else-if="resource.resource_type === 'exercise'">
      <div v-for="(q, i) in exerciseList" :key="i" class="exercise-item">
        <div class="exercise-header">
          <el-tag size="small" :type="q.difficulty === 'hard' ? 'danger' : q.difficulty === 'easy' ? 'success' : ''">
            {{ q.difficulty || '中等' }}
          </el-tag>
          <el-tag size="small" type="info">{{ typeMap[q.question_type] || q.question_type }}</el-tag>
        </div>
        <p class="exercise-question">{{ i + 1 }}. {{ q.question }}</p>
        <div v-if="q.options" class="exercise-options">
          <div v-for="opt in q.options" :key="opt" class="option-item">{{ opt }}</div>
        </div>
        <el-collapse>
          <el-collapse-item title="查看答案与解析">
            <p><strong>答案：</strong>{{ q.answer }}</p>
            <p v-if="q.explanation"><strong>解析：</strong>{{ q.explanation }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 实操案例：代码 + 说明 -->
    <div v-else-if="resource.resource_type === 'case'">
      <h4>{{ caseData.title }}</h4>
      <p>{{ caseData.description }}</p>
      <MarkdownRenderer v-if="caseData.code" :content="'```python\n' + caseData.code + '\n```'" />
      <p v-if="caseData.expected_output" style="color:#67c23a">
        <strong>预期输出：</strong><code>{{ caseData.expected_output }}</code>
      </p>
    </div>

    <!-- 拓展阅读：阅读列表 -->
    <div v-else-if="resource.resource_type === 'extended_reading'">
      <el-card v-for="(item, i) in readingList" :key="i" shadow="never" style="margin-bottom:12px">
        <h4 style="margin:0 0 8px">{{ item.title }}</h4>
        <p>{{ item.summary }}</p>
        <div style="display:flex;justify-content:space-between;color:#909399;font-size:13px">
          <span v-if="item.source">📖 {{ item.source }}</span>
          <span v-if="item.relevance">💡 {{ item.relevance }}</span>
        </div>
      </el-card>
    </div>

    <!-- 视频分镜：场景卡片 -->
    <div v-else-if="resource.resource_type === 'video_storyboard'">
      <h4>{{ storyboard.title }}</h4>
      <el-timeline>
        <el-timeline-item v-for="scene in storyboard.scenes || []" :key="scene.scene_id">
          <el-card shadow="never">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
              <strong>场景 {{ scene.scene_id }}</strong>
              <el-tag size="small">{{ scene.duration_sec }}秒</el-tag>
            </div>
            <p><strong>画面：</strong>{{ scene.visual }}</p>
            <p><strong>旁白：</strong>{{ scene.narration }}</p>
            <p v-if="scene.animation" style="color:#909399"><strong>动画：</strong>{{ scene.animation }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <div v-if="storyboard.ppt_outline?.length" style="margin-top:12px">
        <h4>PPT 大纲</h4>
        <ol>
          <li v-for="(slide, i) in storyboard.ppt_outline" :key="i">{{ slide }}</li>
        </ol>
      </div>
    </div>

    <!-- 兜底：纯文本 -->
    <pre v-else style="white-space:pre-wrap;font-size:14px">{{ textContent }}</pre>
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
const typeMap: Record<string, string> = {
  choice: '选择题', fill_blank: '填空题', short_answer: '简答题',
}

const typeLabel = computed(() => TYPE_LABELS[props.resource.resource_type] || props.resource.resource_type)

const parsed = computed(() => {
  const c = props.resource.content
  if (typeof c === 'string') {
    try { return JSON.parse(c) } catch { return c }
  }
  return c
})

const textContent = computed(() => {
  const p = parsed.value
  if (typeof p === 'string') return p
  if (p && typeof p === 'object' && 'content' in p) return p.content
  return JSON.stringify(p, null, 2)
})

const exerciseList = computed(() => {
  const p = parsed.value
  if (Array.isArray(p)) return p
  if (p && typeof p === 'object' && 'content' in p) {
    try { return JSON.parse(p.content) } catch { /* not nested */ }
  }
  return []
})

const caseData = computed(() => {
  const p = parsed.value
  if (p && typeof p === 'object' && !Array.isArray(p)) {
    if ('title' in p) return p
    if ('content' in p && typeof p.content === 'object') return p.content
  }
  return {}
})

const readingList = computed(() => {
  const p = parsed.value
  if (Array.isArray(p)) return p
  if (p && typeof p === 'object' && 'content' in p && Array.isArray(p.content)) return p.content
  return []
})

const storyboard = computed(() => {
  const p = parsed.value
  if (p && typeof p === 'object' && !Array.isArray(p)) {
    if ('scenes' in p) return p
    if ('content' in p && typeof p.content === 'object') return p.content
  }
  return {}
})
</script>

<style scoped>
.resource-card { margin-bottom: 16px; }
.exercise-item { margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #ebeef5; }
.exercise-item:last-child { border-bottom: none; }
.exercise-header { display: flex; gap: 8px; margin-bottom: 8px; }
.exercise-question { font-weight: 500; margin: 8px 0; }
.exercise-options { padding-left: 16px; }
.option-item { padding: 4px 0; color: #606266; }
</style>
