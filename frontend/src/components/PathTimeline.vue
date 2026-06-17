<template>
  <el-timeline>
    <el-timeline-item v-for="node in nodes" :key="node.id"
      :type="node.status === 'completed' ? 'success' : node.status === 'in_progress' ? 'primary' : 'info'"
      :hollow="node.status === 'pending'">
      <el-card shadow="hover" style="cursor:pointer" @click="$emit('nodeClick', node)">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <strong>{{ node.knowledge_point_title || node.title }}</strong>
            <p style="margin:4px 0 0;color:#909399;font-size:13px">{{ node.reason }}</p>
          </div>
          <el-tag :type="node.status === 'completed' ? 'success' : 'info'" size="small">{{ node.status }}</el-tag>
        </div>
      </el-card>
    </el-timeline-item>
  </el-timeline>
</template>

<script setup lang="ts">
defineProps<{ nodes: Array<{ id: number; knowledge_point_title?: string; title?: string; status: string; reason: string }> }>()
defineEmits<{ nodeClick: [node: any] }>()
</script>
