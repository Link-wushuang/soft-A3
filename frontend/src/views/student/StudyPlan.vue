<template>
  <div class="page-container" style="max-width:1200px">
    <div class="page-header">
      <div><h1 class="page-title">学习计划</h1><p class="page-subtitle">制定和管理你的学习计划</p></div>
      <el-button @click="$router.back()" round><el-icon style="margin-right:6px"><Back /></el-icon>返回</el-button>
    </div>
    <div class="card">
      <div class="card-body" style="min-height:400px">
        <TimeDetail @open-plan="() => {}" />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Back } from '@element-plus/icons-vue'
import TimeDetail from './details/TimeDetail.vue'
</script>
