<script setup>
import { computed } from 'vue'

const props = defineProps({
  padding: {
    type: String,
    default: 'md',
    validator: (v) => ['none', 'sm', 'md', 'lg'].includes(v),
  },
  hover: Boolean,
  bordered: {
    type: Boolean,
    default: true,
  },
})

const paddingClasses = computed(() => {
  const padding = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }
  return padding[props.padding]
})

const baseClasses = computed(() => {
  let classes = 'bg-white rounded-2xl shadow-sm'
  if (props.bordered) classes += ' border border-slate-100'
  if (props.hover) classes += ' hover:-translate-y-0.5 hover:shadow-md transition-all duration-200 cursor-pointer'
  return classes
})
</script>

<template>
  <div :class="`${baseClasses}`">
    <!-- Header slot -->
    <div v-if="$slots.header" class="px-6 py-4 border-b border-slate-100">
      <slot name="header" />
    </div>

    <!-- Body (main slot) -->
    <div :class="paddingClasses">
      <slot />
    </div>

    <!-- Footer slot -->
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-slate-100 bg-slate-50 rounded-b-2xl">
      <slot name="footer" />
    </div>
  </div>
</template>
