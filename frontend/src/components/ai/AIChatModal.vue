<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isOpen = ref(false)
const inputText = ref('')
const isTyping = ref(false)
const messagesEl = ref(null)

const messages = ref([
  {
    role: 'user',
    text: "What's today's profit margin?",
    time: '10:32 AM',
  },
  {
    role: 'ai',
    text: "Your net profit today is ₹4,210 on ₹18,450 in sales — a 22.8% margin. This is 8.1% better than yesterday! 📈 Your lowest-margin category today is Dairy at 14%. Want to see a breakdown?",
    time: '10:32 AM',
    links: [
      { label: 'View Finance →', route: '/finance' },
      { label: 'Sales Breakdown →', route: '/sales' },
    ],
  },
  {
    role: 'user',
    text: 'Which items are expiring soon?',
    time: '10:33 AM',
  },
  {
    role: 'ai',
    text: '3 items expire within 7 days: Amul Curd 400g (2 days), Britannia Bread (5 days), Mother Dairy Paneer 200g (6 days). I recommend a clearance sale or logging them as losses. 🗓',
    time: '10:33 AM',
    links: [{ label: 'Open Inventory →', route: '/inventory' }],
  },
])

const quickChips = [
  "📊 Today's summary",
  '📦 Low stock',
  '💰 Profit analysis',
  '👤 Credit risk',
]

const mockResponses = [
  "Great question! Based on today's data, your store is performing above average. Total sales are ₹18,450 and net profit margin is 22.8%. 📊",
  'I noticed 7 products are below reorder level. The most critical is Aashirvaad Atta 5kg with only 2 units. Want me to create a purchase order? 📦',
  'Your highest-margin product this week is Amul Cheese Slice at 34.2% margin. Consider promoting it! ⭐',
  "Ramesh Patil's credit is overdue by 35 days (₹3,200). I suggest sending a reminder or restricting further credit. 👤",
]

const sendMessage = () => {
  if (inputText.value.trim() === '') return

  // Add user message
  messages.value.push({
    role: 'user',
    text: inputText.value,
    time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
  })

  inputText.value = ''

  // Scroll to bottom
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })

  // Simulate typing
  isTyping.value = true
  setTimeout(() => {
    isTyping.value = false

    // Add AI response
    messages.value.push({
      role: 'ai',
      text: mockResponses[Math.floor(Math.random() * mockResponses.length)],
      time: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
    })

    nextTick(() => {
      if (messagesEl.value) {
        messagesEl.value.scrollTop = messagesEl.value.scrollHeight
      }
    })
  }, 1500)
}

const handleQuickChip = (chip) => {
  inputText.value = chip
  sendMessage()
}

const navigateLink = (route) => {
  router.push(route)
  isOpen.value = false
}
</script>

<template>
  <div>
    <!-- Floating trigger button -->
    <button
      class="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/30 flex items-center justify-center text-white hover:scale-110 transition-transform duration-200"
      @click="isOpen = !isOpen"
    >
      <Transition mode="out-in">
        <div v-if="!isOpen" class="relative flex items-center justify-center">
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path
              d="M12.997 6.71c.305-2.054 2.056-3.645 4.131-3.638 2.076.007 3.81 1.611 4.096 3.667l.39 2.783h.762c2.021 0 3.627 1.703 3.627 3.75v7.9c0 2.047-1.606 3.75-3.627 3.75H2.627C.606 24 0 22.297 0 20.25v-7.9c0-2.047 1.606-3.75 3.627-3.75h.744l.38-2.783c.286-2.058 2.025-3.663 4.098-3.67 2.076-.007 3.826 1.584 4.131 3.638"
            />
          </svg>
          <div class="absolute inset-0 rounded-full bg-emerald-400/20 animate-ping"></div>
        </div>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </Transition>
    </button>

    <!-- Chat panel -->
    <Transition name="chat-panel">
      <div v-show="isOpen" class="fixed bottom-24 right-6 z-50 w-96 h-[540px] bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-5 py-4 flex items-center justify-between flex-shrink-0">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path
                d="M12.997 6.71c.305-2.054 2.056-3.645 4.131-3.638 2.076.007 3.81 1.611 4.096 3.667l.39 2.783h.762c2.021 0 3.627 1.703 3.627 3.75v7.9c0 2.047-1.606 3.75-3.627 3.75H2.627C.606 24 0 22.297 0 20.25v-7.9c0-2.047 1.606-3.75 3.627-3.75h.744l.38-2.783c.286-2.058 2.025-3.663 4.098-3.67 2.076-.007 3.826 1.584 4.131 3.638"
              />
            </svg>
            <div>
              <p class="font-semibold">AI Assistant</p>
              <p class="text-xs text-white/70">Sonik Intelligence</p>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button class="w-8 h-8 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
            </button>
            <button class="w-8 h-8 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors" @click="isOpen = false">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Quick chips -->
        <div class="px-4 py-2 border-b border-slate-100 bg-emerald-50/50 flex gap-2 overflow-x-auto scrollbar-hide">
          <button
            v-for="chip in quickChips"
            :key="chip"
            class="bg-white border border-emerald-200 text-emerald-700 text-xs px-3 py-1.5 rounded-full hover:bg-emerald-50 whitespace-nowrap transition-colors"
            @click="handleQuickChip(chip)"
          >
            {{ chip }}
          </button>
        </div>

        <!-- Messages -->
        <div ref="messagesEl" class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          <div v-for="(message, i) in messages" :key="i" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start gap-2'">
            <!-- AI message left icon -->
            <svg v-if="message.role === 'ai'" class="w-5 h-5 text-emerald-500 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
            </svg>

            <!-- Message content -->
            <div class="flex flex-col" :class="message.role === 'user' ? 'items-end' : 'items-start'">
              <div
                class="text-sm px-4 py-2.5 rounded-2xl max-w-xs"
                :class="
                  message.role === 'user'
                    ? 'bg-emerald-500 text-white rounded-br-sm'
                    : 'bg-slate-100 text-slate-800 rounded-bl-sm'
                "
              >
                {{ message.text }}
              </div>

              <!-- Links -->
              <div v-if="message.links && message.links.length > 0" class="flex flex-wrap gap-2 mt-2">
                <button
                  v-for="link in message.links"
                  :key="link.route"
                  class="bg-white border border-slate-200 text-emerald-600 text-xs px-2.5 py-1 rounded-full hover:bg-emerald-50 transition-colors"
                  @click="navigateLink(link.route)"
                >
                  {{ link.label }}
                </button>
              </div>

              <!-- Time -->
              <p class="text-xs text-slate-400 mt-1">{{ message.time }}</p>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="isTyping" class="flex justify-start gap-2">
            <svg class="w-5 h-5 text-emerald-500 flex-shrink-0 mt-1" fill="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" />
            </svg>
            <div class="bg-slate-100 text-slate-800 text-sm px-4 py-2.5 rounded-2xl rounded-bl-sm flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>

        <!-- Input area -->
        <div class="border-t border-slate-100 px-4 py-3 flex items-center gap-2 bg-white flex-shrink-0">
          <input
            v-model="inputText"
            type="text"
            placeholder="Ask anything..."
            class="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent transition"
            @keyup.enter="sendMessage"
          />
          <button
            class="w-9 h-9 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white flex items-center justify-center transition-colors"
            @click="sendMessage"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
