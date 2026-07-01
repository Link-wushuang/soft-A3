<template>
  <div class="ai-assistant">
    <transition name="panel-slide">
      <div v-if="open" class="panel">
        <div class="panel-header">
          <div class="header-left">
            <div class="ai-logo">
              <svg width="18" height="18" viewBox="0 0 28 28" fill="none">
                <path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="1.8" fill="none"/>
                <circle cx="14" cy="14" r="2.5" fill="white"/>
              </svg>
            </div>
            <div>
              <div class="header-title">EduPath 助手</div>
              <div class="header-sub">AI 智能问答</div>
            </div>
          </div>
          <button class="close-btn" @click="open = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </div>

        <div class="messages" ref="msgContainer">
          <div v-if="!messages.length" class="welcome">
            <div class="welcome-icon">
              <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
                <rect width="28" height="28" rx="8" fill="url(#wa-grad)"/>
                <path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="1.4" fill="none"/>
                <circle cx="14" cy="14" r="2" fill="white"/>
                <defs><linearGradient id="wa-grad" x1="0" y1="0" x2="28" y2="28"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs>
              </svg>
            </div>
            <p class="welcome-title">你好！我是 EduPath 助手</p>
            <p class="welcome-desc">有关于操作系统课程的问题随时可以问我</p>
            <div class="quick-questions">
              <button v-for="q in quickQuestions" :key="q" class="qq-btn" @click="send(q)">{{ q }}</button>
            </div>
          </div>

          <div v-for="(msg, i) in messages" :key="i" class="msg" :class="msg.role">
            <div v-if="msg.role === 'assistant'" class="msg-avatar">
              <svg width="14" height="14" viewBox="0 0 28 28" fill="none"><path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="2" fill="none"/><circle cx="14" cy="14" r="2" fill="white"/></svg>
            </div>
            <div class="msg-content">
              <MarkdownRenderer v-if="msg.role === 'assistant'" :content="msg.content" />
              <p v-else>{{ msg.content }}</p>
            </div>
          </div>

          <div v-if="loading && !isStreaming" class="msg assistant">
            <div class="msg-avatar">
              <svg width="14" height="14" viewBox="0 0 28 28" fill="none"><path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="2" fill="none"/><circle cx="14" cy="14" r="2" fill="white"/></svg>
            </div>
            <div class="msg-content typing"><span class="dot"/><span class="dot"/><span class="dot"/></div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-row">
            <input v-model="input" type="text" placeholder="输入你的问题..." @keydown.enter="send()" :disabled="loading" />
            <button class="send-btn" @click="send()" :disabled="!input.trim() || loading">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
          </div>
        </div>
      </div>
    </transition>

    <button class="fab" :class="{ hidden: open }" @click="open = true">
      <svg width="24" height="24" viewBox="0 0 28 28" fill="none">
        <path d="M8 10L14 5.5L20 10V18L14 22.5L8 18V10Z" stroke="white" stroke-width="1.6" fill="none"/>
        <circle cx="14" cy="14" r="2.5" fill="white" opacity="0.9"/>
      </svg>
      <span class="fab-label">AI 助手</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import api from '../api/index'
import { createSSE } from '../api/sse'
import MarkdownRenderer from './MarkdownRenderer.vue'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const isStreaming = ref(false)
const messages = ref<Array<{ role: string; content: string }>>([])
const msgContainer = ref<HTMLElement>()

const quickQuestions = [
  '什么是进程和线程？',
  '页面置换算法有哪些？',
  '死锁的四个必要条件？',
]

function scrollBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}

watch(open, (v) => { if (v) scrollBottom() })

async function send(text?: string) {
  const q = text || input.value.trim()
  if (!q || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: q })
  scrollBottom()
  loading.value = true

  // 预插入空 assistant 消息，用于流式追加
  const assistantMsg: { role: string; content: string } = { role: 'assistant', content: '' }
  messages.value.push(assistantMsg)
  isStreaming.value = true

  // 拼接历史上下文（取最近 4 轮，避免 query 过长）
  const history = messages.value
    .slice(-9, -2) // 排除刚插入的 user 和空的 assistant
    .filter(m => m.content)
  const contextPrefix = history.length
    ? '之前的对话历史：\n' + history.map(m => `${m.role === 'user' ? '学生' : '助手'}: ${m.content.slice(0, 200)}`).join('\n') + '\n\n当前问题：'
    : ''

  try {
    const params = new URLSearchParams({ question: contextPrefix + q })
    createSSE(
      `/api/tutor/chat/stream?${params.toString()}`,
      (event) => {
        const data = event.data ? JSON.parse(event.data) : {}
        if (event.type === 'token') {
          assistantMsg.content += data.text || ''
          scrollBottom()
        } else if (event.type === 'error') {
          assistantMsg.content = assistantMsg.content || '抱歉，回答生成失败，请稍后重试。'
          if (!assistantMsg.content.includes('抱歉')) {
            assistantMsg.content += '\n\n（生成中断，请重试）'
          }
        }
      },
      () => {
        if (!assistantMsg.content) {
          assistantMsg.content = '抱歉，回答生成失败，请稍后重试。'
        }
        isStreaming.value = false
        loading.value = false
        scrollBottom()
      }
    )
  } catch {
    // EventSource 创建失败，回退到普通接口
    messages.value.pop()
    isStreaming.value = false
    try {
      const chatMessages = messages.value.map(m => ({ role: m.role, content: m.content }))
      const res = await api.post('/tutor/chat', { messages: chatMessages })
      messages.value.push({ role: 'assistant', content: res.data.answer })
    } catch {
      messages.value.push({ role: 'assistant', content: '抱歉，回答生成失败，请稍后重试。' })
    } finally {
      loading.value = false
      scrollBottom()
    }
  }
}
</script>

<style scoped>
.ai-assistant { position: fixed; bottom: 24px; right: 24px; z-index: 9999; }

.fab { display: flex; align-items: center; gap: 8px; padding: 12px 20px; border: none; border-radius: 50px; background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; cursor: pointer; box-shadow: 0 4px 20px rgba(79,70,229,0.4); transition: all 0.3s cubic-bezier(0.4,0,0.2,1); }
.fab:hover { transform: translateY(-2px); box-shadow: 0 6px 28px rgba(79,70,229,0.5); }
.fab.hidden { opacity: 0; pointer-events: none; transform: scale(0.8); }
.fab-label { font-size: 14px; font-weight: 600; }

.panel { position: absolute; bottom: 0; right: 0; width: 380px; height: 560px; background: white; border-radius: 16px; box-shadow: 0 12px 48px rgba(15,23,42,0.15), 0 0 0 1px rgba(15,23,42,0.05); display: flex; flex-direction: column; overflow: hidden; }

.panel-slide-enter-active { transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1); }
.panel-slide-leave-active { transition: all 0.2s ease-in; }
.panel-slide-enter-from { opacity: 0; transform: translateY(20px) scale(0.95); }
.panel-slide-leave-to { opacity: 0; transform: translateY(10px) scale(0.98); }

.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; background: linear-gradient(135deg, #4f46e5, #6d28d9); flex-shrink: 0; }
.header-left { display: flex; align-items: center; gap: 10px; }
.ai-logo { width: 34px; height: 34px; border-radius: 10px; background: rgba(255,255,255,0.18); display: flex; align-items: center; justify-content: center; }
.header-title { color: white; font-size: 14px; font-weight: 600; }
.header-sub { color: rgba(255,255,255,0.7); font-size: 11px; }
.close-btn { background: rgba(255,255,255,0.12); border: none; color: rgba(255,255,255,0.8); width: 30px; height: 30px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; }
.close-btn:hover { background: rgba(255,255,255,0.25); }

.messages { flex: 1; overflow-y: auto; padding: 16px; }

.welcome { text-align: center; padding: 20px 10px; }
.welcome-icon { margin: 0 auto 14px; }
.welcome-title { font-weight: 600; font-size: 15px; margin: 0 0 4px; color: var(--ep-text-primary); }
.welcome-desc { font-size: 13px; color: var(--ep-text-secondary); margin: 0 0 18px; }
.quick-questions { display: flex; flex-direction: column; gap: 8px; }
.qq-btn { padding: 10px 14px; border: 1px solid var(--ep-border); border-radius: 10px; background: white; font-size: 13px; color: var(--ep-text-secondary); cursor: pointer; text-align: left; transition: all 0.2s; }
.qq-btn:hover { border-color: var(--ep-primary); color: var(--ep-primary); background: var(--ep-primary-light); }

.msg { display: flex; gap: 8px; margin-bottom: 14px; animation: msgIn 0.25s ease-out; }
.msg.user { justify-content: flex-end; }
.msg-avatar { width: 28px; height: 28px; border-radius: 8px; background: linear-gradient(135deg, #6366f1, #8b5cf6); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.msg-content { max-width: 78%; padding: 10px 14px; border-radius: 12px; font-size: 13px; line-height: 1.65; }
.msg.user .msg-content { background: linear-gradient(135deg, #4f46e5, #4338ca); color: white; border-bottom-right-radius: 4px; }
.msg.user .msg-content p { margin: 0; }
.msg.assistant .msg-content { background: #f8fafc; border: 1px solid var(--ep-border-light); border-bottom-left-radius: 4px; }

.msg-content.typing { display: flex; align-items: center; gap: 4px; padding: 14px 18px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: #cbd5e1; animation: bounce 1.4s infinite ease-in-out; }
.dot:nth-child(2) { animation-delay: 0.16s; }
.dot:nth-child(3) { animation-delay: 0.32s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0.5); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
@keyframes msgIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.input-area { padding: 12px; border-top: 1px solid var(--ep-border-light); flex-shrink: 0; }
.input-row { display: flex; gap: 8px; align-items: center; }
.input-row input { flex: 1; padding: 10px 14px; border: 1px solid var(--ep-border); border-radius: 10px; font-size: 13px; outline: none; background: #f8fafc; transition: border-color 0.2s, box-shadow 0.2s; }
.input-row input:focus { border-color: var(--ep-primary); box-shadow: 0 0 0 3px rgba(79,70,229,0.08); background: white; }
.send-btn { width: 36px; height: 36px; border: none; border-radius: 10px; background: var(--ep-primary); color: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: opacity 0.15s; flex-shrink: 0; }
.send-btn:disabled { opacity: 0.4; cursor: default; }
.send-btn:hover:not(:disabled) { opacity: 0.9; }
</style>
