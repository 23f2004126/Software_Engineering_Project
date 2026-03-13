<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../../layouts/AuthLayout.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'

const router = useRouter()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

const handleSubmit = () => {
  errorMsg.value = ''

  if (!email.value.includes('@')) {
    errorMsg.value = 'Please enter a valid email address'
    return
  }

  if (password.value.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters'
    return
  }

  isLoading.value = true

  setTimeout(() => {
    localStorage.setItem('sonik_auth', 'true')
    isLoading.value = false
    router.push('/dashboard')
  }, 1500)
}
</script>

<template>
  <AuthLayout>
    <Transition name="scale-fade">
      <div class="bg-white rounded-3xl shadow-[0_20px_60px_rgba(16,185,129,0.15)] p-10 w-full max-w-md">
        <!-- Logo area -->
        <div class="flex flex-col items-center gap-4 mb-8">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
            <svg class="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path
                d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59V20h3.41L17.71 8.71 20 11V6m0-6h-6.59l1.41 1.41L4 12.59V10H0v10h10v-4h2.59l8.15-8.15L24 0z"
              />
            </svg>
          </div>
          <div class="text-center">
            <h1 class="text-3xl font-bold text-slate-900">Sonik</h1>
            <p class="text-sm text-slate-400 mt-1">Retail Management</p>
          </div>
        </div>

        <!-- Heading -->
        <div class="mb-6">
          <h2 class="text-xl font-semibold text-slate-800">Welcome back 👋</h2>
          <p class="text-sm text-slate-500 mt-1">Sign in to your store account</p>
        </div>

        <!-- Form -->
        <form class="space-y-4" @submit.prevent="handleSubmit">
          <!-- Email input -->
          <Input v-model="email" type="email" label="Email / Phone" placeholder="you@example.com" icon="envelope" />

          <!-- Password input -->
          <div>
            <Input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              placeholder="••••••••"
              icon="lock"
            />
            <button
              type="button"
              class="mt-2 text-xs text-emerald-600 hover:text-emerald-700 font-medium"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Hide' : 'Show' }} password
            </button>
          </div>

          <!-- Remember & Forgot -->
          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" class="w-4 h-4 rounded border border-slate-300 accent-emerald-500" />
              <span class="text-slate-600">Remember me</span>
            </label>
            <a href="#" class="text-emerald-600 hover:underline font-medium">Forgot Password?</a>
          </div>

          <!-- Error message -->
          <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-600 rounded-xl p-3 text-sm flex items-center gap-2">
            <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            {{ errorMsg }}
          </div>

          <!-- Submit button -->
          <Button variant="primary" size="lg" fullWidth :loading="isLoading" @click="handleSubmit">
            Sign In
          </Button>
        </form>
      </div>
    </Transition>
  </AuthLayout>
</template>

<style scoped>
.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: all 0.3s ease;
}

.scale-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
