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

const router = useRouter()

const mockCustomers = [
  { id: 1, name: 'Rajesh Patel', phone: '9876543210', credit: 12500, limit: 25000, risk: 'low', lastTransaction: '2025-06-05' },
  { id: 2, name: 'Priya Singh', phone: '9876543211', credit: 18200, limit: 20000, risk: 'high', lastTransaction: '2025-06-04' },
  { id: 3, name: 'Amit Kumar', phone: '9876543212', credit: 8400, limit: 15000, risk: 'low', lastTransaction: '2025-06-03' },
  { id: 4, name: 'Neha Verma', phone: '9876543213', credit: 5600, limit: 10000, risk: 'low', lastTransaction: '2025-06-05' },
  { id: 5, name: 'Vikram Desai', phone: '9876543214', credit: 22300, limit: 25000, risk: 'high', lastTransaction: '2025-05-30' },
  { id: 6, name: 'Anjali Nair', phone: '9876543215', credit: 3200, limit: 8000, risk: 'low', lastTransaction: '2025-06-04' },
]

const showAddModal = ref(false)
const selectedCustomer = ref(null)
const expandedRows = ref(new Set())

const newCustomer = ref({
  name: '',
  phone: '',
  limit: 10000,
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
  return (customer.credit / customer.limit) * 100
}

const toggleRow = (id) => {
  if (expandedRows.value.has(id)) {
    expandedRows.value.delete(id)
  } else {
    expandedRows.value.add(id)
  }
}

const handleAddCustomer = () => {
  showAddModal.value = false
  newCustomer.value = {
    name: '',
    phone: '',
    limit: 10000,
  }
}

const mockTransactions = {
  1: [
    { id: 'TXN001', date: '2025-06-05', amount: 2500, status: 'paid' },
    { id: 'TXN002', date: '2025-06-03', amount: 1800, status: 'pending' },
    { id: 'TXN003', date: '2025-05-28', amount: 3500, status: 'pending' },
  ],
  2: [
    { id: 'TXN004', date: '2025-06-04', amount: 4200, status: 'pending' },
    { id: 'TXN005', date: '2025-06-01', amount: 2800, status: 'pending' },
  ],
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Credit Management</h1>
        <p class="text-sm text-slate-500 mt-1">Track customer credit limits and outstanding payments</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Customers</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ mockCustomers.length }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Outstanding</p>
          <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ formatCurrency(mockCustomers.reduce((sum, c) => sum + c.credit, 0)) }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Avg Credit Used</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ ((mockCustomers.reduce((sum, c) => sum + creditUsagePercent(c), 0) / mockCustomers.length) | 0).toFixed(0) }}%</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">High Risk</p>
          <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ mockCustomers.filter((c) => c.risk === 'high').length }}</p>
        </Card>
      </div>

      <!-- Customers Table -->
      <Card padding="none">
        <Table
          :columns="[
            { key: 'name', label: 'Customer' },
            { key: 'phone', label: 'Phone' },
            { key: 'credit', label: 'Outstanding' },
            { key: 'limit', label: 'Credit Limit' },
            { key: 'usage', label: 'Usage' },
            { key: 'risk', label: 'Risk Level' },
            { key: 'actions', label: '' },
          ]"
          :rows="mockCustomers"
          striped
          hoverable
        >
          <template #credit="{ value }">
            <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(value) }}</span>
          </template>
          <template #limit="{ value }">
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
          <template #risk="{ value }">
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
        <div v-for="customer in mockCustomers" :key="customer.id">
          <div v-show="expandedRows.has(customer.id)" class="bg-emerald-50 border-t border-slate-200 p-6">
            <div class="grid grid-cols-3 gap-6">
              <!-- Customer Info -->
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Customer Info</p>
                <div class="space-y-1">
                  <p class="text-sm font-semibold text-slate-900">{{ customer.name }}</p>
                  <p class="text-sm text-slate-500">{{ customer.phone }}</p>
                  <p class="text-xs text-slate-500 mt-2">Last transaction: {{ formatDate(customer.lastTransaction, 'short') }}</p>
                </div>
              </div>

              <!-- Credit Info -->
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Credit Status</p>
                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-slate-600">Limit:</span>
                    <span class="font-semibold">{{ formatCurrency(customer.limit) }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-slate-600">Outstanding:</span>
                    <span class="font-semibold text-red-600">{{ formatCurrency(customer.credit) }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-slate-600">Available:</span>
                    <span class="font-semibold text-emerald-600">{{ formatCurrency(customer.limit - customer.credit) }}</span>
                  </div>
                </div>
              </div>

              <!-- Recent Transactions -->
              <div>
                <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Recent Transactions</p>
                <div class="space-y-2">
                  <div v-for="txn in mockTransactions[customer.id] || []" :key="txn.id" class="flex items-center justify-between text-sm">
                    <div>
                      <p class="font-semibold text-slate-900">{{ txn.id }}</p>
                      <p class="text-xs text-slate-500">{{ formatDate(txn.date, 'short') }}</p>
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
    </div>

    <!-- Add Customer Modal -->
    <Modal v-model="showAddModal" title="Add New Customer" size="md">
      <div class="space-y-4">
        <Input v-model="newCustomer.name" label="Customer Name" placeholder="e.g., Rajesh Patel" />
        <Input v-model="newCustomer.phone" label="Phone Number" placeholder="10-digit mobile number" />
        <Input v-model.number="newCustomer.limit" label="Credit Limit" prefix="₹" type="number" />
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
