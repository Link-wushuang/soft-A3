<template>
  <el-container style="padding:24px;max-width:900px;margin:0 auto">
    <el-header style="height:auto;padding:16px 0">
      <h1 style="margin:0">对话式学习建档</h1>
      <p style="color:#909399;margin:8px 0 0">描述你的学习情况，系统将自动分析并构建你的学习画像</p>
    </el-header>
    <el-main>
      <el-card>
        <div v-if="!chatHistory.length" style="text-align:center;color:#909399;padding:24px 0">
          <p>你可以这样说：</p>
          <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:12px">
            <el-button v-for="hint in hints" :key="hint" size="small" round @click="useHint(hint)">
              {{ hint }}
            </el-button>
          </div>
        </div>
        <div v-for="(msg, i) in chatHistory" :key="i" class="chat-msg" :class="msg.role">
          <div class="chat-bubble">
            <div class="chat-role">{{ msg.role === 'user' ? '我' : '学习助手' }}</div>
            <MarkdownRenderer v-if="msg.role === 'assistant'" :content="msg.content" />
            <p v-else style="margin:4px 0;white-space:pre-wrap">{{ msg.content }}</p>
          </div>
        </div>
      </el-card>
      <el-form @submit.prevent="sendMessage" style="margin-top:16px;display:flex;gap:8px">
        <el-input v-model="input" placeholder="描述你的学习情况..." :rows="2" type="textarea" style="flex:1"
                  @keydown.ctrl.enter="sendMessage" />
        <el-button type="primary" native-type="submit" :loading="loading" style="height:auto;align-self:flex-end">
          发送
        </el-button>
      </el-form>
      <ProfileCard v-if="profile" :profile="profile" style="margin-top:16px" />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import ProfileCard from '../../components/ProfileCard.vue'
import MarkdownRenderer from '../../components/MarkdownRenderer.vue'
import api from '../../api/index'

const input = ref('')
const loading = ref(false)
const profile = ref<any>(null)
const chatHistory = ref<Array<{ role: string; content: string }>>([])

const hints = [
  '我在学操作系统，文件系统的链接分配不太会',
  '我想两天内掌握文件系统，喜欢图解和例题',
  '我基础一般，想复习进程同步和死锁',
  '我时间不多，想快速掌握磁盘I/O计算',
]

function useHint(hint: string) {
  input.value = hint
  sendMessage()
}

async function sendMessage() {
  if (!input.value.trim()) return
  const userMsg = input.value
  chatHistory.value.push({ role: 'user', content: userMsg })
  input.value = ''
  loading.value = true
  try {
    const res = await api.post('/profile/dialogue', { course_id: 1, message: userMsg })
    profile.value = res.data
    const reply = res.data.reply || '画像已更新，请查看下方画像卡片。'
    chatHistory.value.push({ role: 'assistant', content: reply })
  } catch {
    ElMessage.error('画像提取失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-msg { margin-bottom: 16px; }
.chat-msg.user { display: flex; justify-content: flex-end; }
.chat-msg.assistant { display: flex; justify-content: flex-start; }
.chat-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}
.chat-msg.user .chat-bubble { background: #ecf5ff; border-bottom-right-radius: 4px; }
.chat-msg.assistant .chat-bubble { background: #f4f4f5; border-bottom-left-radius: 4px; }
.chat-role { font-size: 12px; color: #909399; margin-bottom: 4px; }
</style>
