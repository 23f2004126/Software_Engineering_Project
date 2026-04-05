<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { transactionService, customerService } from '../../services/apiService.js'

const router = useRouter()

const customers = ref([])
const loading = ref(false)
const error = ref(null)
const showAddModal = ref(false)
const selectedCustomer = ref(null)
const expandedRows = ref(new Set())
const customerTransactions = ref({})

const newCustomer = ref({
  name: '',
  phone: '',
  credit_limit: 10000,
})

const riskColor = {
  low: 'bg-emerald-100 text-emerald-700',
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
}

const riskDot = {
  low: '🟢',
  high: '🔴',
  medium: '🟡',
}

const creditUsagePercent = (customer) => {
  return (customer.credit_balance / customer.credit_limit) * 100
}

const toggleRow = async (customerId) => {
  if (expandedRows.value.has(customerId)) {
    expandedRows.value.delete(customerId)
  } else {
    expandedRows.value.add(customerId)
    // Load transactions for this customer if not already loaded
    if (!customerTransactions.value[customerId]) {
      try {
        const txns = await transactionService.getTransactions(customerId)
        customerTransactions.value[customerId] = txns || []
      } catch (err) {
        console.error(`Failed to load transactions for customer ${customerId}:`, err)
        customerTransactions.value[customerId] = []
      }
    }
  }
}

const loadCustomers = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await customerService.getCustomers()
    customers.value = data || []
  } catch (err) {
    error.value = err.message || 'Failed to load customers'
    console.error('Failed to load customers:', err)
  } finally {
    loading.value = false
  }
}

const handleAddCustomer = async () => {
  try {
    await customerService.addCustomer({
      name: newCustomer.value.name,
      phone: newCustomer.value.phone,
      credit_limit: newCustomer.value.credit_limit,
    })
    showAddModal.value = false
    await loadCustomers()
    newCustomer.value = {
      name: '',
      phone: '',
      credit_limit: 10000,
    }
  } catch (err) {
    error.value = err.message || 'Failed to add customer'
    console.error('Failed to add customer:', err)
  }
}

import { onMounted } from 'vue'
onMounted(() => {
  loadCustomers()
})
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Error state -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <p class="font-medium">Failed to load credit data</p>
        <p class="text-sm mt-1">{{ error }}</p>
      </div>

      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Credit Management</h1>
        <p class="text-sm text-slate-500 mt-1">Track customer credit limits and outstanding payments</p>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block">
          <div class="animate-spin w-8 h-8 border-4 border-slate-200 border-t-emerald-600 rounded-full"></div>
        </div>
        <p class="text-slate-500 mt-4">Loading credit data...</p>
      </div>

      <!-- Main content -->
      <template v-else>
        <!-- Stats -->
        <div class="grid grid-cols-4 gap-4">
          <Card>
            <p class="text-xs font-semibold text-slate-400 uppercase">Total Customers</p>
            <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ customers.length }}</p>
          </Card>
          <Card>
            <p class="text-xs font-semibold text-slate-400 uppercase">Total Outstanding</p>
            <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ formatCurrency(customers.reduce((sum, c) => sum + (c.credit_balance || 0), 0)) }}</p>
          </Card>
          <Card>
            <p class="text-xs font-semibold text-slate-400 uppercase">Avg Credit Used</p>
            <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ (customers.length ? (customers.reduce((sum, c) => sum + creditUsagePercent(c), 0) / customers.length).toFixed(0) : 0) }}%</p>
          </Card>
          <Card>
            <p class="text-xs font-semibold text-slate-400 uppercase">High Risk</p>
            <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ customers.filter((c) => c.risk_level === 'high').length }}</p>
          </Card>
        </div>

        <!-- Customers Table -->
        <Card padding="none">
          <Table
            :columns="[
              { key: 'name', label: 'Customer' },
              { key: 'phone', label: 'Phone' },
              { key: 'credit_balance', label: 'Outstanding' },
              { key: 'credit_limit', label: 'Credit Limit' },
              { key: 'usage', label: 'Usage' },
              { key: 'risk_level', label: 'Risk Level' },
              { key: 'actions', label: '' },
            ]"
            :rows="customers"
            striped
            hoverable
          >
            <template #credit_balance="{ value }">
              <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(value) }}</span>
            </template>
            <template #credit_limit="{ value }">
              <span class="font-mono font-semibold text-slate-500">{{ formatCurrency(value) }}</span>
            </template>
            <template #usage="{ row }">
              <div class="flex items-center gap-2 w-40">
                <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    class="h-full transition-all"
                    :class="creditUsagePercent(row) > 80 ? 'bg-red-500' : creditUsagePercent(row) > 50 ? 'bg-amber-500' : 'bg-emerald-500'"
                    :style="{ width: `${Math.min(creditUsagePercent(row), 100)}%` }"
                  ></div>
                </div>
                <span class="text-sm font-semibold text-slate-600 w-12">{{ creditUsagePercent(row).toFixed(0) }}%</span>
              </div>
            </template>
            <template #risk_level="{ value }">
              <span :class="`text-sm px-2.5 py-1 rounded-full font-medium ${riskColor[value]}`">
                {{ riskDot[value] }} {{ value }}
              </span>
            </template>
            <template #actions="{ row }">
              <button
                class="text-emerald-600 hover:text-emerald-700 font-semibold text-sm transition-colors"
                @click="toggleRow(row.id)"
              >
                {{ expandedRows.has(row.id) ? '▼' : '▶' }}
              </button>
            </template>
          </Table>

          <!-- Expandable Detail Rows -->
          <div v-for="customer in customers" :key="customer.id">
            <div v-show="expandedRows.has(customer.id)" class="bg-emerald-50 border-t border-slate-200 p-6">
              <div class="grid grid-cols-3 gap-6">
                <!-- Customer Info -->
                <div>
                  <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Customer Info</p>
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-slate-900">{{ customer.name }}</p>
                    <p class="text-sm text-slate-500">{{ customer.phone }}</p>
                    <p class="text-xs text-slate-500 mt-2">Last transaction: {{ formatDate(customer.last_transaction_date, 'short') }}</p>
                  </div>
                </div>

                <!-- Credit Info -->
                <div>
                  <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Credit Status</p>
                  <div class="space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-slate-600">Limit:</span>
                      <span class="font-semibold">{{ formatCurrency(customer.credit_limit) }}</span>
                    </div>
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-slate-600">Outstanding:</span>
                      <span class="font-semibold text-red-600">{{ formatCurrency(customer.credit_balance) }}</span>
                    </div>
                    <div class="flex items-center justify-between">
                      <span class="text-sm text-slate-600">Available:</span>
                      <span class="font-semibold text-emerald-600">{{ formatCurrency(customer.credit_limit - customer.credit_balance) }}</span>
                    </div>
                  </div>
                </div>

                <!-- Recent Transactions -->
                <div>
                  <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Recent Transactions</p>
                  <div v-if="!customerTransactions[customer.id]" class="text-sm text-slate-500">Loading...</div>
                  <div v-else-if="customerTransactions[customer.id].length === 0" class="text-sm text-slate-500">No transactions yet</div>
                  <div v-else class="space-y-2">
                    <div v-for="txn in customerTransactions[customer.id].slice(0, 3)" :key="txn.id" class="flex items-center justify-between text-sm">
                      <div>
                        <p class="font-semibold text-slate-900">{{ txn.id }}</p>
                        <p class="text-xs text-slate-500">{{ formatDate(txn.transaction_date, 'short') }}</p>
                      </div>
                      <div class="text-right">
                        <p class="font-semibold">{{ formatCurrency(txn.amount) }}</p>
                        <span class="text-xs px-2 py-0.5 rounded-full" :class="txn.status === 'paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'">
                          {{ txn.status }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="mt-4 flex gap-2">
                <Button variant="secondary" size="sm">
                  Mark Paid
                </Button>
                <Button variant="secondary" size="sm">
                  Send Reminder
                </Button>
                <Button variant="secondary" size="sm">
                  View Full Statement
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </template>
    </div>

    <!-- Add Customer Modal -->
    <Modal v-model="showAddModal" title="Add New Customer" size="md">
      <div class="space-y-4">
        <Input v-model="newCustomer.name" label="Customer Name" placeholder="e.g., Rajesh Patel" />
        <Input v-model="newCustomer.phone" label="Phone Number" placeholder="10-digit mobile number" />
        <Input v-model.number="newCustomer.credit_limit" label="Credit Limit" prefix="₹" type="number" />
      </div>

      <template #footer>
        <Button variant="secondary" @click="showAddModal = false">
          Cancel
        </Button>
        <Button variant="primary" @click="handleAddCustomer">
          Add Customer
        </Button>
      </template>
    </Modal>
  </MainLayout>
</template>
