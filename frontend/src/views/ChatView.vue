<template>
  <div class="chat-view">
    <h1>Chat with Report Agent</h1>
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.role">
        <div class="message-content">{{ msg.content }}</div>
      </div>
    </div>
    <form @submit.prevent="sendMessage" class="chat-input">
      <input v-model="input" placeholder="Ask about the simulation results..." class="input" :disabled="sending" />
      <button type="submit" class="btn btn-primary" :disabled="!input.trim() || sending">Send</button>
    </form>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { chatWithReport } from '../api/report'

const route = useRoute()
const messages = ref([])
const input = ref('')
const sending = ref(false)
const conversationId = ref(null)
const messagesContainer = ref(null)

const sendMessage = async () => {
  if (!input.value.trim()) return
  const userMsg = input.value
  messages.value.push({ role: 'user', content: userMsg })
  input.value = ''
  sending.value = true

  try {
    const res = await chatWithReport(route.params.reportId, {
      message: userMsg,
      conversation_id: conversationId.value,
    })
    conversationId.value = res.data.conversation_id
    messages.value.push({ role: 'assistant', content: res.data.response })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: 'Error: Could not get response.' })
  }

  sending.value = false
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-view { max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; height: calc(100vh - 120px); }
.chat-messages { flex: 1; overflow-y: auto; padding: 1rem; background: #1a1d27; border-radius: 12px; margin: 1rem 0; }
.message { margin-bottom: 1rem; }
.message.user .message-content { background: #1565c0; padding: 0.75rem 1rem; border-radius: 12px 12px 4px 12px; display: inline-block; max-width: 80%; float: right; clear: both; }
.message.assistant .message-content { background: #252830; padding: 0.75rem 1rem; border-radius: 12px 12px 12px 4px; display: inline-block; max-width: 80%; float: left; clear: both; }
.chat-input { display: flex; gap: 0.75rem; }
.input { flex: 1; padding: 0.75rem; background: #252830; border: 1px solid #3a3d4a; border-radius: 8px; color: #e0e0e0; font-size: 1rem; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; }
.btn-primary { background: #4fc3f7; color: #0f1117; font-weight: bold; }
</style>
