// Sonik — Smart Retail Management System
// Vue 3 + Vue Router + TailwindCSS
// All pages use dummy/mock data. Backend integration pending.

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import './assets/styles/tailwind.css'

createApp(App).use(router).mount('#app')