<template>
  <div v-if="showLayout" class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect width="24" height="24" rx="6" fill="#2563eb"/>
            <path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.5" fill="none"/>
            <circle cx="12" cy="12" r="2.5" fill="white"/>
          </svg>
        </div>
        <span class="brand-text">EduPath</span>
      </div>
      <div class="sidebar-label">{{ isTeacher ? '教师面板' : '学习中心' }}</div>
      <nav class="sidebar-nav">
        <template v-if="isTeacher">
          <router-link to="/teacher/knowledge" class="nav-item" active-class="active">
            <el-icon><Document /></el-icon>
            <span>知识点管理</span>
          </router-link>
          <router-link to="/teacher/analytics" class="nav-item" active-class="active">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </router-link>
        </template>
        <template v-else>
          <router-link to="/student/dashboard" class="nav-item" active-class="active">
            <el-icon><Monitor /></el-icon>
            <span>学习仪表盘</span>
          </router-link>
          <router-link to="/student/profile-chat" class="nav-item" active-class="active">
            <el-icon><ChatDotRound /></el-icon>
            <span>对话建档</span>
          </router-link>
          <router-link to="/student/learning-path" class="nav-item" active-class="active">
            <el-icon><Guide /></el-icon>
            <span>学习路径</span>
          </router-link>
        </template>
      </nav>
      <div class="sidebar-footer">
        <div class="user-block">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <div class="user-name">{{ auth.user?.display_name || auth.user?.username || '用户' }}</div>
            <div class="user-role">{{ isTeacher ? '教师' : '学生' }}</div>
          </div>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <el-icon><SwitchButton /></el-icon>
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { Monitor, ChatDotRound, Guide, Document, DataAnalysis, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const showLayout = computed(() => route.path !== '/login' && route.path !== '/')
const isTeacher = computed(() => auth.user?.role === 'teacher')
const userInitial = computed(() => {
  const name = auth.user?.display_name || auth.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--ep-sidebar-width);
  background: var(--ep-sidebar-bg);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
}

.main-content {
  flex: 1;
  margin-left: var(--ep-sidebar-width);
  min-height: 100vh;
  background: var(--ep-bg);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 22px 20px 18px;
}

.brand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.02em;
}

.sidebar-label {
  padding: 0 20px 12px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ep-sidebar-text);
  font-weight: 600;
}

.sidebar-nav {
  flex: 1;
  padding: 0 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--ep-radius-sm);
  color: var(--ep-sidebar-text);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--ep-transition);
  cursor: pointer;
}

.nav-item:hover {
  background: var(--ep-sidebar-hover);
  color: #e2e8f0;
}

.nav-item.active {
  background: var(--ep-sidebar-active);
  color: var(--ep-sidebar-text-active);
}

.nav-item .el-icon {
  font-size: 18px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.user-info {
  min-width: 0;
}

.user-name {
  color: #e2e8f0;
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  color: var(--ep-sidebar-text);
  font-size: 11px;
  margin-top: 1px;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--ep-sidebar-text);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--ep-radius-sm);
  transition: all var(--ep-transition);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn:hover {
  background: var(--ep-sidebar-hover);
  color: #ef4444;
}

.logout-btn .el-icon {
  font-size: 18px;
}
</style>
