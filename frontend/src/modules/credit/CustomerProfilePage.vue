<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const router = useRouter()

const mockCustomer = {
  id: 1,
  name: 'Rajesh Patel',
  phone: '9876543210',
  email: 'rajesh@example.com',
  address: '123 Market St, Mumbai, 400001',
  totalCredit: 12500,
  creditLimit: 25000,
  totalOrders: 42,
  totalSpent: 125000,
  joinDate: '2024-01-15',
  riskLevel: 'low',
}

const selectedTab = ref('sales')
const showPaymentModal = ref(false)
const paymentAmount = ref(0)
const paymentMode = ref('cash')

const mockSales = [
  { id: '#BL-00234', date: '2025-06-05', items: 5, total: 2500, mode: 'credit' },
  { id: '#BL-00233', date: '2025-06-04', items: 3, total: 1800, mode: 'credit' },
  { id: '#BL-00232', date: '2025-06-03', items: 7, total: 3200, mode: 'credit' },
  { id: '#BL-00231', date: '2025-05-28', items: 4, total: 1500, mode: 'credit' },
]

const mockPayments = [
  { id: 'PAY001', date: '2025-06-01', amount: 5000, mode: 'transfer' },
  { id: 'PAY002', date: '2025-05-20', amount: 3500, mode: 'cash' },
  { id: 'PAY003', date: '2025-05-10', amount: 4000, mode: 'cheque' },
]

const tabs = [
  { id: 'sales', label: 'Sales History', icon: '📋' },
  { id: 'payments', label: 'Payments', icon: '💳' },
]

const totalSales = computed(() => mockSales.reduce((sum, s) => sum + s.total, 0))
const totalPayments = computed(() => mockPayments.reduce((sum, p) => sum + p.amount, 0))
const avgOrderValue = computed(() => (totalSales.value / mockSales.length).toFixed(0))

const handlePayment = () => {
  showPaymentModal.value = false
  paymentAmount.value = 0
  paymentMode.value = 'cash'
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Breadcrumb -->
      <div class="text-sm text-slate-500">
        <a href="/credit" class="text-emerald-600 hover:underline">Credit Management</a>
        <span class="mx-2">→</span>
        {{ mockCustomer.name }}
      </div>

      <!-- Customer Header Card -->
      <Card class="bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200">
        <div class="grid grid-cols-4 gap-8">
          <!-- Profile -->
          <div>
            <div class="w-16 h-16 rounded-full bg-emerald-200 flex items-center justify-center text-2xl mb-4">
              👤
            </div>
            <p class="font-bold text-lg text-slate-900">{{ mockCustomer.name }}</p>
            <p class="text-sm text-slate-500 mt-1">{{ mockCustomer.phone }}</p>
            <p class="text-xs text-slate-400 mt-1">Joined {{ formatDate(mockCustomer.joinDate, 'short') }}</p>
          </div>

          <!-- Contact & Address -->
          <div>
            <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Contact</p>
            <p class="text-sm text-slate-900">{{ mockCustomer.email }}</p>
            <p class="text-xs text-slate-500 mt-3">{{ mockCustomer.address }}</p>
          </div>

          <!-- Credit Info -->
          <div>
            <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Credit Status</p>
            <p class="text-3xl font-bold text-slate-900 mb-3">{{ formatCurrency(mockCustomer.totalCredit) }}</p>
            <p class="text-xs text-slate-500">of {{ formatCurrency(mockCustomer.creditLimit) }} limit</p>
            <div class="mt-3 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div class="h-full bg-red-500" :style="{ width: `${(mockCustomer.totalCredit / mockCustomer.creditLimit) * 100}%` }"></div>
            </div>
          </div>

          <!-- Stats -->
          <div>
            <p class="text-xs font-semibold text-slate-400 uppercase mb-3">Quick Stats</p>
            <div class="space-y-2 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-slate-600">Total Orders:</span>
                <span class="font-semibold">{{ mockCustomer.totalOrders }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-600">Total Spent:</span>
                <span class="font-semibold">{{ formatCurrency(mockCustomer.totalSpent) }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-slate-600">Avg Order:</span>
                <span class="font-semibold">{{ formatCurrency(avgOrderValue) }}</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Tabs -->
      <div class="border-b border-slate-200">
        <div class="flex gap-6">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="py-4 px-2 text-sm font-medium border-b-2 transition-colors"
            :class="
              selectedTab === tab.id
                ? 'border-emerald-500 text-emerald-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            "
            @click="selectedTab = tab.id"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div v-if="selectedTab === 'sales'" class="space-y-6">
        <!-- Sales Summary -->
        <div class="grid grid-cols-3 gap-4">
          <Card class="bg-blue-50 border-blue-100">
            <p class="text-xs font-semibold text-blue-400 uppercase">Total Sales</p>
            <p class="font-mono text-3xl font-bold text-blue-600 mt-2">{{ formatCurrency(totalSales) }}</p>
          </Card>
          <Card class="bg-purple-50 border-purple-100">
            <p class="text-xs font-semibold text-purple-400 uppercase">Number of Orders</p>
            <p class="font-mono text-3xl font-bold text-purple-600 mt-2">{{ mockSales.length }}</p>
          </Card>
          <Card class="bg-teal-50 border-teal-100">
            <p class="text-xs font-semibold text-teal-400 uppercase">Average Order Value</p>
            <p class="font-mono text-3xl font-bold text-teal-600 mt-2">{{ formatCurrency(avgOrderValue) }}</p>
          </Card>
        </div>

        <!-- Sales Table -->
        <Card padding="none">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50">
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Bill ID</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Date</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Items</th>
                <th class="px-6 py-3 text-right font-semibold text-slate-900">Amount</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sale in mockSales" :key="sale.id" class="border-b border-slate-100 hover:bg-slate-50">
                <td class="px-6 py-3">
                  <a href="#" class="text-emerald-600 hover:underline font-semibold">{{ sale.id }}</a>
                </td>
                <td class="px-6 py-3 text-slate-600">{{ formatDate(sale.date, 'short') }}</td>
                <td class="px-6 py-3 text-slate-600">{{ sale.items }}</td>
                <td class="px-6 py-3 text-right font-mono font-semibold">{{ formatCurrency(sale.total) }}</td>
                <td class="px-6 py-3">
                  <span class="text-xs px-2.5 py-1 rounded-full bg-amber-100 text-amber-700 font-medium">Unpaid</span>
                </td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>

      <div v-if="selectedTab === 'payments'" class="space-y-6">
        <!-- Payments Summary -->
        <div class="grid grid-cols-3 gap-4">
          <Card class="bg-emerald-50 border-emerald-100">
            <p class="text-xs font-semibold text-emerald-400 uppercase">Total Payments</p>
            <p class="font-mono text-3xl font-bold text-emerald-600 mt-2">{{ formatCurrency(totalPayments) }}</p>
          </Card>
          <Card class="bg-slate-50 border-slate-100">
            <p class="text-xs font-semibold text-slate-400 uppercase">Remaining Credit</p>
            <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ formatCurrency(mockCustomer.totalCredit - totalPayments) }}</p>
          </Card>
          <Card class="bg-blue-50 border-blue-100">
            <p class="text-xs font-semibold text-blue-400 uppercase">Last Payment</p>
            <p class="text-sm font-semibold text-blue-600 mt-2">{{ formatDate(mockPayments[0].date, 'short') }}</p>
            <p class="text-xs text-blue-500 mt-1">{{ formatCurrency(mockPayments[0].amount) }}</p>
          </Card>
        </div>

        <!-- Add Payment Button -->
        <div class="flex justify-end">
          <Button variant="primary" @click="showPaymentModal = true">
            + Record Payment
          </Button>
        </div>

        <!-- Payments Table -->
        <Card padding="none">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50">
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Payment ID</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Date</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Mode</th>
                <th class="px-6 py-3 text-right font-semibold text-slate-900">Amount</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="payment in mockPayments" :key="payment.id" class="border-b border-slate-100 hover:bg-slate-50">
                <td class="px-6 py-3 font-semibold text-slate-900">{{ payment.id }}</td>
                <td class="px-6 py-3 text-slate-600">{{ formatDate(payment.date, 'short') }}</td>
                <td class="px-6 py-3 text-slate-600 capitalize">{{ payment.mode }}</td>
                <td class="px-6 py-3 text-right font-mono font-semibold text-emerald-600">{{ formatCurrency(payment.amount) }}</td>
                <td class="px-6 py-3">
                  <span class="text-xs px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700 font-medium">Received</span>
                </td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>
    </div>

    <!-- Payment Modal -->
    <Modal v-model="showPaymentModal" title="Record Payment" size="md">
      <div class="space-y-4">
        <div>
          <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Outstanding Amount</p>
          <p class="font-mono text-2xl font-bold text-slate-900">{{ formatCurrency(mockCustomer.totalCredit) }}</p>
        </div>

        <Input
          v-model.number="paymentAmount"
          label="Payment Amount"
          type="number"
          prefix="₹"
          :placeholder="`Up to ${formatCurrency(mockCustomer.totalCredit)}`"
        />

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">Payment Mode</label>
          <select
            v-model="paymentMode"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option>cash</option>
            <option>transfer</option>
            <option>cheque</option>
            <option>upi</option>
          </select>
        </div>
      </div>

      <template #footer>
        <Button variant="secondary" @click="showPaymentModal = false">
          Cancel
        </Button>
        <Button variant="primary" @click="handlePayment">
          Record Payment
        </Button>
      </template>
    </Modal>
  </MainLayout>
</template>
