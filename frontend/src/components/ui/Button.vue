<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'danger', 'ghost'].includes(v),
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v),
  },
  loading: Boolean,
  disabled: Boolean,
  icon: String,
  iconRight: Boolean,
  fullWidth: Boolean,
})

const emit = defineEmits(['click'])

const baseClasses = 'font-medium rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2'

const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-emerald-500 hover:bg-emerald-600 text-white',
    secondary: 'bg-white border border-slate-200 hover:bg-slate-50 text-slate-700',
    danger: 'bg-red-50 hover:bg-red-100 text-red-600 border border-red-200',
    ghost: 'bg-transparent hover:bg-slate-100 text-slate-600',
  }
  return variants[props.variant]
})

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-3 text-base',
  }
  return sizes[props.size]
})

const disabledClasses = computed(() => {
  return props.disabled || props.loading ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''
})

const widthClasses = computed(() => {
  return props.fullWidth ? 'w-full' : ''
})

const finalClasses = computed(() => {
  return `${baseClasses} ${variantClasses.value} ${sizeClasses.value} ${disabledClasses.value} ${widthClasses.value}`
})

const handleClick = () => {
  if (!props.disabled && !props.loading) {
    emit('click')
  }
}
</script>

<template>
  <button :class="finalClasses" :disabled="disabled || loading" @click="handleClick">
    <!-- Left icon -->
    <svg v-if="icon && !iconRight" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <!-- Icon will be injected by parent or use a generic icon component -->
      <circle cx="10" cy="10" r="8" />
    </svg>

    <!-- Loading spinner -->
    <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>

    <!-- Label -->
    <slot />

    <!-- Right icon -->
    <svg v-if="icon && iconRight" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
      <circle cx="10" cy="10" r="8" />
    </svg>
  </button>
</template>
