<template>
  <div class="login-page">
    <div class="bg-layer">
      <div class="bg-orb orb-1" /><div class="bg-orb orb-2" /><div class="bg-orb orb-3" />
      <div class="bg-grid" />
    </div>
    <div class="login-container">
      <section class="brand-panel">
        <div class="brand-content">
          <div class="brand-badge">EduPath Agent</div>
          <h1 class="brand-title">让每个人<br/>拥有专属学习路径</h1>
          <p class="brand-desc">基于大模型的多智能体协同系统，通过对话式画像、个性化路径规划和多模态资源生成，为你打造真正适配的学习体验。</p>
          <div class="feature-list">
            <div class="feature-item"><div class="feature-dot" /><span>8 维对话式学习画像，实时动态更新</span></div>
            <div class="feature-item"><div class="feature-dot" /><span>14 个专业 Agent 协同，生成 6 类学习资源</span></div>
            <div class="feature-item"><div class="feature-dot" /><span>练习自动评估 → 画像反思 → 补救推荐闭环</span></div>
          </div>
        </div>
        <div class="brand-footer"><span>Powered by Multi-Agent System &amp; LLM</span><span class="footer-dot" /><span>操作系统课程知识库</span></div>
      </section>
      <section class="form-panel">
        <div class="form-card">
          <div class="form-header">
            <h2 class="form-title">{{ activeTab === 'login' ? '欢迎回来' : '创建账号' }}</h2>
            <p class="form-subtitle">{{ activeTab === 'login' ? '登录你的学习账号以继续' : '注册新账号开始学习之旅' }}</p>
          </div>
          <div class="tab-row">
            <button :class="['tab-btn', { active: activeTab === 'login' }]" @click="activeTab = 'login'">登录</button>
            <button :class="['tab-btn', { active: activeTab === 'register' }]" @click="activeTab = 'register'">注册</button>
          </div>
          <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="login-form">
            <div class="input-group"><label class="input-label">用户名</label><div class="input-wrap"><el-icon class="input-icon"><User /></el-icon><el-input v-model="username" placeholder="请输入用户名" size="large" class="no-border" /></div></div>
            <div class="input-group"><label class="input-label">密码</label><div class="input-wrap"><el-icon class="input-icon"><Lock /></el-icon><el-input v-model="password" type="password" placeholder="请输入密码" show-password size="large" class="no-border" /></div></div>
            <el-button type="primary" native-type="submit" size="large" :loading="loading" class="submit-btn">登录</el-button>
            <div class="divider"><span>快速体验</span></div>
            <div class="demo-btns">
              <button type="button" class="demo-btn student" @click="demoLogin('student')"><el-icon><User /></el-icon>学生演示账号</button>
              <button type="button" class="demo-btn teacher" @click="demoLogin('teacher')"><el-icon><DataAnalysis /></el-icon>教师演示账号</button>
            </div>
          </form>
          <form v-else @submit.prevent="handleRegister" class="login-form">
            <div class="input-group"><label class="input-label">用户名</label><div class="input-wrap"><el-icon class="input-icon"><User /></el-icon><el-input v-model="regUsername" placeholder="请输入用户名" size="large" class="no-border" /></div></div>
            <div class="input-group"><label class="input-label">显示名称</label><div class="input-wrap"><el-icon class="input-icon"><EditPen /></el-icon><el-input v-model="regDisplayName" placeholder="请输入显示名称" size="large" class="no-border" /></div></div>
            <div class="input-group"><label class="input-label">密码</label><div class="input-wrap"><el-icon class="input-icon"><Lock /></el-icon><el-input v-model="regPassword" type="password" placeholder="至少6位密码" show-password size="large" class="no-border" /></div></div>
            <el-button type="primary" native-type="submit" size="large" :loading="loading" class="submit-btn">注册</el-button>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock, EditPen, DataAnalysis } from '@element-plus/icons-vue'
import api from '../api/index'

const router = useRouter()
const auth = useAuthStore()
const activeTab = ref('login')
const username = ref(''); const password = ref('')
const regUsername = ref(''); const regDisplayName = ref(''); const regPassword = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) { ElMessage.warning('请输入用户名和密码'); return }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push(auth.user?.role === 'teacher' ? '/teacher/knowledge' : '/student/dashboard')
  } catch { ElMessage.error('登录失败，请检查用户名和密码') }
  finally { loading.value = false }
}

async function handleRegister() {
  if (!regUsername.value || !regPassword.value) { ElMessage.warning('请填写用户名和密码'); return }
  if (regPassword.value.length < 6) { ElMessage.warning('密码至少需要6位'); return }
  loading.value = true
  try {
    const res = await api.post('/auth/register', { username: regUsername.value, password: regPassword.value, display_name: regDisplayName.value || regUsername.value })
    localStorage.setItem('token', res.data.access_token); auth.token = res.data.access_token
    ElMessage.success('注册成功'); router.push('/student/dashboard')
  } catch { ElMessage.error('注册失败，用户名可能已存在') }
  finally { loading.value = false }
}

async function demoLogin(role: string) {
  username.value = role === 'teacher' ? 'demo_teacher' : 'demo_student'
  password.value = role === 'teacher' ? 'teacher123456' : 'demo123456'
  await handleLogin()
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; background: #0f172a; }
.login-container { position: relative; z-index: 2; display: flex; width: 960px; min-height: 620px; border-radius: var(--ep-radius-xl); overflow: hidden; box-shadow: 0 25px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.06); }
.bg-layer { position: absolute; inset: 0; z-index: 0; }
.bg-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 60px 60px; mask-image: radial-gradient(ellipse 80% 60% at 50% 40%, black 30%, transparent 70%); }
.bg-orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.12; animation: orbFloat 20s ease-in-out infinite; }
.orb-1 { width: 500px; height: 500px; background: #4f46e5; top: -20%; right: -10%; }
.orb-2 { width: 400px; height: 400px; background: #8b5cf6; bottom: -15%; left: -8%; animation-delay: -7s; }
.orb-3 { width: 300px; height: 300px; background: #ec4899; top: 40%; left: 40%; animation-delay: -13s; }
@keyframes orbFloat { 0%,100% { transform: translate(0,0) scale(1); } 25% { transform: translate(30px,-20px) scale(1.05); } 50% { transform: translate(-15px,25px) scale(0.95); } 75% { transform: translate(-25px,-10px) scale(1.02); } }
.brand-panel { flex: 1; background: linear-gradient(135deg, rgba(15,23,42,0.92) 0%, rgba(30,27,75,0.9) 100%); backdrop-filter: blur(20px); display: flex; flex-direction: column; justify-content: center; padding: 56px 52px; }
.brand-content { max-width: 380px; }
.brand-badge { display: inline-block; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; letter-spacing: 0.04em; color: #a5b4fc; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.25); margin-bottom: 28px; }
.brand-title { font-size: 34px; font-weight: 800; color: #f1f5f9; margin: 0 0 20px; letter-spacing: -0.03em; line-height: 1.25; }
.brand-desc { font-size: 14px; color: #94a3b8; margin: 0 0 40px; line-height: 1.7; }
.feature-list { display: flex; flex-direction: column; gap: 16px; }
.feature-item { display: flex; align-items: center; gap: 12px; font-size: 13px; color: #cbd5e1; }
.feature-dot { width: 6px; height: 6px; border-radius: 50%; background: #6366f1; flex-shrink: 0; box-shadow: 0 0 8px rgba(99,102,241,0.5); }
.brand-footer { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #64748b; margin-top: auto; padding-top: 40px; }
.footer-dot { width: 3px; height: 3px; border-radius: 50%; background: #475569; }
.form-panel { width: 460px; background: rgba(255,255,255,0.97); backdrop-filter: blur(12px); display: flex; align-items: center; justify-content: center; padding: 48px 44px; }
.form-card { width: 100%; max-width: 340px; }
.form-header { margin-bottom: 28px; }
.form-title { font-size: 24px; font-weight: 700; color: var(--ep-text-primary); margin: 0 0 6px; letter-spacing: -0.02em; }
.form-subtitle { font-size: 13px; color: var(--ep-text-secondary); margin: 0; }
.tab-row { display: flex; background: #f1f5f9; border-radius: 10px; padding: 4px; margin-bottom: 28px; }
.tab-btn { flex: 1; padding: 9px 0; border: none; background: none; border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--ep-text-secondary); cursor: pointer; transition: all var(--ep-transition); }
.tab-btn.active { background: white; color: var(--ep-text-primary); box-shadow: 0 1px 3px rgba(15,23,42,0.08), 0 1px 2px rgba(15,23,42,0.04); }
.login-form { display: flex; flex-direction: column; }
.input-group { margin-bottom: 18px; }
.input-label { display: block; font-size: 12px; font-weight: 600; color: var(--ep-text-secondary); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.04em; }
.input-wrap { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 14px; z-index: 10; font-size: 16px; color: var(--ep-text-muted); pointer-events: none; }
.input-wrap :deep(.el-input__inner) { padding-left: 42px !important; height: 46px !important; border-radius: 10px !important; border-color: var(--ep-border) !important; font-size: 14px !important; background: #f8fafc !important; transition: all var(--ep-transition) !important; }
.input-wrap :deep(.el-input__inner):focus { border-color: var(--ep-primary) !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important; background: white !important; }
.submit-btn { width: 100%; height: 46px; margin-top: 6px; font-size: 14px; font-weight: 600; border-radius: 10px !important; letter-spacing: 0.01em; background: linear-gradient(135deg, #4f46e5, #6366f1) !important; border: none !important; transition: all var(--ep-transition) !important; }
.submit-btn:hover { box-shadow: 0 4px 14px rgba(79,70,229,0.4) !important; transform: translateY(-1px); }
.divider { display: flex; align-items: center; gap: 14px; margin: 20px 0; color: var(--ep-text-muted); font-size: 12px; }
.divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: var(--ep-border); }
.demo-btns { display: flex; gap: 10px; }
.demo-btn { flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 11px 0; border: 1px solid var(--ep-border); border-radius: 10px; background: white; font-size: 12px; font-weight: 500; color: var(--ep-text-secondary); cursor: pointer; transition: all var(--ep-transition); }
.demo-btn:hover { border-color: var(--ep-primary); color: var(--ep-primary); background: var(--ep-primary-light); }
.demo-btn .el-icon { font-size: 14px; }
</style>
