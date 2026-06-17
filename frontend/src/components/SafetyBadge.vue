<template>
  <el-tag :type="tagType" size="small">{{ label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string; warnings?: string[] }>()

const tagType = computed(() => {
  if (props.warnings && props.warnings.length > 0) return 'warning'
  if (props.status === 'passed') return 'success'
  if (props.status === 'blocked') return 'danger'
  return 'info'
})

const label = computed(() => {
  if (props.status === 'blocked') return '已过滤'
  if (props.warnings && props.warnings.length > 0) return '有警告'
  return '已验证'
})
</script>
