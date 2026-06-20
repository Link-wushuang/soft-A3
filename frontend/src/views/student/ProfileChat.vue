<template>
  <div class="page-container" style="max-width:960px">
    <div class="page-header">
      <div>
        <h1 class="page-title">对话式学习建档</h1>
        <p class="page-subtitle">描述你的学习情况，系统将自动分析并构建你的学习画像</p>
      </div>
    </div>

    <div class="chat-layout">
      <div class="chat-main">
        <div class="chat-card card">
          <div class="chat-messages" ref="messageArea">
            <div v-if="!chatHistory.length" class="chat-empty">
              <div class="empty-icon">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                  <rect width="48" height="48" rx="12" fill="#eff6ff"/>
                  <path d="M16 20C16 18.9 16.9 18 18 18H30C31.1 18 32 18.9 32 20V28C32 29.1 31.1 30 30 30H26L22 34V30H18C16.9 30 16 29.1 16 28V20Z" stroke="#2563eb" stroke-width="1.5" fill="none"/>
                  <circle cx="22" cy="24" r="1" fill="#2563eb"/>
                  <circle cx="26" cy="24" r="1" fill="#2563eb"/>
                </svg>
              </div>
              <p class="empty-title">开始你的学习建档对话</p>
              <p class="empty-desc">你可以点击下方提示快速开始</p>
              <div class="hint-grid">
                <button v-for="hint in hints" :key="hint" class="hint-btn" @click="useHint(hint)">
                  {{ hint }}
                </button>
              </div>
            </div>

            <div v-for="(msg, i) in chatHistory" :key="i" :class="['msg-row', msg.role]">
              <div class="msg-avatar" v-if="msg.role === 'assistant'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <rect width="24" height="24" rx="6" fill="#2563eb"/>
                  <path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.2" fill="none"/>
                  <circle cx="12" cy="12" r="2" fill="white"/>
                </svg>
              </div>
              <div class="msg-bubble">
                <MarkdownRenderer v-if="msg.role === 'assistant'" :content="msg.content" />
                <p v-else>{{ msg.content }}</p>
              </div>
              <div class="msg-avatar user-avatar" v-if="msg.role === 'user'">
                <el-icon :size="16"><User /></el-icon>
              </div>
            </div>

            <div v-if="loading" class="msg-row assistant">
              <div class="msg-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <rect width="24" height="24" rx="6" fill="#2563eb"/>
                  <path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.2" fill="none"/>
                  <circle cx="12" cy="12" r="2" fill="white"/>
                </svg>
              </div>
              <div class="msg-bubble typing">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <el-input v-model="input" placeholder="描述你的学习情况..." :rows="2" type="textarea"
                      @keydown.ctrl.enter="sendMessage" resize="none" />
            <el-button type="primary" :loading="loading" :disabled="!input.trim()" @click="sendMessage" class="send-btn">
              发送
            </el-button>
          </div>
        </div>
      </div>

      <div class="chat-aside">
        <ProfileCard v-if="profile" :profile="profile" />
        <div v-else class="card">
          <div class="card-body" style="text-align:center;padding:32px;color:var(--ep-text-muted)">
            <el-icon :size="32"><User /></el-icon>
            <p style="margin:12px 0 0;font-size:14px">发送消息后将生成学习画像</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import ProfileCard from '../../components/ProfileCard.vue'
import MarkdownRenderer from '../../components/MarkdownRenderer.vue'
import api from '../../api/index'

const input = ref('')
const loading = ref(false)
const profile = ref<any>(null)
const chatHistory = ref<Array<{ role: string; content: string }>>([])
const messageArea = ref<HTMLElement>()

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

function scrollToBottom() {
  nextTick(() => {
    if (messageArea.value) {
      messageArea.value.scrollTop = messageArea.value.scrollHeight
    }
  })
}

async function sendMessage() {
  if (!input.value.trim()) return
  const userMsg = input.value
  chatHistory.value.push({ role: 'user', content: userMsg })
  input.value = ''
  loading.value = true
  scrollToBottom()
  try {
    const res = await api.post('/profile/dialogue', { course_id: 1, message: userMsg })
    profile.value = res.data
    const reply = res.data.reply || '画像已更新，请查看右侧画像卡片。'
    chatHistory.value.push({ role: 'assistant', content: reply })
    scrollToBottom()
  } catch {
    ElMessage.error('画像提取失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  align-items: start;
}

.chat-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  padding: 24px;
  min-height: 400px;
  max-height: 560px;
  overflow-y: auto;
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.empty-icon { margin-bottom: 16px; }

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--ep-text-primary);
  margin: 0 0 6px;
}

.empty-desc {
  font-size: 13px;
  color: var(--ep-text-secondary);
  margin: 0 0 24px;
}

.hint-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  width: 100%;
}

.hint-btn {
  padding: 12px 16px;
  border: 1px solid var(--ep-border);
  border-radius: var(--ep-radius-md);
  background: white;
  font-size: 13px;
  color: var(--ep-text-secondary);
  cursor: pointer;
  transition: all var(--ep-transition);
  text-align: left;
  line-height: 1.5;
}

.hint-btn:hover {
  border-color: var(--ep-primary);
  color: var(--ep-primary);
  background: var(--ep-primary-light);
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 20px;
  animation: fadeUp 0.25s ease;
}

.msg-row.user {
  justify-content: flex-end;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--ep-primary-lighter);
}

.msg-avatar.user-avatar {
  background: var(--ep-bg);
  color: var(--ep-text-secondary);
}

.msg-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.7;
}

.msg-row.user .msg-bubble {
  background: var(--ep-primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-row.user .msg-bubble p {
  margin: 0;
}

.msg-row.assistant .msg-bubble {
  background: var(--ep-bg);
  border-bottom-left-radius: 4px;
}

.msg-bubble.typing {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 16px 20px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ep-text-muted);
  animation: bounce 1.4s infinite ease-in-out;
}

.dot:nth-child(2) { animation-delay: 0.16s; }
.dot:nth-child(3) { animation-delay: 0.32s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.chat-input-area {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--ep-border-light);
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.chat-input-area :deep(.el-textarea__inner) {
  border-radius: var(--ep-radius-md);
  box-shadow: none;
  border-color: var(--ep-border);
}

.send-btn {
  height: 40px;
  padding: 0 24px;
  border-radius: var(--ep-radius-sm) !important;
}

.chat-aside {
  position: sticky;
  top: 32px;
}

@media (max-width: 768px) {
  .chat-layout {
    grid-template-columns: 1fr;
  }
}
</style>
