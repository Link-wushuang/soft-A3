<template>
  <div class="page-container" style="max-width:960px">
    <div class="page-header"><div><h1 class="page-title">智能答疑</h1><p class="page-subtitle">选择知识点，提出疑问，获取 AI 个性化解答</p></div></div>
    <div class="kp-bar"><el-select v-model="selectedKpId" placeholder="选择知识点" filterable :loading="loadingKps" @change="onKpChange" style="width:100%;max-width:420px" size="large"><el-option v-for="kp in knowledgePoints" :key="kp.id" :label="`${kp.chapter} · ${kp.title}`" :value="kp.id" /></el-select><el-tag v-if="selectedKp" type="info" effect="light" round size="small">{{ selectedKpDiff }}</el-tag></div>
    <div class="chat-card card" :class="{ disabled: !selectedKpId }">
      <div class="chat-messages" ref="msgBox">
        <div v-if="!chatHistory.length" class="chat-empty"><div class="empty-state-icon" style="background:#eef2ff"><el-icon :size="26" style="color:#6366f1"><ChatDotRound /></el-icon></div><p class="empty-state-title">{{ selectedKpId?'有什么想问的？':'请先选择一个知识点' }}</p><p class="empty-state-desc">{{ selectedKpId?'输入你对当前知识点的疑问，AI 将为你解答':'在上方下拉框中选择你要提问的知识点' }}</p><div v-if="selectedKpId" class="hint-grid"><button v-for="hint in hints" :key="hint" class="hint-btn" @click="sendMessage(hint)">{{ hint }}</button></div></div>
        <div v-for="(msg,i) in chatHistory" :key="i" class="msg-row" :class="msg.role"><div v-if="msg.role==='assistant'" class="msg-avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="6" fill="url(#gt-ai)"/><path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.2" fill="none"/><circle cx="12" cy="12" r="2" fill="white"/><defs><linearGradient id="gt-ai" x1="0" y1="0" x2="24" y2="24"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#8b5cf6"/></linearGradient></defs></svg></div><div class="msg-bubble"><MarkdownRenderer v-if="msg.role==='assistant'" :content="msg.content" /><p v-else>{{ msg.content }}</p></div><div v-if="msg.role==='user'" class="msg-avatar user-avatar">{{ userInitial }}</div></div>
        <div v-if="loading" class="msg-row assistant"><div class="msg-avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect width="24" height="24" rx="6" fill="url(#gt-ai)"/><path d="M7 8.5L12 5L17 8.5V15.5L12 19L7 15.5V8.5Z" stroke="white" stroke-width="1.2" fill="none"/><circle cx="12" cy="12" r="2" fill="white"/></svg></div><div class="msg-bubble typing"><span class="dot" /><span class="dot" /><span class="dot" /></div></div>
      </div>
      <div class="chat-input-area"><div class="input-wrap"><el-input v-model="inputText" type="textarea" :autosize="{minRows:1,maxRows:4}" :placeholder="selectedKpId?'输入你的问题...':'请先选择知识点'" :disabled="!selectedKpId" @keydown.enter.exact.prevent="sendMessage()" /><el-button type="primary" class="send-btn" :loading="loading" :disabled="!inputText.trim()||!selectedKpId" @click="sendMessage()"><el-icon :size="18"><Promotion /></el-icon></el-button></div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'; import { useAuthStore } from '../../stores/auth'; import { ElMessage } from 'element-plus'; import { ChatDotRound, Promotion } from '@element-plus/icons-vue'; import api from '../../api/index'; import MarkdownRenderer from '../../components/MarkdownRenderer.vue'
const auth = useAuthStore(); const knowledgePoints = ref<Array<{id:number;chapter:string;title:string;difficulty:string}>>([]); const loadingKps = ref(false); const selectedKpId = ref<number|null>(null)
const chatHistory = ref<Array<{role:string;content:string}>>([]); const inputText = ref(''); const loading = ref(false); const msgBox = ref<HTMLElement>()
const userInitial = computed(() => { const n = auth.user?.display_name||auth.user?.username||'?'; return n.charAt(0).toUpperCase() })
const selectedKp = computed(() => knowledgePoints.value.find(k => k.id===selectedKpId.value))
const selectedKpDiff = computed(() => { const d=selectedKp.value?.difficulty; if(d==='easy') return '简单'; if(d==='hard') return '困难'; return '中等' })
const hints = ['这个知识点的核心概念是什么？','能举一个具体的例子吗？','常见的易错点有哪些？','和其他相关知识点有什么区别？']
function scrollToBottom() { nextTick(() => { if(msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight }) }
function onKpChange() { chatHistory.value=[] }
async function sendMessage(text?:string) { const q = text||inputText.value.trim(); if(!q||!selectedKpId.value) return; inputText.value=''; chatHistory.value.push({role:'user',content:q}); scrollToBottom(); loading.value=true
  try { const r = await api.post('/tutor/ask',{knowledge_point_id:selectedKpId.value,question:q}); chatHistory.value.push({role:'assistant',content:r.data.answer}); scrollToBottom() } catch { ElMessage.error('回答生成失败') } finally { loading.value=false } }
onMounted(async()=>{ loadingKps.value=true; try { const r=await api.get('/courses/1/knowledge-points'); knowledgePoints.value=r.data } catch { ElMessage.error('加载知识点列表失败') } finally { loadingKps.value=false } })
</script>

<style scoped>
.kp-bar { display:flex;align-items:center;gap:12px;margin-bottom:20px; } .chat-card { display:flex;flex-direction:column;overflow:hidden; } .chat-card.disabled { opacity:0.6;pointer-events:none; }
.chat-messages { padding:24px;min-height:400px;max-height:560px;overflow-y:auto; } .chat-empty { display:flex;flex-direction:column;align-items:center;padding:40px 20px; }
.hint-grid { display:grid;grid-template-columns:1fr 1fr;gap:10px;width:100%; } .hint-btn { padding:14px 16px;border:1px solid var(--ep-border);border-radius:var(--ep-radius-md);background:white;font-size:13px;color:var(--ep-text-secondary);cursor:pointer;transition:all var(--ep-transition);text-align:left;line-height:1.5; } .hint-btn:hover { border-color:var(--ep-primary);color:var(--ep-primary);background:var(--ep-primary-light);transform:translateY(-2px);box-shadow:var(--ep-shadow-sm); }
.msg-row { display:flex;align-items:flex-start;gap:10px;margin-bottom:22px;animation:fadeUp 0.3s ease; } .msg-row.user { justify-content:flex-end; }
.msg-avatar { width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;background:#eef2ff;box-shadow:inset 0 1px 0 rgba(255,255,255,0.5); } .msg-avatar.user-avatar { background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;font-size:13px;font-weight:600; }
.msg-bubble { max-width:75%;padding:12px 18px;border-radius:16px;font-size:14px;line-height:1.7; } .msg-row.user .msg-bubble { background:linear-gradient(135deg,#6366f1,#4f46e5);color:white;border-bottom-right-radius:6px;box-shadow:0 2px 8px rgba(99,102,241,0.25); } .msg-row.user .msg-bubble p { margin:0; } .msg-row.assistant .msg-bubble { background:#f8fafc;border:1px solid var(--ep-border-light);border-bottom-left-radius:6px; }
.msg-bubble.typing { display:flex;align-items:center;gap:5px;padding:18px 22px; } .dot { width:7px;height:7px;border-radius:50%;background:#cbd5e1;animation:bounce 1.4s infinite ease-in-out; } .dot:nth-child(2){ animation-delay:0.16s; } .dot:nth-child(3){ animation-delay:0.32s; } @keyframes bounce { 0%,80%,100%{ transform:scale(0.5);opacity:0.3; } 40%{ transform:scale(1);opacity:1; } }
.chat-input-area { padding:16px 20px 20px;border-top:1px solid var(--ep-border-light); } .input-wrap { display:flex;gap:10px;align-items:flex-end; } .input-wrap :deep(.el-textarea__inner) { border-radius:12px!important;box-shadow:none!important;border-color:var(--ep-border)!important;font-size:14px!important;padding:12px 16px!important;background:#f8fafc!important;transition:all var(--ep-transition)!important; } .input-wrap :deep(.el-textarea__inner):focus { border-color:var(--ep-primary)!important;box-shadow:0 0 0 3px rgba(99,102,241,0.08)!important;background:white!important; }
.send-btn { height:42px;width:42px;padding:0!important;border-radius:12px!important;flex-shrink:0; }
</style>
