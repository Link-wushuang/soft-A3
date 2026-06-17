<template>
  <el-card class="profile-card">
    <template #header><span>学生画像 ({{ profile.confidence || '未知' }}置信度)</span></template>
    <el-row :gutter="16">
      <el-col :span="12" v-for="dim in dimensions" :key="dim.key">
        <div class="dim-item">
          <div class="dim-label">{{ dim.label }}</div>
          <div class="dim-value">
            <template v-if="Array.isArray(profile[dim.key])">
              <el-tag v-for="tag in profile[dim.key]" :key="tag" size="small" style="margin:2px">{{ tag }}</el-tag>
            </template>
            <template v-else>{{ profile[dim.key] || '—' }}</template>
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{ profile: Record<string, any> }>()

const dimensions = [
  { key: 'base_level', label: '基础水平' },
  { key: 'learning_goal', label: '学习目标' },
  { key: 'knowledge_state', label: '知识状态' },
  { key: 'weak_points', label: '薄弱知识点' },
  { key: 'mastered_points', label: '已掌握知识点' },
  { key: 'learning_preference', label: '学习偏好' },
  { key: 'cognitive_style', label: '认知风格' },
  { key: 'time_budget', label: '时间预算' },
]
</script>

<style scoped>
.profile-card { margin-bottom: 16px; }
.dim-item { margin-bottom: 12px; }
.dim-label { font-weight: 600; color: #606266; margin-bottom: 4px; font-size: 13px; }
.dim-value { font-size: 14px; }
</style>
