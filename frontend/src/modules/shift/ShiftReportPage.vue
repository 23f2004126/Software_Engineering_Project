<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore.js'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { shiftReportService } from '../../services/apiService.js'

const router = useRouter()
const authStore = useAuthStore()
const shifts = ref([])
const loading = ref(false)
const error = ref('')
const filterEmployee = ref('all')
const filterDate = ref(new Date().toISOString().split('T')[0])

const currentEmployeeShift = computed(() => {
  if (authStore.isOwner) return null
  return shifts.value[0] || null
})

const filteredShifts = computed(() => {
  if (authStore.isEmployee) {
    return currentEmployeeShift.value ? [currentEmployeeShift.value] : []
  }

  return shifts.value.filter((shift) => {
    if (filterEmployee.value !== 'all' && shift.employee !== filterEmployee.value) return false
    if (filterDate.value && shift.date !== filterDate.value) return false
    return true
  })
})

const anomalyShifts = computed(() => filteredShifts.value.filter((shift) => shift.anomaly))
const employees = computed(() => [...new Set(shifts.value.map((shift) => shift.employee))])
const totalSales = computed(() => filteredShifts.value.reduce((sum, shift) => sum + shift.sales, 0))
const totalTransactions = computed(() => filteredShifts.value.reduce((sum, shift) => sum + shift.transactions, 0))
const avgPerformance = computed(() => {
  if (filteredShifts.value.length === 0) return 0
  const avg = filteredShifts.value.reduce((sum, shift) => sum + shift.performance, 0) / filteredShifts.value.length
  return Math.round(avg)
})

function formatDuration(minutes) {
  if (!minutes) return '0m'
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  if (hours === 0) return `${remainingMinutes}m`
  if (remainingMinutes === 0) return `${hours}h`
  return `${hours}h ${remainingMinutes}m`
}

function performanceColor(score) {
  if (score >= 90) return 'text-emerald-600'
  if (score >= 80) return 'text-blue-600'
  if (score >= 70) return 'text-amber-600'
  return 'text-red-600'
}

async function loadShiftReports() {
  loading.value = true
  error.value = ''
  try {
    const selectedEmployee = shifts.value.find((shift) => shift.employee === filterEmployee.value)
    shifts.value = await shiftReportService.getShiftReports({
      date: filterDate.value,
      userId: authStore.isOwner && filterEmployee.value !== 'all' ? selectedEmployee?.user_id : undefined,
    })
  } catch (err) {
    error.value = err.message || 'Failed to load shift reports'
  } finally {
    loading.value = false
  }
}

function handleEndShift() {
  authStore.endShift()
  router.push('/login')
}

onMounted(loadShiftReports)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <div v-if="authStore.isOwner" class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Shift Reports</h1>
          <p class="text-sm text-slate-500 mt-1">Monitor employee shifts and performance metrics</p>
        </div>
      </div>

      <div v-if="authStore.isEmployee" class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Shift Report</h1>
          <p class="text-sm text-slate-500 mt-1">Summary of your shift sales and activity</p>
        </div>
        <Button variant="danger" @click="handleEndShift">
          End Shift
        </Button>
      </div>

      <Card v-if="authStore.isOwner">
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label class="block text-sm font-medium text-slate-700 mb-1">Employee</label>
            <select
              v-model="filterEmployee"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
            >
              <option value="all">All Employees</option>
              <option v-for="employee in employees" :key="employee" :value="employee">
                {{ employee }}
              </option>
            </select>
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium text-slate-700 mb-1">Date</label>
            <input
              v-model="filterDate"
              type="date"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
            />
          </div>
          <Button variant="secondary" @click="loadShiftReports">
            Refresh
          </Button>
        </div>
      </Card>

      <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500">
        Loading shift reports...
      </div>
      <div v-else-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {{ error }}
      </div>

      <Card v-if="!loading && !error && authStore.isOwner && anomalyShifts.length > 0" class="bg-red-50 border-red-100">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="text-2xl">!</span>
            <div>
              <p class="font-semibold text-slate-900">Flagged Shifts ({{ anomalyShifts.length }})</p>
              <p class="text-xs text-slate-500">Unusual activity detected during these shifts</p>
            </div>
          </div>
        </template>

        <div class="space-y-3">
          <div v-for="shift in anomalyShifts" :key="shift.id" class="bg-white rounded-xl p-4 border-l-4 border-red-500">
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ shift.employee }}</p>
                <p class="text-sm text-slate-500">{{ formatDate(shift.date, 'short') }} • {{ shift.start_time || '--:--' }} - {{ shift.end_time || '--:--' }}</p>
              </div>
              <span class="bg-red-100 text-red-700 text-xs px-2.5 py-1 rounded-full font-semibold">
                {{ shift.anomaly }}
              </span>
            </div>
            <div class="mt-3 flex gap-6 text-sm">
              <div>
                <span class="text-slate-600">Sales:</span>
                <span class="font-semibold">{{ formatCurrency(shift.sales) }}</span>
              </div>
              <div>
                <span class="text-slate-600">Transactions:</span>
                <span class="font-semibold">{{ shift.transactions }}</span>
              </div>
              <div>
                <span class="text-slate-600">Performance:</span>
                <span class="font-semibold" :class="performanceColor(shift.performance)">{{ shift.performance }}%</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <div v-if="!loading && !error && authStore.isOwner" class="grid grid-cols-4 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Sales</p>
          <p class="font-mono text-3xl font-bold text-emerald-600 mt-2">{{ formatCurrency(totalSales) }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Transactions</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ totalTransactions }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Avg Performance</p>
          <p class="font-mono text-3xl font-bold text-blue-600 mt-2">{{ avgPerformance }}%</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Shifts Recorded</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ filteredShifts.length }}</p>
        </Card>
      </div>

      <div v-if="!loading && !error && authStore.isEmployee && currentEmployeeShift" class="grid grid-cols-3 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Today's Sales</p>
          <p class="font-mono text-3xl font-bold text-emerald-600 mt-2">{{ formatCurrency(currentEmployeeShift.sales) }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Transactions</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ currentEmployeeShift.transactions }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Performance</p>
          <p class="font-mono text-3xl font-bold text-blue-600 mt-2">{{ currentEmployeeShift.performance }}%</p>
        </Card>
      </div>

      <Card v-if="!loading && !error && authStore.isOwner" padding="none">
        <Table
          :columns="[
            { key: 'employee', label: 'Employee' },
            { key: 'date', label: 'Date' },
            { key: 'time', label: 'Time' },
            { key: 'duration', label: 'Duration' },
            { key: 'sales', label: 'Sales' },
            { key: 'transactions', label: 'Txn' },
            { key: 'performance', label: 'Performance' },
            { key: 'anomaly', label: 'Status' },
          ]"
          :rows="filteredShifts"
          striped
          hoverable
        >
          <template #date="{ value }">
            {{ formatDate(value, 'short') }}
          </template>
          <template #time="{ row }">
            {{ row.start_time || '--:--' }} - {{ row.end_time || '--:--' }}
          </template>
          <template #duration="{ row }">
            {{ formatDuration(row.duration_minutes) }}
          </template>
          <template #sales="{ value }">
            <span class="font-mono font-semibold">{{ formatCurrency(value) }}</span>
          </template>
          <template #performance="{ value }">
            <div class="flex items-center gap-2">
              <div class="w-20 h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full"
                  :class="value >= 90 ? 'bg-emerald-500' : value >= 80 ? 'bg-blue-500' : value >= 70 ? 'bg-amber-500' : 'bg-red-500'"
                  :style="{ width: `${value}%` }"
                ></div>
              </div>
              <span class="font-semibold text-sm" :class="performanceColor(value)">{{ value }}%</span>
            </div>
          </template>
          <template #anomaly="{ value }">
            <span v-if="value" class="text-xs px-2.5 py-1 rounded-full bg-red-100 text-red-700 font-semibold">
              {{ value }}
            </span>
            <span v-else class="text-xs px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700 font-semibold">
              Normal
            </span>
          </template>
        </Table>
      </Card>

      <Card v-if="!loading && !error && authStore.isEmployee && currentEmployeeShift" class="bg-gradient-to-br from-slate-50 to-slate-100">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold text-slate-900">Shift Details</h3>
              <p class="text-sm text-slate-600 mt-1">{{ formatDate(currentEmployeeShift.date, 'long') }}</p>
            </div>
            <span class="text-3xl" :class="currentEmployeeShift.performance >= 80 ? 'text-emerald-600' : 'text-amber-600'">
              ✓
            </span>
          </div>
          <div class="grid grid-cols-2 gap-4 pt-2 border-t border-slate-200">
            <div>
              <p class="text-xs font-semibold text-slate-500 uppercase">Shift Time</p>
              <p class="text-sm font-semibold text-slate-900 mt-1">{{ currentEmployeeShift.start_time || '--:--' }} - {{ currentEmployeeShift.end_time || '--:--' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-slate-500 uppercase">Duration</p>
              <p class="text-sm font-semibold text-slate-900 mt-1">{{ formatDuration(currentEmployeeShift.duration_minutes) }}</p>
            </div>
          </div>
        </div>
      </Card>

      <Card v-if="!loading && !error && filteredShifts.length === 0">
        <p class="text-sm text-slate-500">No shift data found for the selected date.</p>
      </Card>
    </div>
  </MainLayout>
</template>
