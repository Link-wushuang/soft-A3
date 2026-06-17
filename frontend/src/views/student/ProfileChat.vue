<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header style="height:auto;padding:16px 0"><h1 style="margin:0">对话式学习建档</h1></el-header>
    <el-main>
      <el-card>
        <div v-for="(msg, i) in chatHistory" :key="i" :style="{ textAlign: msg.role === 'user' ? 'right' : 'left', marginBottom: '12px' }">
          <el-tag :type="msg.role === 'user' ? 'primary' : 'success'" size="small">{{ msg.role === 'user' ? '我' : '系统' }}</el-tag>
          <p style="margin:4px 0;white-space:pre-wrap">{{ msg.content }}</p>
        </div>
      </el-card>
      <el-form @submit.prevent="sendMessage" style="margin-top:16px;display:flex;gap:8px">
        <el-input v-model="input" placeholder="描述你的学习情况，例如：我在学操作系统，文件系统的链接分配不太会..." :rows="3" type="textarea" style="flex:1" />
        <el-button type="primary" native-type="submit" :loading="loading" style="height:auto">发送</el-button>
      </el-form>
      <ProfileCard v-if="profile" :profile="profile" style="margin-top:16px" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import ProfileCard from '../../components/ProfileCard.vue'
import api from '../../api/index'

const input = ref('')
const loading = ref(false)
const profile = ref<any>(null)
const chatHistory = ref<Array<{ role: string; content: string }>>([])

async function sendMessage() {
  if (!input.value.trim()) return
  const userMsg = input.value
  chatHistory.value.push({ role: 'user', content: userMsg })
  input.value = ''
  loading.value = true
  try {
    const res = await api.post('/profile/dialogue', { course_id: 1, message: userMsg })
    profile.value = res.data
    chatHistory.value.push({ role: 'assistant', content: '画像已更新，请查看下方画像卡片。' })
  } catch {
    ElMessage.error('画像提取失败')
  } finally {
    loading.value = false
  }
}
</script>
