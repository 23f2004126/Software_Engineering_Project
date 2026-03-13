<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency, formatDate } from '../../utils/currency.js'

const mockSubscribers = [
  { id: 1, name: 'Rajesh Patel', phone: '9876543210', quantity: 500, frequency: 'daily', startDate: '2025-01-15', status: 'active', amount: 500 },
  { id: 2, name: 'Priya Singh', phone: '9876543211', quantity: 1000, frequency: 'daily', startDate: '2024-11-20', status: 'active', amount: 1000 },
  { id: 3, name: 'Amit Kumar', phone: '9876543212', quantity: 250, frequency: 'alter', startDate: '2025-03-10', status: 'inactive', amount: 250 },
  { id: 4, name: 'Neha Verma', phone: '9876543213', quantity: 750, frequency: 'daily', startDate: '2025-02-05', status: 'active', amount: 750 },
  { id: 5, name: 'Vikram Desai', phone: '9876543214', quantity: 2000, frequency: 'daily', startDate: '2024-08-12', status: 'active', amount: 2000 },
]

const showAddModal = ref(false)
const showInvoiceDrawer = ref(false)
const selectedSubscriber = ref(null)

const newSubscriber = ref({
  name: '',
  phone: '',
  quantity: 500,
  frequency: 'daily',
})

const mockInvoices = [
  { id: 'INV-001', date: '2025-06-05', amount: 15500, status: 'paid' },
  { id: 'INV-002', date: '2025-05-31', amount: 15500, status: 'pending' },
  { id: 'INV-003', date: '2025-05-23', amount: 15500, status: 'paid' },
]

const handleAddSubscriber = () => {
  showAddModal.value = false
  newSubscriber.value = {
    name: '',
    phone: '',
    quantity: 500,
    frequency: 'daily',
  }
}

const activeSubscribersCount = computed(() => mockSubscribers.filter((s) => s.status === 'active').length)
const totalDailyQuantity = computed(() => mockSubscribers.filter((s) => s.status === 'active').reduce((sum, s) => sum + s.quantity, 0))
const monthlyRevenue = computed(() => totalDailyQuantity.value * 30)

const openInvoice = (subscriber) => {
  selectedSubscriber.value = subscriber
  showInvoiceDrawer.value = true
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Milk Subscribers</h1>
          <p class="text-sm text-slate-500 mt-1">Manage daily milk subscription customers</p>
        </div>
        <Button variant="primary" @click="showAddModal = true">
          + Add Subscriber
        </Button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Active Subscribers</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ activeSubscribersCount }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Daily Quantity</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ totalDailyQuantity }}</p>
          <p class="text-xs text-slate-500 mt-1">liters/day</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Monthly Revenue</p>
          <p class="font-mono text-3xl font-bold text-emerald-600 mt-2">{{ formatCurrency(monthlyRevenue) }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Subscribers</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ mockSubscribers.length }}</p>
        </Card>
      </div>

      <!-- Subscriber Cards Grid -->
      <div class="grid grid-cols-3 gap-5">
        <Card v-for="subscriber in mockSubscribers" :key="subscriber.id" hover class="cursor-pointer">
          <template #header>
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ subscriber.name }}</p>
                <p class="text-sm text-slate-500">{{ subscriber.phone }}</p>
              </div>
              <span
                class="text-xs px-2 py-1 rounded-full font-semibold"
                :class="subscriber.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'"
              >
                {{ subscriber.status }}
              </span>
            </div>
          </template>

          <div class="space-y-3 mb-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Daily Quantity:</span>
              <span class="font-semibold">{{ subscriber.quantity }}L</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Frequency:</span>
              <span class="font-semibold text-sm">{{ subscriber.frequency === 'alter' ? 'Alternate' : 'Daily' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Monthly:</span>
              <span class="font-mono font-semibold text-emerald-600">{{ formatCurrency(subscriber.amount * 30) }}</span>
            </div>
          </div>

          <template #footer>
            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth @click="openInvoice(subscriber)">
                View Invoice
              </Button>
              <Button variant="secondary" size="sm" fullWidth>
                Edit
              </Button>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Add Subscriber Modal -->
    <Modal v-model="showAddModal" title="Add New Subscriber" size="md">
      <div class="space-y-4">
        <Input v-model="newSubscriber.name" label="Customer Name" placeholder="e.g., Rajesh Patel" />
        <Input v-model="newSubscriber.phone" label="Phone Number" placeholder="10-digit mobile number" />
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Daily Quantity (Liters)</label>
          <input
            v-model.number="newSubscriber.quantity"
            type="number"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Frequency</label>
          <select
            v-model="newSubscriber.frequency"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="daily">Daily</option>
            <option value="alter">Alternate Days</option>
          </select>
        </div>
      </div>

      <template #footer>
        <Button variant="secondary" @click="showAddModal = false">
          Cancel
        </Button>
        <Button variant="primary" @click="handleAddSubscriber">
          Add Subscriber
        </Button>
      </template>
    </Modal>

    <!-- Invoice Drawer -->
    <div
      v-show="showInvoiceDrawer"
      class="fixed inset-0 z-40 bg-black/20 transition-opacity"
      @click="showInvoiceDrawer = false"
    ></div>

    <div
      v-show="showInvoiceDrawer"
      class="fixed right-0 top-0 h-screen w-96 bg-white shadow-xl z-50 transform transition-transform"
      :class="{ 'translate-x-0': showInvoiceDrawer, 'translate-x-full': !showInvoiceDrawer }"
    >
      <div class="p-6 h-full flex flex-col overflow-y-auto">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-900">{{ selectedSubscriber?.name }} - Invoices</h3>
          <button
            class="text-slate-400 hover:text-slate-600 text-2xl"
            @click="showInvoiceDrawer = false"
          >
            ✕
          </button>
        </div>

        <!-- Invoice List -->
        <div class="flex-1">
          <div v-for="invoice in mockInvoices" :key="invoice.id" class="mb-4 p-4 border border-slate-200 rounded-xl">
            <div class="flex items-center justify-between mb-2">
              <p class="font-semibold text-slate-900">{{ invoice.id }}</p>
              <span
                class="text-xs px-2 py-1 rounded-full font-semibold"
                :class="invoice.status === 'paid' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
              >
                {{ invoice.status }}
              </span>
            </div>
            <p class="text-sm text-slate-500 mb-2">{{ invoice.date }}</p>
            <p class="font-mono font-semibold text-slate-900">{{ formatCurrency(invoice.amount) }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="border-t border-slate-200 pt-4 space-y-2">
          <Button variant="primary" fullWidth>
            Send Invoice
          </Button>
          <Button variant="secondary" fullWidth>
            Mark as Paid
          </Button>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
