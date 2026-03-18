<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const router = useRouter()

const mockSales = Array.from({ length: 25 }, (_, i) => ({
  id: `#BL-${String(234 - i).padStart(5, '0')}`,
  date: new Date(2025, 5, 7 - Math.floor(i / 5)).toISOString(),
  customer: ['Walk-in', 'Ramesh Patil', 'Sunita Sharma', 'Vikram Nair', 'Mohan Verma'][i % 5],
  items: Math.floor(Math.random() * 15) + 1,
  total: Math.floor(Math.random() * 5000) + 200,
  employee: ['Ravi Kumar', 'Priya Singh', 'Ankit Rao'][i % 3],
  mode: ['cash', 'upi', 'credit'][i % 3],
}))

const filters = ref({
  dateFrom: '',
  dateTo: '',
  employee: '',
  mode: '',
  minAmount: '',
  maxAmount: '',
})

const currentPage = ref(1)
const pageSize = 10

const filteredRows = computed(() => {
  return mockSales.filter((row) => {
    if (filters.value.employee && row.employee !== filters.value.employee) return false
    if (filters.value.mode && row.mode !== filters.value.mode) return false
    if (filters.value.minAmount && row.total < parseFloat(filters.value.minAmount)) return false
    if (filters.value.maxAmount && row.total > parseFloat(filters.value.maxAmount)) return false
    return true
  })
})

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRows.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.ceil(filteredRows.value.length / pageSize)
})

const totalTransactions = computed(() => filteredRows.value.length)
const totalRevenue = computed(() => filteredRows.value.reduce((sum, r) => sum + r.total, 0))
const avgBillValue = computed(() => {
  return totalTransactions.value > 0 ? totalRevenue.value / totalTransactions.value : 0
})

const columns = [
  { key: 'id', label: 'Bill ID' },
  { key: 'date', label: 'Date & Time' },
  { key: 'customer', label: 'Customer' },
  { key: 'items', label: 'Items', align: 'center' },
  { key: 'total', label: 'Amount', align: 'right' },
  { key: 'employee', label: 'Employee' },
  { key: 'mode', label: 'Mode', align: 'center' },
]

const handleViewSale = (row) => {
  router.push(`/sales/${row.id}`)
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Sales History</h1>
        <p class="text-sm text-slate-500 mt-1">Track all transactions and revenue</p>
      </div>

      <!-- Filters -->
      <Card>
        <div class="space-y-4">
          <div class="flex flex-wrap gap-4 items-end">
            <div class="flex-1 min-w-48">
              <label class="block text-xs font-semibold text-slate-400 uppercase mb-1">Date Range</label>
              <div class="flex gap-2">
                <Input v-model="filters.dateFrom" type="date" placeholder="From" />
                <Input v-model="filters.dateTo" type="date" placeholder="To" />
              </div>
            </div>

            <div class="w-48">
              <label class="block text-xs font-semibold text-slate-400 uppercase mb-1">Employee</label>
              <select v-model="filters.employee" class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400">
                <option value="">All Employees</option>
                <option>Ravi Kumar</option>
                <option>Priya Singh</option>
                <option>Ankit Rao</option>
              </select>
            </div>

            <div class="flex gap-2">
              <button
                v-for="mode in ['All', 'cash', 'upi', 'credit']"
                :key="mode"
                class="px-3 py-2.5 text-xs rounded-lg transition-colors whitespace-nowrap"
                :class="
                  (mode === 'All' && !filters.mode) || filters.mode === mode
                    ? 'bg-emerald-100 text-emerald-700 font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                "
                @click="filters.mode = mode === 'All' ? '' : mode"
              >
                {{ mode }}
              </button>
            </div>

            <div class="flex gap-2">
              <Button variant="primary" size="sm">Apply</Button>
              <Button
                variant="secondary"
                size="sm"
                @click="
                  filters = {
                    dateFrom: '',
                    dateTo: '',
                    employee: '',
                    mode: '',
                    minAmount: '',
                    maxAmount: '',
                  }
                "
              >
                Reset
              </Button>
            </div>
          </div>
        </div>
      </Card>

      <!-- Summary strip -->
      <div class="grid grid-cols-3 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Transactions</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ totalTransactions }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Revenue</p>
          <p class="font-mono text-3xl font-bold text-emerald-600 mt-2">{{ formatCurrency(totalRevenue) }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Bill Value</p>
          <p class="font-mono text-3xl font-bold text-blue-600 mt-2">{{ formatCurrency(avgBillValue) }}</p>
        </Card>
      </div>

      <!-- Table -->
      <Card padding="none">
        <Table
          :columns="columns"
          :rows="paginatedRows"
          striped
          hoverable
          @row-click="handleViewSale"
        >
          <template #date="{ value }">
            {{ formatDate(value, 'datetime') }}
          </template>
          <template #items="{ value }">
            <span class="bg-slate-100 text-slate-700 text-xs px-2.5 py-1 rounded-full font-medium">
              {{ value }} items
            </span>
          </template>
          <template #total="{ value }">
            <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(value) }}</span>
          </template>
          <template #mode="{ value }">
            <span
              class="text-xs px-2.5 py-1 rounded-full font-medium capitalize"
              :class="{
                'bg-emerald-100 text-emerald-700': value === 'cash',
                'bg-blue-100 text-blue-700': value === 'upi',
                'bg-amber-100 text-amber-700': value === 'credit',
              }"
            >
              {{ value }}
            </span>
          </template>
        </Table>
      </Card>

      <!-- Pagination -->
      <div class="flex items-center justify-center gap-2">
        <Button
          variant="secondary"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage = Math.max(1, currentPage - 1)"
        >
          ← Prev
        </Button>
        <div class="flex gap-1">
          <button
            v-for="page in totalPages"
            :key="page"
            class="w-8 h-8 rounded-lg text-sm font-medium transition-colors"
            :class="
              currentPage === page
                ? 'bg-emerald-500 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            "
            @click="currentPage = page"
          >
            {{ page }}
          </button>
        </div>
        <Button
          variant="secondary"
          size="sm"
          :disabled="currentPage === totalPages"
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
        >
          Next →
        </Button>
      </div>
    </div>
  </MainLayout>
</template>
