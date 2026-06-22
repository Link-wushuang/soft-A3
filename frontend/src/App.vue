<template>
  <div v-if="showLayout" class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="url(#logo-grad)"/>
            <path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="1.6" fill="none"/>
            <circle cx="14" cy="14" r="3" fill="white" opacity="0.9"/>
            <defs><linearGradient id="logo-grad" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>
          </svg>
        </div>
        <span class="brand-text">EduPath</span>
      </div>
      <div class="sidebar-label">{{ isTeacher ? '教师面板' : '学习中心' }}</div>
      <nav class="sidebar-nav">
        <template v-if="isTeacher">
          <router-link to="/teacher/knowledge" class="nav-item" active-class="active"><div class="nav-icon-wrap"><el-icon :size="18"><Document /></el-icon></div><span>知识点管理</span></router-link>
          <router-link to="/teacher/analytics" class="nav-item" active-class="active"><div class="nav-icon-wrap"><el-icon :size="18"><DataAnalysis /></el-icon></div><span>数据分析</span></router-link>
        </template>
        <template v-else>
          <router-link to="/student/dashboard" class="nav-item" active-class="active"><div class="nav-icon-wrap"><el-icon :size="18"><Monitor /></el-icon></div><span>学习仪表盘</span></router-link>
          <router-link to="/student/profile-chat" class="nav-item" active-class="active"><div class="nav-icon-wrap"><el-icon :size="18"><ChatDotRound /></el-icon></div><span>对话建档</span></router-link>
          <router-link to="/student/learning-path" class="nav-item" active-class="active"><div class="nav-icon-wrap"><el-icon :size="18"><Guide /></el-icon></div><span>学习路径</span></router-link>
          <router-link to="/student/tutor" class="nav-item" active-class="active"><div class="nav-icon-wrap"><el-icon :size="18"><ChatDotSquare /></el-icon></div><span>智能答疑</span></router-link>
        </template>
      </nav>
      <div class="sidebar-footer">
        <div class="user-block">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <div class="user-name">{{ auth.user?.display_name || auth.user?.username || '用户' }}</div>
            <div class="user-role"><span class="role-dot" :class="isTeacher ? 'teacher' : 'student'" />{{ isTeacher ? '教师' : '学生' }}</div>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录"><el-icon :size="18"><SwitchButton /></el-icon></button>
      </div>
    </aside>
    <main class="main-content"><router-view /></main>
  </div>
  <router-view v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { Monitor, ChatDotRound, ChatDotSquare, Guide, Document, DataAnalysis, SwitchButton } from '@element-plus/icons-vue'
const route = useRoute(); const router = useRouter(); const auth = useAuthStore()
const showLayout = computed(() => route.path !== '/login' && route.path !== '/')
const isTeacher = computed(() => auth.user?.role === 'teacher')
const userInitial = computed(() => { const n = auth.user?.display_name || auth.user?.username || '?'; return n.charAt(0).toUpperCase() })
function handleLogout() { auth.logout(); router.push('/login') }
</script>

<style scoped>
.app-layout { display: flex; min-height: 100vh; }
.sidebar { width: var(--ep-sidebar-width); background: var(--ep-sidebar-bg); display: flex; flex-direction: column; position: fixed; top: 0; left: 0; bottom: 0; z-index: 100; overflow-y: auto; border-right: 1px solid rgba(255,255,255,0.04); }
.main-content { flex: 1; margin-left: var(--ep-sidebar-width); min-height: 100vh; background: var(--ep-bg); }
.sidebar-brand { display: flex; align-items: center; gap: 11px; padding: 24px 20px 20px; }
.brand-icon { display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.brand-text { font-size: 19px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.02em; }
.sidebar-label { padding: 6px 20px 16px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: #818cf8; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.sidebar-label::before { content: ''; width: 3px; height: 14px; border-radius: 2px; background: linear-gradient(180deg, #6366f1, #818cf8); flex-shrink: 0; }
.sidebar-nav { flex: 1; padding: 0 12px; display: flex; flex-direction: column; gap: 2px; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: var(--ep-sidebar-text); text-decoration: none; font-size: 13px; font-weight: 500; transition: all var(--ep-transition); position: relative; }
.nav-item:hover { background: var(--ep-sidebar-hover); color: #cbd5e1; }
.nav-item.active { background: var(--ep-sidebar-active); color: #e2e8f0; }
.nav-item.active::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 20px; border-radius: 0 3px 3px 0; background: #818cf8; }
.nav-icon-wrap { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; background: rgba(255,255,255,0.04); transition: background var(--ep-transition); }
.nav-item.active .nav-icon-wrap { background: rgba(99,102,241,0.2); }
.nav-item.active .nav-icon-wrap :deep(.el-icon) { color: #a5b4fc; }
.sidebar-footer { padding: 16px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.user-block { display: flex; align-items: center; gap: 10px; min-width: 0; }
.user-avatar { width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 14px; flex-shrink: 0; }
.user-info { min-width: 0; }
.user-name { color: #e2e8f0; font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { color: var(--ep-sidebar-text); font-size: 11px; margin-top: 2px; display: flex; align-items: center; gap: 5px; }
.role-dot { width: 6px; height: 6px; border-radius: 50%; background: #64748b; }
.role-dot.teacher { background: #f59e0b; }
.role-dot.student { background: #10b981; }
.logout-btn { background: none; border: none; color: #64748b; cursor: pointer; padding: 8px; border-radius: 8px; transition: all var(--ep-transition); display: flex; align-items: center; justify-content: center; }
.logout-btn:hover { background: rgba(239,68,68,0.1); color: #ef4444; }
</style>
