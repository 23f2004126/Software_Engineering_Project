<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  type: {
    type: String,
    default: 'text',
  },
  label: String,
  placeholder: String,
  error: String,
  hint: String,
  icon: String,
  iconRight: String,
  disabled: Boolean,
  required: Boolean,
  prefix: String,
  suffix: String,
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputRef = ref(null)

const inputClasses = computed(() => {
  let classes = 'w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent transition disabled:opacity-50 disabled:cursor-not-allowed'

  if (props.icon || props.prefix) classes += ' pl-10'
  if (props.iconRight || props.suffix) classes += ' pr-10'
  if (props.error) classes += ' border-red-300 focus:ring-red-400'

  return classes
})

const handleInput = (e) => {
  emit('update:modelValue', e.target.value)
}

const handleBlur = () => {
  emit('blur')
}

const handleFocus = () => {
  emit('focus')
}

const focus = () => {
  if (inputRef.value) {
    inputRef.value.focus()
  }
}

defineExpose({ focus })
</script>

<template>
  <div class="flex flex-col gap-1">
    <!-- Label -->
    <label v-if="label" class="text-sm font-medium text-slate-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Input wrapper -->
    <div class="relative">
      <!-- Left icon or prefix -->
      <div v-if="icon || prefix" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm flex items-center">
        <span v-if="prefix">{{ prefix }}</span>
        <!-- Icon SVG would go here if icon prop exists -->
      </div>

      <!-- Input field -->
      <input
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Right icon or suffix -->
      <div v-if="iconRight || suffix" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm flex items-center">
        <span v-if="suffix">{{ suffix }}</span>
        <!-- Icon SVG would go here if iconRight prop exists -->
      </div>
    </div>

    <!-- Error message -->
    <p v-if="error" class="text-xs text-red-500 flex items-center gap-1">
      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {{ error }}
    </p>

    <!-- Hint message -->
    <p v-if="hint && !error" class="text-xs text-slate-400">
      {{ hint }}
    </p>
  </div>
</template>
