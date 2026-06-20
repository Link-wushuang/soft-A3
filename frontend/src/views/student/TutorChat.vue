<template>
  <div class="page-container" style="max-width:960px">
    <div class="page-header">
      <div>
        <h1 class="page-title">智能答疑</h1>
        <p class="page-subtitle">针对当前知识点提出问题，获取个性化解答</p>
      </div>
      <el-button @click="$router.back()">
        <el-icon style="margin-right:6px"><Back /></el-icon>
        返回
      </el-button>
    </div>

    <div class="chat-card card">
      <div class="chat-messages" ref="msgBox">
        <div v-if="!chatHistory.length" class="chat-empty">
          <div class="empty-icon">
            <el-icon :size="48" style="color:var(--ep-primary)"><ChatDotRound /></el-icon>
          </div>
          <p class="empty-title">有什么想问的？</p>
          <p class="empty-desc">输入你对当前知识点的疑问，AI 将为你解答</p>
          <div class="hint-grid">
            <button v-for="hint in hints" :key="hint" class="hint-btn" @click="sendMessage(hint)">
              {{ hint }}
            </button>
          </div>
        </div>

        <div v-for="(msg, i) in chatHistory" :key="i" class="msg-row" :class="msg.role">
          <div v-if="msg.role === 'assistant'" class="msg-avatar">
            <el-icon :size="16" style="color:var(--ep-primary)"><Cpu /></el-icon>
          </div>
          <div class="msg-bubble">
            <MarkdownRenderer v-if="msg.role === 'assistant'" :content="msg.content" />
            <p v-else>{{ msg.content }}</p>
          </div>
          <div v-if="msg.role === 'user'" class="msg-avatar user-avatar">
            <el-icon :size="14"><User /></el-icon>
          </div>
        </div>

        <div v-if="loading" class="msg-row assistant">
          <div class="msg-avatar">
            <el-icon :size="16" style="color:var(--ep-primary)"><Cpu /></el-icon>
          </div>
          <div class="msg-bubble typing">
            <span class="dot" /><span class="dot" /><span class="dot" />
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="输入你的问题..."
          @keydown.enter.exact.prevent="sendMessage()"
        />
        <el-button type="primary" class="send-btn" :loading="loading" @click="sendMessage()">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, ChatDotRound, Cpu, User } from '@element-plus/icons-vue'
import api from '../../api/index'
import MarkdownRenderer from '../../components/MarkdownRenderer.vue'

const route = useRoute()
const kpId = computed(() => Number(route.params.knowledgePointId))

const chatHistory = ref<Array<{ role: string; content: string }>>([])
const inputText = ref('')
const loading = ref(false)
const msgBox = ref<HTMLElement>()

const hints = [
  '这个知识点的核心概念是什么？',
  '能举一个具体的例子吗？',
  '常见的易错点有哪些？',
  '和其他相关知识点有什么区别？',
]

function scrollToBottom() {
  nextTick(() => {
    if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
  })
}

async function sendMessage(text?: string) {
  const question = text || inputText.value.trim()
  if (!question) return
  inputText.value = ''

  chatHistory.value.push({ role: 'user', content: question })
  scrollToBottom()
  loading.value = true

  try {
    const res = await api.post('/tutor/ask', {
      knowledge_point_id: kpId.value,
      question,
    })
    chatHistory.value.push({ role: 'assistant', content: res.data.answer })
    scrollToBottom()
  } catch {
    ElMessage.error('回答生成失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
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

.msg-row.user .msg-bubble p { margin: 0; }

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

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
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
</style>
