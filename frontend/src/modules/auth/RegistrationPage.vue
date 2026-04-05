<!-- <script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { BarChart3, Package, ShieldCheck } from 'lucide-vue-next'

const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const phoneNo = ref('')
const role = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const isLoading = ref(false)

const roleOptions = [
  { label: 'Supervisor', value: 'supervisor' },
  { label: 'Sales Staff', value: 'sales_staff' },
  { label: 'Store Manager', value: 'store_manager' },
  { label: 'Inventory Manager', value: 'inventory_manager' },
]

const handleSubmit = () => {
  errorMsg.value = ''
  successMsg.value = ''

  if (!name.value.trim()) {
    errorMsg.value = 'Please enter your name'
    return
  }

  if (!email.value.includes('@')) {
    errorMsg.value = 'Please enter a valid email address'
    return
  }

  if (password.value.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters'
    return
  }

  if (!phoneNo.value.trim()) {
    errorMsg.value = 'Please enter your phone number'
    return
  }

  if (!role.value) {
    errorMsg.value = 'Please select a role'
    return
  }

  isLoading.value = true

  setTimeout(() => {
    successMsg.value = 'Registration successful! Redirecting to login...'
    isLoading.value = false
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  }, 1500)
}

const features = [
  { 
    icon: BarChart3, 
    title: 'Smart Sales Analytics', 
    desc: 'Real-time insights into your store performance' 
  },
  { 
    icon: Package, 
    title: 'Real-time Inventory', 
    desc: 'Track stock levels across your store' 
  },
  { 
    icon: ShieldCheck, 
    title: 'Supplier & Credit Tracking', 
    desc: 'Manage relationships and payment terms' 
  },
]
</script> -->
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { BarChart3, Package, ShieldCheck } from 'lucide-vue-next'
import api from '@/utils/api'   // ✅ IMPORTANT

const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const phoneNo = ref('')
const role = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const isLoading = ref(false)

const roleOptions = [
  { label: 'Supervisor', value: 'Supervisor' },
  { label: 'Sales Staff', value: 'Sales_staff' },
  { label: 'Store Manager', value: 'Store_manager' },
  { label: 'Inventory Manager', value: 'Inventory_manager' },
]

const handleSubmit = async () => {
  errorMsg.value = ''
  successMsg.value = ''

  // ✅ Validation
  if (!name.value.trim()) {
    errorMsg.value = 'Please enter your name'
    return
  }

  if (!email.value.includes('@')) {
    errorMsg.value = 'Please enter a valid email address'
    return
  }

  if (password.value.length < 8) {
    errorMsg.value = 'Password must be at least 8 characters'
    return
  }

  // Check for special character
  if (!/[^a-zA-Z0-9]/.test(password.value)) {
    errorMsg.value = 'Password must contain at least one special character (!@#$%^&*)'
    return
  }

  if (!phoneNo.value.trim()) {
    errorMsg.value = 'Please enter your phone number'
    return
  }

  if (!/^\d{10}$/.test(phoneNo.value.trim())) {
    errorMsg.value = 'Phone number must be exactly 10 digits'
    return
  }

  if (!role.value) {
    errorMsg.value = 'Please select a role'
    return
  }

  try {
    isLoading.value = true

    // ✅ CALL BACKEND API
    await api.post('/api/users/register', {
      name: name.value,
      email: email.value,
      password: password.value,
      phone: phoneNo.value,   // match backend field
      role: role.value
    })

    successMsg.value = 'Registration successful! Redirecting to login...'

    // reset form
    name.value = ''
    email.value = ''
    password.value = ''
    phoneNo.value = ''
    role.value = ''

    setTimeout(() => {
      router.push('/login')
    }, 1500)

  } catch (error) {
    console.error('Registration error:', error)
    console.error('Response data:', error.response?.data)
    console.error('Status code:', error.response?.status)

    // Better error handling
    if (error.response?.status === 400) {
      errorMsg.value = error.response.data?.detail || 'Registration failed. Please check your input.'
    } else if (error.response?.data?.detail) {
      errorMsg.value = error.response.data.detail
    } else if (error.message === 'Network Error') {
      errorMsg.value = 'Unable to connect to server. Please check if the backend is running.'
    } else if (error.response?.status === 422) {
      // Validation error from Pydantic
      const errors = error.response.data?.detail
      if (Array.isArray(errors)) {
        errorMsg.value = errors.map(e => e.msg).join(', ')
      } else {
        errorMsg.value = 'Validation error. Please check your input.'
      }
    } else {
      errorMsg.value = error.message || 'Something went wrong. Please try again.'
    }

  } finally {
    isLoading.value = false
  }
}

const features = [
  { 
    icon: BarChart3, 
    title: 'Smart Sales Analytics', 
    desc: 'Real-time insights into your store performance' 
  },
  { 
    icon: Package, 
    title: 'Real-time Inventory', 
    desc: 'Track stock levels across your store' 
  },
  { 
    icon: ShieldCheck, 
    title: 'Supplier & Credit Tracking', 
    desc: 'Manage relationships and payment terms' 
  },
]
</script>
<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-50 to-white">
    <!-- Header -->
    <div class="border-b border-slate-200 bg-white/50 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59V20h3.41L17.71 8.71 20 11V6m0-6h-6.59l1.41 1.41L4 12.59V10H0v10h10v-4h2.59l8.15-8.15L24 0z" />
          </svg>
        </div>
        <span class="text-lg font-semibold text-slate-900">Sonik</span>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-6 py-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        
        <!-- Left side - Marketing -->
        <Transition name="fade-in-left">
          <div class="space-y-10">
            <!-- Headline -->
            <div class="space-y-4">
              <h1 class="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                Join Our Team
              </h1>
              <p class="text-xl text-slate-600 leading-relaxed">
                Register as an employee and start managing your retail store with smart tools.
              </p>
            </div>

            <!-- Features -->
            <div class="space-y-4">
              <div v-for="(feature, idx) in features" :key="idx" class="flex gap-4">
                <div class="flex-shrink-0">
                  <div class="flex items-center justify-center h-12 w-12 rounded-lg bg-emerald-100">
                    <component :is="feature.icon" class="h-6 w-6 text-emerald-600" />
                  </div>
                </div>
                <div>
                  <h3 class="text-base font-semibold text-slate-900">{{ feature.title }}</h3>
                  <p class="text-sm text-slate-600 mt-1">{{ feature.desc }}</p>
                </div>
              </div>
            </div>

            <!-- Illustration -->
            <div class="pt-8">
              <img 
                src="../../assets/illustrations/Grocery shopping-cuate.svg" 
                alt="Retail dashboard illustration"
                class="w-full max-w-lg mx-auto lg:mx-0"
              />
            </div>
          </div>
        </Transition>

        <!-- Right side - Registration Form -->
        <Transition name="fade-in-right">
          <div class="flex items-center justify-center lg:justify-start">
            <div class="w-full max-w-sm">
              <!-- Card -->
              <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
                
                <!-- Form Heading -->
                <div class="mb-8">
                  <h2 class="text-2xl font-bold text-slate-900">Employee Registration</h2>
                  <p class="text-slate-600 text-sm mt-2">Create your employee account</p>
                </div>

                <!-- Form -->
                <form class="space-y-5" @submit.prevent="handleSubmit">
                  
                  <!-- Name -->
                  <div>
                    <label class="block text-sm font-medium text-slate-900 mb-2">
                      Name
                    </label>
                    <input
                      v-model="name"
                      type="text"
                      placeholder="John Doe"
                      class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                    />
                  </div>

                  <!-- Email -->
                  <div>
                    <label class="block text-sm font-medium text-slate-900 mb-2">
                      Email Address
                    </label>
                    <input
                      v-model="email"
                      type="email"
                      placeholder="you@example.com"
                      class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                    />
                  </div>

                  <!-- Password -->
                  <div>
                    <label class="block text-sm font-medium text-slate-900 mb-2">
                      Password
                    </label>
                    <input
                      v-model="password"
                      type="password"
                      placeholder="••••••••"
                      class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                    />
                  </div>

                  <!-- Phone Number -->
                  <div>
                    <label class="block text-sm font-medium text-slate-900 mb-2">
                      Phone Number
                    </label>
                    <input
                      v-model="phoneNo"
                      type="tel"
                      placeholder="+1 (234) 567-8900"
                      class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
                    />
                  </div>

                  <!-- Role -->
                  <div>
                    <label class="block text-sm font-medium text-slate-900 mb-2">
                      Role
                    </label>
                    <select
                      v-model="role"
                      class="w-full px-4 py-2.5 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all bg-white"
                    >
                      <option value="">Select a role</option>
                      <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </option>
                    </select>
                  </div>

                  <!-- Error Message -->
                  <Transition name="fade">
                    <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3.5 text-sm flex items-start gap-3">
                      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                      <span>{{ errorMsg }}</span>
                    </div>
                  </Transition>

                  <!-- Success Message -->
                  <Transition name="fade">
                    <div v-if="successMsg" class="bg-green-50 border border-green-200 text-green-700 rounded-lg p-3.5 text-sm flex items-start gap-3">
                      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                      <span>{{ successMsg }}</span>
                    </div>
                  </Transition>

                  <!-- Submit Button -->
                  <button
                    :disabled="isLoading"
                    class="w-full px-4 py-2.5 rounded-lg bg-emerald-600 text-white font-semibold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                  >
                    <svg v-if="isLoading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isLoading ? 'Registering...' : 'Register' }}
                  </button>

                </form>

                <!-- Footer -->
                <div class="mt-8 pt-6 border-t border-slate-200">
                  <p class="text-center text-xs text-slate-600">
                    Already have an account?
                    <router-link to="/login" class="text-emerald-600 hover:text-emerald-700 font-medium">
                      Sign in
                    </router-link>
                  </p>
                </div>

              </div>

              <!-- Trust Badge -->
              <div class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-600">
                <svg class="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span>Secure • SSL Encrypted</span>
              </div>

            </div>
          </div>
        </Transition>

      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-in-left-enter-active,
.fade-in-right-enter-active {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-in-left-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-in-right-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>