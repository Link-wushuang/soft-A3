<template>
  <div class="login-page">
    <div class="login-brand">
      <div class="brand-content">
        <div class="brand-logo">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <rect width="24" height="24" rx="6" fill="white"/>
            <path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="#2563eb" stroke-width="1.5" fill="none"/>
            <circle cx="12" cy="12" r="2.5" fill="#2563eb"/>
          </svg>
        </div>
        <h1 class="brand-title">EduPath</h1>
        <p class="brand-desc">基于大模型的个性化学习多智能体系统</p>
        <div class="feature-list">
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="8" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
                <path d="M7 10L9 12L13 8" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <div class="feature-title">智能学习画像</div>
              <div class="feature-desc">对话式自动构建8维学习画像</div>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="8" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
                <path d="M7 10L9 12L13 8" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <div class="feature-title">多智能体协同</div>
              <div class="feature-desc">14个专业Agent协作生成个性化资源</div>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="8" stroke="rgba(255,255,255,0.6)" stroke-width="1.5"/>
                <path d="M7 10L9 12L13 8" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <div class="feature-title">闭环学习反馈</div>
              <div class="feature-desc">练习评估 → 画像更新 → 补救推送</div>
            </div>
          </div>
        </div>
      </div>
      <div class="brand-footer">
        Powered by Multi-Agent System &amp; LLM
      </div>
    </div>

    <div class="login-form-side">
      <div class="form-wrapper">
        <h2 class="form-title">
          {{ activeTab === 'login' ? '欢迎回来' : '创建账号' }}
        </h2>
        <p class="form-subtitle">
          {{ activeTab === 'login' ? '登录你的学习账号以继续' : '注册新账号开始学习之旅' }}
        </p>

        <div class="tab-switch">
          <button :class="['tab-btn', { active: activeTab === 'login' }]" @click="activeTab = 'login'">登录</button>
          <button :class="['tab-btn', { active: activeTab === 'register' }]" @click="activeTab = 'register'">注册</button>
        </div>

        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="login-form">
          <div class="form-field">
            <label class="form-label">用户名</label>
            <el-input v-model="username" placeholder="请输入用户名" size="large" />
          </div>
          <div class="form-field">
            <label class="form-label">密码</label>
            <el-input v-model="password" type="password" placeholder="请输入密码" show-password size="large" />
          </div>
          <el-button type="primary" native-type="submit" size="large" :loading="loading" class="submit-btn">
            登录
          </el-button>
          <div class="divider">
            <span>或</span>
          </div>
          <el-button size="large" class="demo-btn" @click="demoLogin('student')">
            演示学生账号登录
          </el-button>
          <el-button size="large" class="demo-btn teacher" @click="demoLogin('teacher')">
            演示教师账号登录
          </el-button>
        </form>

        <form v-else @submit.prevent="handleRegister" class="login-form">
          <div class="form-field">
            <label class="form-label">用户名</label>
            <el-input v-model="regUsername" placeholder="请输入用户名" size="large" />
          </div>
          <div class="form-field">
            <label class="form-label">显示名称</label>
            <el-input v-model="regDisplayName" placeholder="请输入显示名称" size="large" />
          </div>
          <div class="form-field">
            <label class="form-label">密码</label>
            <el-input v-model="regPassword" type="password" placeholder="至少6位密码" show-password size="large" />
          </div>
          <el-button type="primary" native-type="submit" size="large" :loading="loading" class="submit-btn">
            注册
          </el-button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import api from '../api/index'

const router = useRouter()
const auth = useAuthStore()
const activeTab = ref('login')
const username = ref('')
const password = ref('')
const regUsername = ref('')
const regDisplayName = ref('')
const regPassword = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    const dest = auth.user?.role === 'teacher' ? '/teacher/knowledge' : '/student/dashboard'
    router.push(dest)
  } catch {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!regUsername.value || !regPassword.value) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  if (regPassword.value.length < 6) {
    ElMessage.warning('密码至少需要6位')
    return
  }
  loading.value = true
  try {
    const res = await api.post('/auth/register', {
      username: regUsername.value,
      password: regPassword.value,
      display_name: regDisplayName.value || regUsername.value,
    })
    localStorage.setItem('token', res.data.access_token)
    auth.token = res.data.access_token
    ElMessage.success('注册成功')
    router.push('/student/dashboard')
  } catch {
    ElMessage.error('注册失败，用户名可能已存在')
  } finally {
    loading.value = false
  }
}

async function demoLogin(role: string) {
  username.value = role === 'teacher' ? 'demo_teacher' : 'demo_student'
  password.value = 'demo123456'
  await handleLogin()
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
}

.login-brand {
  flex: 1;
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #7c3aed 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
}

.login-brand::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 30% 40%, rgba(255,255,255,0.08) 0%, transparent 50%),
              radial-gradient(circle at 70% 80%, rgba(255,255,255,0.05) 0%, transparent 40%);
  pointer-events: none;
}

.brand-content {
  position: relative;
  z-index: 1;
  max-width: 440px;
}

.brand-logo {
  margin-bottom: 24px;
}

.brand-title {
  font-size: 42px;
  font-weight: 800;
  color: white;
  margin: 0 0 12px;
  letter-spacing: -0.03em;
}

.brand-desc {
  font-size: 17px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 48px;
  line-height: 1.6;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.feature-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.feature-title {
  font-size: 15px;
  font-weight: 600;
  color: white;
  margin-bottom: 3px;
}

.feature-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.65);
}

.brand-footer {
  position: absolute;
  bottom: 32px;
  left: 60px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  z-index: 1;
}

.login-form-side {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
}

.form-wrapper {
  width: 100%;
  max-width: 380px;
}

.form-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--ep-text-primary);
  margin: 0 0 8px;
}

.form-subtitle {
  font-size: 14px;
  color: var(--ep-text-secondary);
  margin: 0 0 28px;
}

.tab-switch {
  display: flex;
  background: var(--ep-bg);
  border-radius: var(--ep-radius-sm);
  padding: 3px;
  margin-bottom: 28px;
}

.tab-btn {
  flex: 1;
  padding: 8px 0;
  border: none;
  background: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  color: var(--ep-text-secondary);
  cursor: pointer;
  transition: all var(--ep-transition);
}

.tab-btn.active {
  background: white;
  color: var(--ep-text-primary);
  box-shadow: var(--ep-shadow-xs);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-field {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--ep-text-primary);
  margin-bottom: 6px;
}

.submit-btn {
  width: 100%;
  margin-top: 8px;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--ep-radius-sm) !important;
}

.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  color: var(--ep-text-muted);
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--ep-border);
}

.demo-btn {
  width: 100%;
  height: 42px;
  border-radius: var(--ep-radius-sm) !important;
  font-weight: 500;
}

.demo-btn.teacher {
  margin-top: 8px;
}
</style>
