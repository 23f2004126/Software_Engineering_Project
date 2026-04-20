<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { chatbotService } from '../../services/apiService.js'
import { useAuthStore } from '../../stores/authStore.js'
import { useAIAssistantStore } from '../../stores/aiAssistantStore.js'

const router = useRouter()
const authStore = useAuthStore()
const aiAssistantStore = useAIAssistantStore()

const inputText = ref('')
const isTyping = ref(false)
const messagesEl = ref(null)
const conversationHistory = ref([])

const ownerIntroMessage = 'Ask me about sales, inventory, credit, profit, or trends. I will use the `/query/chat` endpoint for each message.'
const employeeIntroMessage = 'Ask me about billing, inventory, milk entries, shift activity, or today\'s store status. I only answer store-related questions here and will not answer user-related or employee-account questions.'

const messages = ref([])
const assistantScope = computed(() => (authStore.isEmployee ? 'employee_store_only' : 'default'))

const quickChips = computed(() => {
  if (authStore.isEmployee) {
    return [
      "Today's summary",
      'Low stock items',
      'Today\'s billing status',
      'My shift summary',
    ]
  }

  return [
    "Today's summary",
    'Low stock items',
    'Profit analysis',
    'Credit risk customers',
  ]
})

const buildIntroMessage = () => ({
  role: 'ai',
  text: authStore.isEmployee ? employeeIntroMessage : ownerIntroMessage,
  time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
})

const resetConversation = () => {
  messages.value = [buildIntroMessage()]
  conversationHistory.value = []
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

const sendMessage = async (prefilledText = '') => {
  const promptSource = typeof prefilledText === 'string' ? prefilledText : inputText.value
  const prompt = promptSource.trim()
  if (!prompt || isTyping.value) return

  messages.value.push({
    role: 'user',
    text: prompt,
    time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
  })

  inputText.value = ''
  await scrollToBottom()

  isTyping.value = true

  try {
    const result = await chatbotService.queryChat(prompt, conversationHistory.value, {
      scope: assistantScope.value,
    })

    conversationHistory.value = result.history || []

    messages.value.push({
      role: 'ai',
      text: result.text || 'The assistant responded without a message body.',
      time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    })
  } catch (error) {
    messages.value.push({
      role: 'ai',
      text: error.message || 'Failed to reach the chatbot service.',
      time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
      isError: true,
    })
  } finally {
    isTyping.value = false
    await scrollToBottom()
  }
}

const handleQuickChip = (chip) => {
  sendMessage(chip)
}

const navigateLink = (route) => {
  router.push(route)
  aiAssistantStore.close()
}

watch(
  () => aiAssistantStore.isOpen,
  async (isOpen) => {
    if (!isOpen) return

    if (messages.value.length === 0) {
      resetConversation()
    }

    await scrollToBottom()

    const pendingPrompt = aiAssistantStore.consumePendingPrompt()
    if (pendingPrompt) {
      inputText.value = pendingPrompt
      sendMessage(pendingPrompt)
    }
  }
)

watch(
  () => authStore.role,
  () => {
    resetConversation()
  },
  { immediate: true }
)
</script>

<template>
  <div>
    <button
      class="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/30 transition-transform duration-200 hover:scale-110"
      @click="aiAssistantStore.isOpen ? aiAssistantStore.close() : aiAssistantStore.open()"
    >
      <Transition mode="out-in">
        <div v-if="!aiAssistantStore.isOpen" class="relative flex items-center justify-center">
          <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
            <path
              d="M12.997 6.71c.305-2.054 2.056-3.645 4.131-3.638 2.076.007 3.81 1.611 4.096 3.667l.39 2.783h.762c2.021 0 3.627 1.703 3.627 3.75v7.9c0 2.047-1.606 3.75-3.627 3.75H2.627C.606 24 0 22.297 0 20.25v-7.9c0-2.047 1.606-3.75 3.627-3.75h.744l.38-2.783c.286-2.058 2.025-3.663 4.098-3.67 2.076-.007 3.826 1.584 4.131 3.638"
            />
          </svg>
          <div class="absolute inset-0 rounded-full bg-emerald-400/20 animate-ping"></div>
        </div>
        <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </Transition>
    </button>

    <Transition name="chat-panel">
      <div
        v-show="aiAssistantStore.isOpen"
        class="fixed bottom-24 right-6 z-50 flex h-[540px] w-96 flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl"
      >
        <div class="flex shrink-0 items-center justify-between bg-gradient-to-r from-emerald-500 to-teal-600 px-5 py-4 text-white">
          <div class="flex items-center gap-2">
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
              <path
                d="M12.997 6.71c.305-2.054 2.056-3.645 4.131-3.638 2.076.007 3.81 1.611 4.096 3.667l.39 2.783h.762c2.021 0 3.627 1.703 3.627 3.75v7.9c0 2.047-1.606 3.75-3.627 3.75H2.627C.606 24 0 22.297 0 20.25v-7.9c0-2.047 1.606-3.75 3.627-3.75h.744l.38-2.783c.286-2.058 2.025-3.663 4.098-3.67 2.076-.007 3.826 1.584 4.131 3.638"
              />
            </svg>
            <div>
              <p class="font-semibold">AI Assistant</p>
              <p class="text-xs text-white/70">Connected to `/query/chat`</p>
            </div>
          </div>
          <button class="h-8 w-8 rounded-lg text-white/70 transition-colors hover:bg-white/10 hover:text-white" @click="aiAssistantStore.close()">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="scrollbar-hide flex gap-2 overflow-x-auto border-b border-slate-100 bg-emerald-50/50 px-4 py-2">
          <button
            v-for="chip in quickChips"
            :key="chip"
            class="whitespace-nowrap rounded-full border border-emerald-200 bg-white px-3 py-1.5 text-xs text-emerald-700 transition-colors hover:bg-emerald-50"
            @click="handleQuickChip(chip)"
          >
            {{ chip }}
          </button>
        </div>

        <div ref="messagesEl" class="flex-1 space-y-4 overflow-y-auto px-4 py-4">
          <div v-for="(message, i) in messages" :key="i" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start gap-2'">
            <svg v-if="message.role === 'ai'" class="mt-1 h-5 w-5 shrink-0 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
            </svg>

            <div class="flex flex-col" :class="message.role === 'user' ? 'items-end' : 'items-start'">
              <div
                class="max-w-xs rounded-2xl px-4 py-2.5 text-sm"
                :class="
                  message.role === 'user'
                    ? 'rounded-br-sm bg-emerald-500 text-white'
                    : message.isError
                      ? 'rounded-bl-sm border border-red-200 bg-red-50 text-red-700'
                      : 'rounded-bl-sm bg-slate-100 text-slate-800'
                "
              >
                {{ message.text }}
              </div>

              <pre
                v-if="message.sql"
                class="mt-2 max-w-xs overflow-x-auto whitespace-pre-wrap rounded-2xl bg-slate-950 px-4 py-3 text-xs leading-6 text-emerald-200"
              >{{ message.sql }}</pre>

              <div v-if="message.links && message.links.length > 0" class="mt-2 flex flex-wrap gap-2">
                <button
                  v-for="link in message.links"
                  :key="link.route"
                  class="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs text-emerald-600 transition-colors hover:bg-emerald-50"
                  @click="navigateLink(link.route)"
                >
                  {{ link.label }}
                </button>
              </div>

              <p class="mt-1 text-xs text-slate-400">{{ message.time }}</p>
            </div>
          </div>

          <div v-if="isTyping" class="flex justify-start gap-2">
            <svg class="mt-1 h-5 w-5 shrink-0 text-emerald-500" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
            </svg>
            <div class="flex items-center gap-1.5 rounded-2xl rounded-bl-sm bg-slate-100 px-4 py-2.5 text-sm text-slate-800">
              <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" style="animation-delay: 0ms"></span>
              <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" style="animation-delay: 150ms"></span>
              <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>

        <div class="flex shrink-0 items-center gap-2 border-t border-slate-100 bg-white px-4 py-3">
          <input
            v-model="inputText"
            type="text"
            placeholder="Ask anything..."
            class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm transition focus:border-transparent focus:outline-none focus:ring-2 focus:ring-emerald-400"
            @keyup.enter="sendMessage"
          />
          <button
            class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500 text-white transition-colors hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="isTyping || !inputText.trim()"
            @click="sendMessage"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.chat-panel-enter-active,
.chat-panel-leave-active {
  transition: all 0.3s ease;
  transform-origin: bottom right;
}

.chat-panel-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(24px);
}

.chat-panel-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(24px);
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

.animate-bounce {
  animation: bounce 0.6s infinite;
}
</style>
