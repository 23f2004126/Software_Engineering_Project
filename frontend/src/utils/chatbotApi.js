import axios from 'axios'

const rawChatbotBaseUrl = import.meta.env.VITE_CHATBOT_API_URL || 'http://127.0.0.1:8001'
const normalizedChatbotBaseUrl = rawChatbotBaseUrl.replace(/\/+$/, '')

const chatbotApi = axios.create({
  baseURL: normalizedChatbotBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default chatbotApi
