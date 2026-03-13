<script setup></script>

<template>
  <div class="relative min-h-screen bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 overflow-hidden" :style="{ animation: 'hueRotate 10s ease-in-out infinite alternate' }">
    <!-- Decorative blurred circles -->
    <div class="absolute -top-48 -left-32 w-96 h-96 bg-white/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-20 -right-16 w-72 h-72 bg-teal-300/20 rounded-full blur-2xl pointer-events-none"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-emerald-300/10 rounded-full blur-2xl pointer-events-none"></div>

    <!-- Content -->
    <div class="relative z-10 flex items-center justify-center min-h-screen px-4">
      <slot />
    </div>

    <!-- Footer -->
    <p class="absolute bottom-6 left-0 right-0 text-white/50 text-xs text-center">
      © 2025 Sonik. Built for smart retailers.
    </p>
  </div>
</template>

<style scoped>
@keyframes hueRotate {
  from {
    filter: hue-rotate(0deg);
  }
  to {
    filter: hue-rotate(15deg);
  }
}
</style>
