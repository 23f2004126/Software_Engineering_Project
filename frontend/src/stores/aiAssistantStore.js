import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAIAssistantStore = defineStore('aiAssistant', () => {
  const isOpen = ref(false)
  const pendingPrompt = ref('')

  const open = () => {
    isOpen.value = true
  }

  const close = () => {
    isOpen.value = false
  }

  const openWithPrompt = (prompt = '') => {
    pendingPrompt.value = prompt
    isOpen.value = true
  }

  const consumePendingPrompt = () => {
    const prompt = pendingPrompt.value
    pendingPrompt.value = ''
    return prompt
  }

  return {
    isOpen,
    pendingPrompt,
    open,
    close,
    openWithPrompt,
    consumePendingPrompt,
  }
})
