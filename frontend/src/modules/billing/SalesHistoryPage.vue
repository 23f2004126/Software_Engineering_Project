<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { salesService } from '../../services/apiService.js'

const router = useRouter()

const sales = ref([])
const loading = ref(false)
const error = ref('')

const filters = ref({
  dateFrom: '',
  dateTo: '',
  payment_method: '',
  status: '',
})

const currentPage = ref(1)
const pageSize = 10

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sales.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.ceil(sales.value.length / pageSize)
})

const totalTransactions = computed(() => sales.value.length)
const totalRevenue = computed(() => sales.value.reduce((sum, r) => sum + (parseFloat(r.total_amount) || 0), 0))
const avgBillValue = computed(() => {
  return totalTransactions.value > 0 ? totalRevenue.value / totalTransactions.value : 0
})

const columns = [
  { key: 'receipt_number', label: 'Receipt #' },
  { key: 'bill_date', label: 'Date & Time' },
  { key: 'customer_name', label: 'Customer' },
  { key: 'total_amount', label: 'Amount', align: 'right' },
  { key: 'payment_method', label: 'Mode', align: 'center' },
  { key: 'status', label: 'Status', align: 'center' },
]

const fetchSalesHistory = async () => {
  try {
    loading.value = true
    error.value = ''

    const response = await salesService.getSalesHistory({
      startDate: filters.value.dateFrom,
      endDate: filters.value.dateTo,
      paymentMethod: filters.value.payment_method,
      status: filters.value.status
    })
    sales.value = response || []
    currentPage.value = 1
  } catch (err) {
    error.value = err.message || 'Failed to fetch sales history'
    console.error('Fetch sales error:', err)
    sales.value = []
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  fetchSalesHistory()
}

const resetFilters = () => {
  filters.value = {
    dateFrom: '',
    dateTo: '',
    payment_method: '',
    status: '',
  }
  fetchSalesHistory()
}

const handleViewSale = (row) => {
  router.push(`/sales/${row.bill_id}`)
}

onMounted(() => {
  fetchSalesHistory()
})
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Sales History</h1>
        <p class="text-sm text-slate-500 mt-1">Track all transactions and revenue</p>
      </div>

      <!-- Error message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
        <p class="text-sm text-red-700">{{ error }}</p>
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

            <div class="flex gap-2">
              <button
                v-for="mode in ['All', 'cash', 'upi', 'credit', 'card']"
                :key="mode"
                class="px-3 py-2.5 text-xs rounded-lg transition-colors whitespace-nowrap"
                :class="
                  (mode === 'All' && !filters.payment_method) || filters.payment_method === mode
                    ? 'bg-emerald-100 text-emerald-700 font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                "
                @click="filters.payment_method = mode === 'All' ? '' : mode"
              >
                {{ mode }}
              </button>
            </div>

            <div class="flex gap-2">
              <button
                v-for="st in ['All', 'paid', 'pending', 'cancelled']"
                :key="st"
                class="px-3 py-2.5 text-xs rounded-lg transition-colors whitespace-nowrap"
                :class="
                  (st === 'All' && !filters.status) || filters.status === st
                    ? 'bg-blue-100 text-blue-700 font-semibold'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                "
                @click="filters.status = st === 'All' ? '' : st"
              >
                {{ st }}
              </button>
            </div>

            <div class="flex gap-2">
              <Button variant="primary" size="sm" @click="applyFilters">Apply</Button>
              <Button variant="secondary" size="sm" @click="resetFilters">Reset</Button>
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
        <div v-if="loading" class="p-8 text-center">
          <p class="text-slate-500">Loading sales history...</p>
        </div>
        <div v-else-if="sales.length === 0" class="p-8 text-center">
          <p class="text-slate-500">No sales found</p>
        </div>
        <Table
          v-else
          :columns="columns"
          :rows="paginatedRows"
          striped
          hoverable
          @row-click="handleViewSale"
        >
          <template #bill_date="{ value }">
            {{ formatDate(value, 'datetime') }}
          </template>
          <template #total_amount="{ value }">
            <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(value) }}</span>
          </template>
          <template #payment_method="{ value }">
            <span
              class="text-xs px-2.5 py-1 rounded-full font-medium capitalize"
              :class="{
                'bg-emerald-100 text-emerald-700': value === 'cash',
                'bg-blue-100 text-blue-700': value === 'upi' || value === 'card',
                'bg-amber-100 text-amber-700': value === 'credit',
              }"
            >
              {{ value }}
            </span>
          </template>
          <template #status="{ value }">
            <span
              class="text-xs px-2.5 py-1 rounded-full font-medium capitalize"
              :class="{
                'bg-emerald-100 text-emerald-700': value === 'paid',
                'bg-amber-100 text-amber-700': value === 'pending',
                'bg-red-100 text-red-700': value === 'cancelled',
              }"
            >
              {{ value }}
            </span>
          </template>
        </Table>
      </Card>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-2">
        <Button
          variant="secondary"
          size="sm"
          :disabled="currentPage === 1"
          @click="currentPage = Math.max(1, currentPage - 1)"
        >
          â† Prev
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
          Next â†’
        </Button>
      </div>
    </div>
  </MainLayout>
</template>
