<template>
  <div :class="['card exercise-card', { answered: !!result }]">
    <div class="card-body">
      <div class="exercise-header">
        <span class="exercise-num">{{ index }}</span>
        <div class="exercise-tags">
          <el-tag size="small" effect="light" round
                  :type="exercise.difficulty === 'hard' ? 'danger' : exercise.difficulty === 'easy' ? 'success' : 'warning'">
            {{ diffLabel[exercise.difficulty] || exercise.difficulty }}
          </el-tag>
          <el-tag size="small" effect="light" round type="info">
            {{ typeLabel[exercise.question_type] || exercise.question_type }}
          </el-tag>
        </div>
      </div>

      <p class="exercise-question">{{ exercise.question }}</p>

      <div v-if="exercise.options && !result" class="options-list">
        <label v-for="opt in exercise.options" :key="opt"
               :class="['option-item', { selected: answer === opt.charAt(0) }]"
               @click="answer = opt.charAt(0)">
          <span class="option-radio">
            <span v-if="answer === opt.charAt(0)" class="radio-dot"></span>
          </span>
          <span>{{ opt }}</span>
        </label>
      </div>
      <el-input v-else-if="!result" v-model="answer" type="textarea" :rows="3"
                placeholder="请输入你的答案" style="margin-top:12px" />

      <div v-if="result" class="result-area">
        <div :class="['result-badge', result.evaluation?.is_correct ? 'correct' : 'wrong']">
          <el-icon :size="18">
            <SuccessFilled v-if="result.evaluation?.is_correct" />
            <CircleCloseFilled v-else />
          </el-icon>
          <span>{{ result.evaluation?.is_correct ? '回答正确' : '回答错误' }}</span>
        </div>
        <p v-if="result.evaluation?.feedback" class="result-feedback">{{ result.evaluation.feedback }}</p>
        <div v-if="result.evaluation?.mistake_tags?.length" class="result-tags">
          <span class="tags-label">错误标签:</span>
          <el-tag v-for="tag in result.evaluation.mistake_tags" :key="tag"
                  type="danger" size="small" effect="light" round>{{ tag }}</el-tag>
        </div>
        <div v-if="result.reflection?.change_reason" class="profile-update">
          <el-icon style="color:var(--ep-primary);flex-shrink:0"><InfoFilled /></el-icon>
          <span>画像已更新: {{ result.reflection.change_reason }}</span>
        </div>
      </div>

      <el-button v-if="!result" type="primary" :disabled="!answer" @click="$emit('submit', exercise.id, answer)"
                 style="margin-top:16px" round>
        提交答案
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { SuccessFilled, CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue'

defineProps<{ exercise: any; index?: number; result?: any }>()
defineEmits<{ submit: [exerciseId: number, answer: string] }>()

const answer = ref('')

const diffLabel: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
const typeLabel: Record<string, string> = {
  choice: '选择题', multi_choice: '多选题', fill_blank: '填空题',
  short_answer: '简答题', code: '编程题',
}
</script>

<style scoped>
.exercise-card.answered {
  border-color: var(--ep-border) !important;
}

.exercise-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.exercise-num {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--ep-primary-light);
  color: var(--ep-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
}

.exercise-tags {
  display: flex;
  gap: 6px;
}

.exercise-question {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.7;
  margin: 0 0 16px;
  color: var(--ep-text-primary);
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid var(--ep-border-light);
  border-radius: var(--ep-radius-md);
  cursor: pointer;
  transition: all var(--ep-transition);
  font-size: 14px;
  color: var(--ep-text-primary);
}

.option-item:hover {
  border-color: var(--ep-primary);
  background: var(--ep-primary-light);
}

.option-item.selected {
  border-color: var(--ep-primary);
  background: var(--ep-primary-light);
}

.option-radio {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid var(--ep-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: border-color var(--ep-transition);
}

.option-item.selected .option-radio {
  border-color: var(--ep-primary);
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ep-primary);
}

.result-area {
  margin-top: 16px;
  padding: 16px;
  background: var(--ep-bg-hover);
  border-radius: var(--ep-radius-md);
}

.result-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
}

.result-badge.correct { color: var(--ep-success); }
.result-badge.wrong { color: var(--ep-danger); }

.result-feedback {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--ep-text-secondary);
  line-height: 1.6;
}

.result-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.tags-label {
  font-size: 12px;
  color: var(--ep-text-muted);
}

.profile-update {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 14px;
  background: var(--ep-primary-light);
  border-radius: var(--ep-radius-sm);
  font-size: 13px;
  color: var(--ep-primary);
}
</style>
