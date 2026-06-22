<template>
  <div class="page-container" style="max-width:1200px">
    <div class="page-header">
      <div><h1 class="page-title">学习记录</h1><p class="page-subtitle">你的知识点学习历程与时间线</p></div>
      <el-button @click="$router.back()" round><el-icon style="margin-right:6px"><Back /></el-icon>返回</el-button>
    </div>
    <div class="card">
      <div class="card-body" style="min-height:400px">
        <LearnedDetail />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { Back } from '@element-plus/icons-vue'
import LearnedDetail from './details/LearnedDetail.vue'
</script>
