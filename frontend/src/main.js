// Sonik — Smart Retail Management System
// Vue 3 + Vue Router + Pinia + TailwindCSS
// All pages use dummy/mock data. Backend integration pending.

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './assets/styles/tailwind.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.mount('#app')