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

const features = [
  { icon: '📊', title: 'Real-time Analytics', desc: 'Track your sales and inventory live' },
  { icon: '🚀', title: 'Fast & Reliable', desc: 'Lightning-quick performance' },
  { icon: '🔒', title: 'Secure', desc: 'Your data is protected' },
]
</script>

<template>
  <AuthLayout>
    <div class="min-h-screen flex items-center justify-center px-4 py-6">
      <!-- Main container -->
      <div class="w-full max-w-7xl">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <!-- Left side - Features section -->
          <Transition name="slide-in-left">
            <div class="hidden lg:flex flex-col justify-center space-y-8">
              <!-- Header -->
              <div>
                <div class="flex items-center gap-4 mb-6">
                  <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600 flex items-center justify-center shadow-lg">
                    <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59V20h3.41L17.71 8.71 20 11V6m0-6h-6.59l1.41 1.41L4 12.59V10H0v10h10v-4h2.59l8.15-8.15L24 0z" />
                    </svg>
                  </div>
                  <div>
                    <h1 class="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">Sonik</h1>
                    <p class="text-slate-500 font-medium">Retail Management Platform</p>
                  </div>
                </div>
                <p class="text-lg text-slate-600 font-light">Streamline your retail business with powerful tools for inventory, sales, and customer management</p>
              </div>

              <!-- Feature cards -->
              <div class="space-y-4">
                <div v-for="(feature, idx) in features" :key="idx" class="flex gap-4 p-4 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 hover:from-slate-100 hover:to-slate-150 transition-all duration-300 border border-slate-200 hover:border-emerald-300">
                  <div class="text-3xl flex-shrink-0">{{ feature.icon }}</div>
                  <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-slate-900">{{ feature.title }}</h3>
                    <p class="text-sm text-slate-500 mt-1">{{ feature.desc }}</p>
                  </div>
                </div>
              </div>

              <!-- Decorative element -->
              <div class="pt-8 mt-8 border-t border-slate-200">
                <div class="inline-flex items-center gap-2 text-sm text-slate-600">
                  <div class="flex -space-x-2">
                    <div class="w-8 h-8 rounded-full bg-emerald-400 border-2 border-white"></div>
                    <div class="w-8 h-8 rounded-full bg-teal-400 border-2 border-white"></div>
                    <div class="w-8 h-8 rounded-full bg-cyan-400 border-2 border-white"></div>
                  </div>
                  <span>Trusted by 1000+ retail stores</span>
                </div>
              </div>
            </div>
          </Transition>

          <!-- Right side - Login form -->
          <Transition name="scale-fade">
            <div class="flex justify-center">
              <div class="w-full max-w-sm">
                <!-- Form card -->
                <div class="bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
                  <!-- Mobile header (visible on small screens) -->
                  <div class="lg:hidden flex flex-col items-center gap-3 mb-8">
                    <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600 flex items-center justify-center shadow-lg">
                      <svg class="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59V20h3.41L17.71 8.71 20 11V6m0-6h-6.59l1.41 1.41L4 12.59V10H0v10h10v-4h2.59l8.15-8.15L24 0z" />
                      </svg>
                    </div>
                    <div class="text-center">
                      <h1 class="text-2xl font-bold text-slate-900">Sonik</h1>
                      <p class="text-xs text-slate-400">Retail Management</p>
                    </div>
                  </div>

                  <!-- Heading -->
                  <div class="mb-8">
                    <h2 class="text-2xl font-bold text-slate-900">Welcome back 👋</h2>
                    <p class="text-slate-500 text-sm mt-2">Sign in to access your store dashboard</p>
                  </div>

                  <!-- Form -->
                  <form class="space-y-5" @submit.prevent="handleSubmit">
                    <!-- Email input -->
                    <div>
                      <Input v-model="email" type="email" label="Email Address" placeholder="you@example.com" icon="envelope" />
                    </div>

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
                        class="mt-3 text-xs font-medium text-emerald-600 hover:text-emerald-700 transition-colors"
                        @click="showPassword = !showPassword"
                      >
                        {{ showPassword ? '✓ Hide' : 'Show' }} password
                      </button>
                    </div>

                    <!-- Remember & Forgot -->
                    <div class="flex items-center justify-between text-sm pt-2">
                      <label class="flex items-center gap-2 cursor-pointer group">
                        <input type="checkbox" class="w-4 h-4 rounded border-2 border-slate-300 accent-emerald-500 group-hover:border-emerald-400 transition-colors" />
                        <span class="text-slate-600 group-hover:text-slate-800 transition-colors">Remember me</span>
                      </label>
                      <a href="#" class="text-emerald-600 hover:text-emerald-700 font-medium transition-colors">Forgot?</a>
                    </div>

                    <!-- Error message -->
                    <Transition name="fade">
                      <div v-if="errorMsg" class="bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg p-4 text-sm flex items-start gap-3">
                        <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                        <span>{{ errorMsg }}</span>
                      </div>
                    </Transition>

                    <!-- Submit button -->
                    <Button variant="primary" size="lg" fullWidth :loading="isLoading" @click="handleSubmit" class="mt-6">
                      {{ isLoading ? 'Signing in...' : 'Sign In' }}
                    </Button>
                  </form>

                  <!-- Footer -->
                  <div class="mt-8 pt-8 border-t border-slate-100">
                    <p class="text-center text-xs text-slate-500">
                      By signing in, you agree to our
                      <a href="#" class="text-emerald-600 hover:underline">Terms of Service</a>
                      and
                      <a href="#" class="text-emerald-600 hover:underline">Privacy Policy</a>
                    </p>
                  </div>
                </div>

                <!-- Security badge -->
                <div class="mt-6 flex items-center justify-center gap-2 text-xs text-slate-500">
                  <svg class="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 11-1.414 1.414L10 7.414 6.707 10.707a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-slate-600">Your data is encrypted and secure</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </AuthLayout>
</template>

<style scoped>
.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.scale-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.slide-in-left-enter-active,
.slide-in-left-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-in-left-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-in-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
