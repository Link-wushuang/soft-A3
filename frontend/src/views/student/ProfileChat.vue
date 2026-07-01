<template>
  <div class="page-container" style="max-width:960px">
    <div class="page-header"><div><h1 class="page-title">对话式学习建档</h1><p class="page-subtitle">描述你的学习情况，系统将自动分析并构建你的学习画像</p></div></div>
    <div class="chat-layout">
      <div class="chat-main">
        <div class="chat-card card">
          <div class="chat-messages" ref="messageArea">
            <div v-if="!chatHistory.length" class="chat-empty">
              <div class="empty-state-icon" style="background:#eef2ff"><svg width="26" height="26" viewBox="0 0 26 26" fill="none"><path d="M5 12L5 8C5 6.9 5.9 6 7 6L19 6C20.1 6 21 6.9 21 8L21 16C21 17.1 20.1 18 19 18L15 18L11 22L11 18L7 18C5.9 18 5 17.1 5 16Z" stroke="#6366f1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="1.2" fill="#6366f1"/><circle cx="16" cy="12" r="1.2" fill="#6366f1"/></svg></div>
              <p class="empty-state-title">开始你的学习建档对话</p><p class="empty-state-desc">你可以点击下方提示快速开始</p>
              <div class="hint-grid"><button v-for="hint in hints" :key="hint" class="hint-btn" @click="useHint(hint)">{{ hint }}</button></div>
            </div>
            <div v-for="(msg,i) in chatHistory" :key="i" :class="['msg-row',msg.role]">
              <div class="msg-avatar" v-if="msg.role==='assistant'"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="6" fill="url(#ai-grad)"/><path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.2" fill="none"/><circle cx="12" cy="12" r="2" fill="white"/><defs><linearGradient id="ai-grad" x1="0" y1="0" x2="24" y2="24"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs></svg></div>
              <div class="msg-bubble"><MarkdownRenderer v-if="msg.role==='assistant'" :content="msg.content" /><p v-else>{{ msg.content }}</p></div>
              <div class="msg-avatar user-avatar" v-if="msg.role==='user'">{{ userInitial }}</div>
            </div>
            <div v-if="loading && !isStreaming" class="msg-row assistant"><div class="msg-avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="6" fill="url(#ai-grad)"/><path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.2" fill="none"/><circle cx="12" cy="12" r="2" fill="white"/></svg></div><div class="msg-bubble typing"><span class="dot" /><span class="dot" /><span class="dot" /></div></div>
          </div>
          <div class="chat-input-area"><div class="input-wrap"><el-input v-model="input" placeholder="描述你的学习情况..." :rows="2" type="textarea" @keydown.ctrl.enter="sendMessage" resize="none" /><el-button type="primary" :loading="loading" :disabled="!input.trim()" @click="sendMessage" class="send-btn"><el-icon :size="18"><Promotion /></el-icon></el-button></div></div>
        </div>
      </div>
      <div class="chat-aside"><ProfileCard v-if="profile" :profile="profile" /><div v-else class="card"><div class="card-body" style="text-align:center;padding:40px 24px;color:var(--ep-text-muted)"><div class="empty-state-icon" style="background:var(--ep-bg-soft);margin-bottom:16px"><el-icon :size="24"><User /></el-icon></div><p style="margin:0;font-size:14px;font-weight:500;color:var(--ep-text-secondary)">发送消息后将生成学习画像</p></div></div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'; import { ElMessage } from 'element-plus'; import { User, Promotion } from '@element-plus/icons-vue'
import ProfileCard from '../../components/ProfileCard.vue'; import MarkdownRenderer from '../../components/MarkdownRenderer.vue'; import api from '../../api/index'; import { createSSE } from '../../api/sse'
const auth = useAuthStore(); const input = ref(''); const loading = ref(false); const profile = ref<any>(null)
const chatHistory = ref<Array<{role:string;content:string}>>([]); const messageArea = ref<HTMLElement>()
const isStreaming = ref(false)
// 当前为单课程上下文（course_id=1）
const COURSE_ID = 1
const userInitial = computed(() => { const n = auth.user?.display_name||auth.user?.username||'?'; return n.charAt(0).toUpperCase() })
const hints = ['我在学操作系统，文件系统的链接分配不太会','我想两天内掌握文件系统，喜欢图解和例题','我基础一般，想复习进程同步和死锁','我时间不多，想快速掌握磁盘I/O计算']
function useHint(h:string) { input.value = h; sendMessage() }
onMounted(async () => { try { const res = await api.get(`/profile/${COURSE_ID}`); if (res.data && res.data.learning_goal) profile.value = res.data } catch {} })
function scrollToBottom() { nextTick(() => { if(messageArea.value) messageArea.value.scrollTop = messageArea.value.scrollHeight }) }
async function sendMessage() {
  if(!input.value.trim()) return
  const m = input.value
  chatHistory.value.push({role:'user',content:m})
  input.value=''
  loading.value=true
  scrollToBottom()
  // 流式回复：预先插入空 assistant 消息，逐 token 追加
  const assistantMsg: {role:string;content:string} = {role:'assistant',content:''}
  chatHistory.value.push(assistantMsg)
  isStreaming.value = true
  scrollToBottom()
  try {
    const params = new URLSearchParams({ course_id: String(COURSE_ID), message: m })
    createSSE(
      `/api/profile/dialogue/stream?${params.toString()}`,
      (event) => {
        const data = event.data ? JSON.parse(event.data) : {}
        if (event.type === 'token') {
          assistantMsg.content += data.text || ''
          scrollToBottom()
        } else if (event.type === 'profile_ready') {
          profile.value = data
        } else if (event.type === 'error') {
          ElMessage.error(data.message || '画像提取失败')
        }
      },
      () => {
        if (!assistantMsg.content) {
          assistantMsg.content = '画像已更新，请查看右侧画像卡片。'
        }
        isStreaming.value = false
        loading.value = false
        scrollToBottom()
      }
    )
  } catch {
    chatHistory.value.pop()
    isStreaming.value = false
    try {
      const r = await api.post('/profile/dialogue',{course_id:COURSE_ID,message:m})
      profile.value=r.data
      chatHistory.value.push({role:'assistant',content:r.data.reply||'画像已更新，请查看右侧画像卡片。'})
      scrollToBottom()
    } catch { ElMessage.error('画像提取失败') }
    finally { loading.value=false }
  }
}
</script>

<style scoped>
.chat-layout { display:grid;grid-template-columns:1fr 300px;gap:20px;align-items:start; } .chat-card { display:flex;flex-direction:column;overflow:hidden; }
.chat-messages { padding:24px;min-height:400px;max-height:560px;overflow-y:auto; } .chat-empty { display:flex;flex-direction:column;align-items:center;padding:40px 20px; }
.hint-grid { display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%; } .hint-btn { padding:14px 16px;border:1px solid var(--ep-border);border-radius:var(--ep-radius-md);background:white;font-size:13px;color:var(--ep-text-secondary);cursor:pointer;transition:all var(--ep-transition);text-align:left;line-height:1.5; } .hint-btn:hover { border-color:var(--ep-primary);color:var(--ep-primary);background:var(--ep-primary-light);transform:translateY(-2px);box-shadow:var(--ep-shadow-sm); }
.msg-row { display:flex;align-items:flex-start;gap:10px;margin-bottom:22px;animation:fadeUp 0.3s ease; } .msg-row.user { justify-content:flex-end; }
.msg-avatar { width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;background:#eef2ff;box-shadow:inset 0 1px 0 rgba(255,255,255,0.5); } .msg-avatar.user-avatar { background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;font-size:13px;font-weight:600; }
.msg-bubble { max-width:75%;padding:12px 18px;border-radius:16px;font-size:14px;line-height:1.7; } .msg-row.user .msg-bubble { background:linear-gradient(135deg,#6366f1,#4f46e5);color:white;border-bottom-right-radius:6px;box-shadow:0 2px 8px rgba(99,102,241,0.25); } .msg-row.user .msg-bubble p { margin:0; } .msg-row.assistant .msg-bubble { background:#f8fafc;border:1px solid var(--ep-border-light);border-bottom-left-radius:6px; }
.msg-bubble.typing { display:flex;align-items:center;gap:5px;padding:18px 22px; } .dot { width:7px;height:7px;border-radius:50%;background:#cbd5e1;animation:bounce 1.4s infinite ease-in-out; } .dot:nth-child(2){ animation-delay:0.16s; } .dot:nth-child(3){ animation-delay:0.32s; }
@keyframes bounce { 0%,80%,100%{ transform:scale(0.5);opacity:0.3; } 40%{ transform:scale(1);opacity:1; } }
.chat-input-area { padding:16px 20px 20px;border-top:1px solid var(--ep-border-light); } .input-wrap { display:flex;gap:10px;align-items:flex-end; } .input-wrap :deep(.el-textarea__inner) { border-radius:12px!important;box-shadow:none!important;border-color:var(--ep-border)!important;font-size:14px!important;padding:12px 16px!important;background:#f8fafc!important;transition:all var(--ep-transition)!important; } .input-wrap :deep(.el-textarea__inner):focus { border-color:var(--ep-primary)!important;box-shadow:0 0 0 3px rgba(99,102,241,0.08)!important;background:white!important; }
.send-btn { height:42px;width:42px;padding:0!important;border-radius:12px!important;flex-shrink:0; } .chat-aside { position:sticky;top:32px; }
@media (max-width:768px) { .chat-layout { grid-template-columns:1fr; } }
</style>
