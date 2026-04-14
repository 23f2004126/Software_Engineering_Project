<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { milkSubscriberService } from '../../services/apiService.js'
import { formatCurrency } from '../../utils/currency.js'

const subscribers = ref([])
const router = useRouter()
const loading = ref(false)
const submitLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showAddModal = ref(false)
const showInvoiceDrawer = ref(false)
const selectedSubscriber = ref(null)

const newSubscriber = ref({
  name: '',
  phone: '',
  quantity: 0.5,
  frequency: 'daily',
  start_date: new Date().toISOString().split('T')[0], // YYYY-MM-DD
  status: 'active',
  amount: 0,
  address: '',
  note: ''
})

const mockInvoices = [
  { id: 'INV-001', date: '2026-04-05', amount: 1550, status: 'paid' },
  { id: 'INV-002', date: '2026-03-31', amount: 1550, status: 'pending' },
  { id: 'INV-003', date: '2026-03-05', amount: 1485, status: 'paid' },
]

const activeSubscribersCount = computed(() => subscribers.value.filter((s) => s.status === 'active').length)
const totalDailyQuantity = computed(() => {
  return subscribers.value
    .filter((s) => s.status === 'active')
    .reduce((sum, s) => sum + Number(s.quantity || 0), 0)
})
const monthlyRevenue = computed(() => {
  return subscribers.value
    .filter((s) => s.status === 'active')
    .reduce((sum, s) => sum + Number(s.amount || s.quantity || 0) * 30, 0)
})

const closeAddModal = () => {
  showAddModal.value = false
  resetForm()
}

const resetForm = () => {
  newSubscriber.value = {
    name: '',
    phone: '',
    quantity: 0.5,
    frequency: 'daily',
    start_date: new Date().toISOString().split('T')[0],
    status: 'active',
    amount: 0,
    address: '',
    note: ''
  }
}

const loadSubscribers = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    subscribers.value = await milkSubscriberService.getSubscribers()
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load subscribers'
  } finally {
    loading.value = false
  }
}

const handleAddSubscriber = async () => {
  successMessage.value = ''
  errorMessage.value = ''

  if (!newSubscriber.value.name.trim() || !newSubscriber.value.phone.trim()) {
    errorMessage.value = 'Name and phone are required'
    return
  }
  if (!Number.isFinite(Number(newSubscriber.value.quantity)) || Number(newSubscriber.value.quantity) <= 0) {
    errorMessage.value = 'Daily quantity must be greater than 0'
    return
  }

  submitLoading.value = true
  try {
    const payload = {
      ...newSubscriber.value,
      name: newSubscriber.value.name.trim(),
      phone: newSubscriber.value.phone.trim(),
      quantity: Number(newSubscriber.value.quantity),
      amount: Number(newSubscriber.value.amount || newSubscriber.value.quantity),
      start_date: newSubscriber.value.start_date || new Date().toISOString().split('T')[0],
      status: newSubscriber.value.status || 'active'
    }

    await milkSubscriberService.createSubscriber(payload)
    await loadSubscribers()
    showAddModal.value = false
    successMessage.value = 'Subscriber added successfully'
    resetForm()
  } catch (error) {
    errorMessage.value = error.message || 'Failed to add subscriber'
  } finally {
    submitLoading.value = false
  }
}

const openInvoice = (subscriber) => {
  selectedSubscriber.value = subscriber
  showInvoiceDrawer.value = true
}

const openDailyEntries = (subscriber) => {
  router.push(`/milk/${subscriber.id}`)
}

onMounted(loadSubscribers)
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Milk Subscribers</h1>
          <p class="text-sm text-slate-500 mt-1">Manage daily milk subscription customers</p>
        </div>
        <Button variant="primary" @click="showAddModal = true">
          + Add Subscriber
        </Button>
      </div>

      <div v-if="successMessage" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {{ errorMessage }}
      </div>

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
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ subscribers.length }}</p>
        </Card>
      </div>

      <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500">
        Loading subscribers...
      </div>

      <div v-else-if="subscribers.length === 0" class="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
        <p class="text-slate-500">No milk subscribers found yet.</p>
      </div>

      <div v-else class="grid grid-cols-3 gap-5">
        <Card v-for="subscriber in subscribers" :key="subscriber.id" hover class="cursor-pointer">
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
              <span class="font-mono font-semibold text-emerald-600">{{ formatCurrency((subscriber.amount || subscriber.quantity) * 30) }}</span>
            </div>
          </div>

          <template #footer>
            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth @click="openInvoice(subscriber)">
                View Invoice
              </Button>
              <Button variant="secondary" size="sm" fullWidth @click="openDailyEntries(subscriber)">
                Daily Entry
              </Button>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Modal v-model="showAddModal" title="Add New Subscriber" size="md">
      <form class="space-y-4" @submit.prevent="handleAddSubscriber">
        <Input v-model="newSubscriber.name" label="Customer Name" placeholder="e.g., Rajesh Patel" />
        <Input v-model="newSubscriber.phone" label="Phone Number" placeholder="10-digit mobile number" />
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Daily Quantity (Liters)</label>
          <input
            v-model.number="newSubscriber.quantity"
            type="number"
            min="0.1"
            step="0.1"
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
        <Input v-model="newSubscriber.address" label="Address" placeholder="Customer address" />
        <Input v-model="newSubscriber.note" label="Note" placeholder="Optional note" />
      </form>

      <template #footer>
        <Button variant="secondary" @click="closeAddModal">
          Cancel
        </Button>
        <button
          type="button"
          :disabled="submitLoading"
          class="font-medium rounded-xl transition-all duration-200 active:scale-95 flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          @click="handleAddSubscriber"
        >
          {{ submitLoading ? 'Saving...' : 'Add Subscriber' }}
        </button>
      </template>
    </Modal>

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
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
          <h3 class="font-semibold text-slate-900">{{ selectedSubscriber?.name }} - Invoices</h3>
          <button
            class="text-slate-400 hover:text-slate-600 text-2xl"
            @click="showInvoiceDrawer = false"
          >
            x
          </button>
        </div>

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
