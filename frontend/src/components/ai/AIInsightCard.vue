<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (v) => ['warning', 'success', 'danger', 'info'].includes(v),
  },
  title: String,
  message: String,
  linkLabel: String,
  linkRoute: String,
  dismissible: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['dismiss', 'navigate'])

const isDismissed = ref(false)

const iconClasses = computed(() => {
  const classes = {
    warning: { bg: 'bg-amber-100', text: 'text-amber-600' },
    success: { bg: 'bg-emerald-100', text: 'text-emerald-600' },
    danger: { bg: 'bg-red-100', text: 'text-red-600' },
    info: { bg: 'bg-blue-100', text: 'text-blue-600' },
  }
  return classes[props.type] || classes.info
})

const handleDismiss = () => {
  isDismissed.value = true
  emit('dismiss')
}

const handleNavigate = () => {
  if (props.linkRoute) {
    router.push(props.linkRoute)
  }
  emit('navigate')
}

const handleCardClick = () => {
  if (props.linkRoute) {
    handleNavigate()
  }
}
</script>

<template>
  <Transition name="fade">
    <div
      v-show="!isDismissed"
      class="flex items-start gap-3 px-5 py-4 border-b border-slate-100 last:border-0 hover:bg-slate-50/50 transition-colors"
      :class="linkRoute ? 'cursor-pointer' : ''"
      @click="handleCardClick"
    >
      <!-- Icon -->
      <div
        class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
        :class="`${iconClasses.bg}`"
      >
        <svg class="w-5 h-5" :class="`${iconClasses.text}`" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="10" cy="10" r="8" />
        </svg>
      </div>

      <!-- Content -->
      <div class="flex-1">
        <p class="text-sm font-semibold text-slate-800">{{ title }}</p>
        <p class="text-xs text-slate-500 mt-0.5 leading-relaxed">{{ message }}</p>

        <!-- Link chip -->
        <button
          v-if="linkLabel"
          class="mt-1.5 bg-white border border-slate-200 text-emerald-600 text-xs px-2.5 py-1 rounded-full inline-flex items-center gap-1 hover:border-emerald-300 transition-colors"
          @click.stop="handleNavigate"
        >
          {{ linkLabel }}
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- Dismiss button -->
      <button
        v-if="dismissible"
        class="w-6 h-6 rounded-lg text-slate-300 hover:text-slate-500 hover:bg-slate-100 transition-colors flex-shrink-0"
        @click.stop="handleDismiss"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
