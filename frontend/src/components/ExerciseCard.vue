<template>
  <el-card shadow="hover" style="margin-bottom:16px">
    <template #header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <span>{{ exercise.question }}</span>
        <el-tag size="small">{{ exercise.difficulty }}</el-tag>
      </div>
    </template>
    <el-radio-group v-if="exercise.options && !result" v-model="answer" style="display:block">
      <el-radio v-for="opt in exercise.options" :key="opt" :value="opt.charAt(0)" style="display:block;margin:8px 0">{{ opt }}</el-radio>
    </el-radio-group>
    <el-input v-else-if="!result" v-model="answer" type="textarea" :rows="3" placeholder="请输入答案" style="margin-top:8px" />
    <div v-if="result" style="margin-top:12px">
      <el-result :icon="result.evaluation.is_correct ? 'success' : 'error'"
        :title="result.evaluation.is_correct ? '回答正确' : '回答错误'" style="padding:8px">
        <template #sub-title>{{ result.evaluation.feedback }}</template>
      </el-result>
      <div v-if="result.evaluation.mistake_tags?.length" style="margin-top:8px">
        <span style="color:#909399;font-size:13px">错误标签: </span>
        <el-tag v-for="tag in result.evaluation.mistake_tags" :key="tag" type="danger" size="small" style="margin:2px">{{ tag }}</el-tag>
      </div>
      <el-alert v-if="result.reflection?.change_reason" type="info" show-icon :closable="false" style="margin-top:8px"
        :title="'画像更新: ' + result.reflection.change_reason" />
    </div>
    <el-button v-if="!result" type="primary" size="small" style="margin-top:12px"
      :disabled="!answer" @click="$emit('submit', exercise.id, answer)">提交答案</el-button>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ exercise: any; result?: any }>()
defineEmits<{ submit: [exerciseId: number, answer: string] }>()

const answer = ref('')
</script>
