<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '../../layouts/AuthLayout.vue'
import Button from '../../components/ui/Button.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatDuration, formatDurationHM, formatDate } from '../../utils/dateFormatter'

const router = useRouter()

const shiftActive = ref(false)
const startTime = ref(null)
const currentTime = ref(new Date())
const elapsedSeconds = ref(0)
const showConfirmModal = ref(false)

const mockEmployee = {
  name: 'Ravi Kumar',
  role: 'Sales Staff',
  initials: 'RK',
}

let clockInterval = null
let elapsedInterval = null

const formatTime = (date) => {
  return new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  }).format(date)
}

const startShift = () => {
  shiftActive.value = true
  startTime.value = new Date()
  elapsedSeconds.value = 0

  elapsedInterval = setInterval(() => {
    elapsedSeconds.value++
  }, 1000)
}

const endShift = () => {
  showConfirmModal.value = true
}

const confirmEndShift = () => {
  shiftActive.value = false
  if (elapsedInterval) clearInterval(elapsedInterval)
  showConfirmModal.value = false
  router.push('/billing')
}

onMounted(() => {
  clockInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval)
  if (elapsedInterval) clearInterval(elapsedInterval)
})
</script>

<template>
  <AuthLayout>
    <div class="max-w-lg mx-auto px-4">
      <!-- Main card -->
      <div class="bg-white rounded-3xl border border-slate-100 shadow-sm p-8">
        <!-- Employee header -->
        <div class="flex items-center gap-4 pb-6 border-b border-slate-100 mb-6">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white font-semibold text-sm">
            {{ mockEmployee.initials }}
          </div>
          <div>
            <h2 class="text-xl font-semibold text-slate-900">{{ mockEmployee.name }}</h2>
            <p class="text-sm text-slate-500">{{ mockEmployee.role }}</p>
          </div>
        </div>

        <!-- Clock section -->
        <div class="text-center mb-8">
          <p class="font-mono text-5xl font-bold text-slate-900">
            {{ formatTime(currentTime) }}
          </p>
          <p class="text-sm text-slate-500 mt-2">{{ formatDate(currentTime, 'full') }}</p>
        </div>

        <!-- Shift status -->
        <div class="bg-slate-50 rounded-2xl p-4 mb-6">
          <div class="flex items-center gap-2 mb-2">
            <div
              class="w-2 h-2 rounded-full"
              :class="shiftActive ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'"
            ></div>
            <p :class="shiftActive ? 'text-emerald-600 font-semibold' : 'text-slate-600'">
              {{ shiftActive ? 'Shift Active' : 'Shift Not Started' }}
            </p>
          </div>
          <p v-if="shiftActive" class="font-mono text-sm text-slate-600 ml-4">
            Duration: {{ formatDuration(elapsedSeconds) }}
          </p>
          <p class="text-sm text-slate-500 ml-4 mt-1">Today's Hours: {{ formatDurationHM(elapsedSeconds) }}</p>
        </div>

        <!-- Action buttons -->
        <div class="mb-6">
          <Button
            v-if="!shiftActive"
            variant="primary"
            size="lg"
            fullWidth
            @click="startShift"
          >
            ▶ Start Shift
          </Button>
          <Button
            v-else
            variant="danger"
            size="lg"
            fullWidth
            @click="endShift"
          >
            ⏹ End Shift
          </Button>
        </div>

        <!-- Info note -->
        <div class="bg-amber-50 border border-amber-200 rounded-xl p-3 text-sm text-amber-700 flex items-center gap-2">
          <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          All billing actions are locked until your shift is started.
        </div>
      </div>
    </div>

    <!-- End shift confirmation modal -->
    <Modal v-model="showConfirmModal" title="End Shift?" size="sm">
      <p class="text-slate-600 text-sm">
        Are you sure? Your shift duration will be recorded as
        <span class="font-semibold text-slate-900">{{ formatDurationHM(elapsedSeconds) }}</span>
      </p>
      <template #footer>
        <Button variant="secondary" size="sm" @click="showConfirmModal = false">
          Cancel
        </Button>
        <Button variant="danger" size="sm" @click="confirmEndShift">
          End Shift
        </Button>
      </template>
    </Modal>
  </AuthLayout>
</template>
