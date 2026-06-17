<template>
  <div>
    <el-menu v-if="showNav" mode="horizontal" :default-active="route.path" router
             style="padding:0 24px" :ellipsis="false">
      <el-menu-item style="font-weight:700;font-size:16px;pointer-events:none">
        EduPath
      </el-menu-item>
      <template v-if="isTeacher">
        <el-menu-item index="/teacher/knowledge">知识点管理</el-menu-item>
        <el-menu-item index="/teacher/analytics">数据分析</el-menu-item>
      </template>
      <template v-else>
        <el-menu-item index="/student/dashboard">仪表盘</el-menu-item>
        <el-menu-item index="/student/profile-chat">学习建档</el-menu-item>
        <el-menu-item index="/student/learning-path">学习路径</el-menu-item>
      </template>
      <div style="flex:1" />
      <el-menu-item @click="handleLogout">
        <span style="color:#909399">退出登录</span>
      </el-menu-item>
    </el-menu>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const showNav = computed(() => route.path !== '/login' && route.path !== '/')
const isTeacher = computed(() => auth.user?.role === 'teacher')

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
