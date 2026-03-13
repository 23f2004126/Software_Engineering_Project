<script setup>
import { computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg', 'xl'].includes(v),
  },
  closable: {
    type: Boolean,
    default: true,
  },
  persistent: Boolean,
})

const emit = defineEmits(['update:modelValue', 'close'])

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-2xl',
  }
  return sizes[props.size]
})

const handleClose = () => {
  if (!props.persistent) {
    emit('update:modelValue', false)
    emit('close')
  }
}

const handleOverlayClick = () => {
  if (!props.persistent && props.closable) {
    handleClose()
  }
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape' && !props.persistent && props.closable) {
    handleClose()
  }
}

onMounted(() => {
  if (props.modelValue) {
    document.addEventListener('keydown', handleKeyDown)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-show="modelValue" class="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" @click="handleOverlayClick">
        <div class="bg-white rounded-2xl shadow-2xl w-full" :class="sizeClasses" @click.stop>
          <!-- Header -->
          <div v-if="title || closable" class="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 v-if="title" class="text-base font-semibold text-slate-900">
              {{ title }}
            </h2>
            <button v-if="closable" class="w-8 h-8 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 flex items-center justify-center transition" @click="handleClose">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Body -->
          <div class="px-6 py-5">
            <slot />
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-slate-100 bg-slate-50 rounded-b-2xl flex justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease-out, transform 0.2s ease-out;
}

.modal-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
