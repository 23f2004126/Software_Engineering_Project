<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from './stores/authStore'
import AIChatModal from './components/ai/AIChatModal.vue'

const authStore = useAuthStore()
</script>

<template>
  <RouterView />
  <AIChatModal v-if="authStore.isOwner" />
</template>
