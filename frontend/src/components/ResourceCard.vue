<template>
  <div class="resource-content">
    <div class="resource-header">
      <span class="resource-type">{{ typeLabel }}</span>
      <SafetyBadge :status="resource.safety_status || 'pending'" :warnings="resource.warnings" />
    </div>

    <MarkdownRenderer v-if="resource.resource_type === 'lecture'" :content="textContent" />

    <MermaidRenderer v-else-if="resource.resource_type === 'mindmap'" :code="textContent" />

    <div v-else-if="resource.resource_type === 'exercise'" class="exercise-list">
      <div v-for="(q, i) in exerciseList" :key="i" class="gen-exercise">
        <div class="gen-exercise-header">
          <span class="gen-exercise-num">{{ i + 1 }}</span>
          <el-tag size="small" effect="light" round
                  :type="q.difficulty === 'hard' ? 'danger' : q.difficulty === 'easy' ? 'success' : 'warning'">
            {{ q.difficulty || '中等' }}
          </el-tag>
          <el-tag size="small" effect="light" round type="info">{{ typeMap[q.question_type] || q.question_type }}</el-tag>
        </div>
        <p class="gen-exercise-question">{{ q.question }}</p>
        <div v-if="q.options" class="gen-options">
          <div v-for="opt in q.options" :key="opt" class="gen-option">{{ opt }}</div>
        </div>
        <el-collapse>
          <el-collapse-item title="查看答案与解析">
            <p><strong>答案：</strong>{{ q.answer }}</p>
            <p v-if="q.explanation"><strong>解析：</strong>{{ q.explanation }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <div v-else-if="resource.resource_type === 'case'" class="case-content">
      <h4 class="case-title">{{ caseData.title }}</h4>
      <p class="case-desc">{{ caseData.description }}</p>
      <MarkdownRenderer v-if="caseData.code" :content="'```python\n' + caseData.code + '\n```'" />
      <div v-if="caseData.expected_output" class="case-output">
        <strong>预期输出：</strong><code>{{ caseData.expected_output }}</code>
      </div>
    </div>

    <div v-else-if="resource.resource_type === 'extended_reading'" class="reading-list">
      <div v-for="(item, i) in readingList" :key="i" class="reading-item card">
        <div class="card-body">
          <h4 class="reading-title">{{ item.title }}</h4>
          <p class="reading-summary">{{ item.summary }}</p>
          <div class="reading-meta">
            <span v-if="item.source" class="meta-item">
              <el-icon><Reading /></el-icon> {{ item.source }}
            </span>
            <span v-if="item.relevance" class="meta-item relevance">
              <el-icon><Connection /></el-icon> {{ item.relevance }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="resource.resource_type === 'video_storyboard'" class="storyboard-content">
      <h4 class="storyboard-title">{{ storyboard.title }}</h4>
      <StoryboardPreview v-if="storyboard.scenes?.length" :scenes="storyboard.scenes" />
      <div v-if="storyboard.ppt_outline?.length" class="ppt-section">
        <h4 class="section-title">PPT 大纲</h4>
        <ol class="ppt-list">
          <li v-for="(slide, i) in storyboard.ppt_outline" :key="i">{{ slide }}</li>
        </ol>
      </div>
    </div>

    <pre v-else class="fallback-text">{{ textContent }}</pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Reading, Connection } from '@element-plus/icons-vue'
import MarkdownRenderer from './MarkdownRenderer.vue'
import MermaidRenderer from './MermaidRenderer.vue'
import SafetyBadge from './SafetyBadge.vue'
import StoryboardPreview from './StoryboardPreview.vue'

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
.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--ep-border-light);
}

.resource-type {
  font-weight: 600;
  font-size: 16px;
  color: var(--ep-text-primary);
}

.gen-exercise {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--ep-border-light);
}
.gen-exercise:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }

.gen-exercise-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.gen-exercise-num {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: var(--ep-primary-light);
  color: var(--ep-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.gen-exercise-question {
  font-weight: 500;
  margin: 0 0 12px;
  line-height: 1.7;
}

.gen-options {
  padding-left: 8px;
  margin-bottom: 12px;
}

.gen-option {
  padding: 6px 0;
  color: var(--ep-text-secondary);
  font-size: 14px;
}

.case-title {
  margin: 0 0 8px;
  font-size: 16px;
}

.case-desc {
  color: var(--ep-text-secondary);
  margin: 0 0 16px;
  line-height: 1.6;
}

.case-output {
  margin-top: 12px;
  padding: 10px 14px;
  background: var(--ep-success-light);
  border-radius: var(--ep-radius-sm);
  font-size: 14px;
  color: var(--ep-success);
}

.case-output code {
  background: none;
  padding: 0;
}

.reading-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reading-title {
  margin: 0 0 6px;
  font-size: 15px;
}

.reading-summary {
  color: var(--ep-text-secondary);
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.6;
}

.reading-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: var(--ep-text-muted);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item.relevance {
  color: var(--ep-primary);
}

.storyboard-title {
  margin: 0 0 16px;
  font-size: 16px;
}

.ppt-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--ep-border-light);
}

.ppt-list {
  padding-left: 20px;
  margin: 0;
}

.ppt-list li {
  padding: 4px 0;
  color: var(--ep-text-secondary);
  font-size: 14px;
}

.fallback-text {
  white-space: pre-wrap;
  font-size: 14px;
  background: var(--ep-bg-hover);
  padding: 16px;
  border-radius: var(--ep-radius-md);
  margin: 0;
}
</style>
