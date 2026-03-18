<script setup>
import Sidebar from '../components/layout/Sidebar.vue'
import Navbar from '../components/layout/Navbar.vue'
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-slate-50">
    <Sidebar />
    <div class="flex flex-col flex-1 overflow-hidden">
      <Navbar />
      <main class="flex-1 overflow-y-auto p-8">
        <Transition name="page">
          <slot />
        </Transition>
      </main>
    </div>
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
