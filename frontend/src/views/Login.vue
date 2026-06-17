<template>
  <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f0f2f5">
    <el-card style="width:420px">
      <template #header><h2 style="margin:0;text-align:center">EduPath 个性化学习系统</h2></template>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login">
          <el-form @submit.prevent="handleLogin">
            <el-form-item label="用户名">
              <el-input v-model="username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="password" type="password" placeholder="请输入密码" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" style="width:100%" :loading="loading">登录</el-button>
            </el-form-item>
            <el-form-item>
              <el-button style="width:100%" @click="demoLogin">演示账号一键登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form @submit.prevent="handleRegister">
            <el-form-item label="用户名">
              <el-input v-model="regUsername" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="显示名称">
              <el-input v-model="regDisplayName" placeholder="请输入显示名称" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="regPassword" type="password" placeholder="请输入密码（至少6位）" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" native-type="submit" style="width:100%" :loading="loading">注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
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

async function demoLogin() {
  username.value = 'demo_student'
  password.value = 'demo123456'
  await handleLogin()
}
</script>
