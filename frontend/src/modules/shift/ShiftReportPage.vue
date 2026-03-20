<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore.js'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const router = useRouter()
const authStore = useAuthStore()

const mockShifts = [
  { id: 1, employee: 'Ravi Kumar', date: '2025-06-05', startTime: '08:00', endTime: '16:00', duration: '8h', sales: 4200, transactions: 12, anomaly: null, performance: 92 },
  { id: 2, employee: 'Priya Singh', date: '2025-06-05', startTime: '10:00', endTime: '18:00', duration: '8h', sales: 3800, transactions: 10, anomaly: null, performance: 88 },
  { id: 3, employee: 'Amit Kumar', date: '2025-06-05', startTime: '08:00', endTime: '14:00', duration: '6h', sales: 1200, transactions: 4, anomaly: 'Low Sales', performance: 56 },
  { id: 4, employee: 'Neha Verma', date: '2025-06-04', startTime: '08:00', endTime: '16:00', duration: '8h', sales: 5100, transactions: 15, anomaly: null, performance: 95 },
  { id: 5, employee: 'Vikram Desai', date: '2025-06-04', startTime: '08:00', endTime: '17:00', duration: '9h', sales: 6200, transactions: 18, anomaly: null, performance: 98 },
  { id: 6, employee: 'Anjali Nair', date: '2025-06-04', startTime: '10:30', endTime: '17:30', duration: '7h', sales: 800, transactions: 2, anomaly: 'Extended Break', performance: 35 },
]

// For employee, get only their current shift
const currentEmployeeShift = computed(() => {
  if (authStore.isOwner) return null
  return mockShifts.find(s => s.employee === authStore.user?.name)
})

const filterEmployee = ref('all')
const filterDate = ref('all')

const filteredShifts = computed(() => {
  if (authStore.isEmployee && currentEmployeeShift.value) {
    // Employees only see their own shift
    return [currentEmployeeShift.value]
  }
  // Owners see all shifts
  return mockShifts.filter((shift) => {
    if (filterEmployee.value !== 'all' && shift.employee !== filterEmployee.value) return false
    if (filterDate.value !== 'all' && shift.date !== filterDate.value) return false
    return true
  })
})

const anomalyShifts = computed(() => {
  return filteredShifts.value.filter((s) => s.anomaly)
})

const employees = ['Ravi Kumar', 'Priya Singh', 'Amit Kumar', 'Neha Verma', 'Vikram Desai', 'Anjali Nair']
const dates = ['2025-06-05', '2025-06-04', '2025-06-03']

const totalSales = computed(() => {
  return filteredShifts.value.reduce((sum, s) => sum + s.sales, 0)
})

const totalTransactions = computed(() => {
  return filteredShifts.value.reduce((sum, s) => sum + s.transactions, 0)
})

const avgPerformance = computed(() => {
  if (filteredShifts.value.length === 0) return 0
  const avg = filteredShifts.value.reduce((sum, s) => sum + s.performance, 0) / filteredShifts.value.length
  return Math.round(avg)
})

const performanceColor = (score) => {
  if (score >= 90) return 'text-emerald-600'
  if (score >= 80) return 'text-blue-600'
  if (score >= 70) return 'text-amber-600'
  return 'text-red-600'
}

const handleEndShift = () => {
  // End shift using auth store
  authStore.endShift()
  // Redirect to login
  router.push('/login')
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div v-if="authStore.isOwner" class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Shift Reports</h1>
          <p class="text-sm text-slate-500 mt-1">Monitor employee shifts and performance metrics</p>
        </div>
      </div>

      <!-- Employee Header -->
      <div v-if="authStore.isEmployee" class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Shift Report</h1>
          <p class="text-sm text-slate-500 mt-1">Summary of your shift sales and activity</p>
        </div>
        <Button variant="danger" @click="handleEndShift">
          End Shift
        </Button>
      </div>

      <!-- Filters (Owner only) -->
      <Card v-if="authStore.isOwner">
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label class="block text-sm font-medium text-slate-700 mb-1">Employee</label>
            <select
              v-model="filterEmployee"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
            >
              <option value="all">All Employees</option>
              <option v-for="emp in employees" :key="emp" :value="emp">
                {{ emp }}
              </option>
            </select>
          </div>
          <div class="flex-1">
            <label class="block text-sm font-medium text-slate-700 mb-1">Date</label>
            <select
              v-model="filterDate"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
            >
              <option value="all">All Dates</option>
              <option v-for="date in dates" :key="date" :value="date">
                {{ formatDate(date, 'short') }}
              </option>
            </select>
          </div>
        </div>
      </Card>

      <!-- Anomalies Panel (Owner only) -->
      <Card v-if="authStore.isOwner && anomalyShifts.length > 0" class="bg-red-50 border-red-100">
        <template #header>
          <div class="flex items-center gap-2">
            <span class="text-2xl">⚠️</span>
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
                <p class="text-sm text-slate-500">{{ formatDate(shift.date, 'short') }} • {{ shift.startTime }} - {{ shift.endTime }}</p>
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

      <!-- Summary Stats (Owner only) -->
      <div v-if="authStore.isOwner" class="grid grid-cols-4 gap-4">
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

      <!-- Employee Summary (Employee only) -->
      <div v-if="authStore.isEmployee && currentEmployeeShift" class="grid grid-cols-3 gap-4">
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

      <!-- Shifts Table / Employee Report -->
      <Card v-if="authStore.isOwner" padding="none">
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
            {{ row.startTime }} - {{ row.endTime }}
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

      <!-- Employee Shift Report (Employee only) -->
      <Card v-if="authStore.isEmployee && currentEmployeeShift" class="bg-gradient-to-br from-slate-50 to-slate-100">
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
              <p class="text-sm font-semibold text-slate-900 mt-1">{{ currentEmployeeShift.startTime }} - {{ currentEmployeeShift.endTime }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-slate-500 uppercase">Duration</p>
              <p class="text-sm font-semibold text-slate-900 mt-1">{{ currentEmployeeShift.duration }}</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  </MainLayout>
</template>
