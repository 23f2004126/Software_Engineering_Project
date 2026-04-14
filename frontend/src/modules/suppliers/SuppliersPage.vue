<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { supplierService } from '../../services/apiService.js'
import { paymentService } from '../../services/payementService.js'
import { ensureRazorpayLoaded } from '../../utils/razorpay.js'

const router = useRouter()
const suppliers = ref([])
const loading = ref(false)
const error = ref(null)
const showPaymentPanel = ref(true)
const expandedPayments = ref(new Set())
const showPaymentModal = ref(false)
const paymentLoading = ref(false)
const paymentError = ref('')
const paymentSuccess = ref('')
const selectedSupplier = ref(null)

const paymentForm = ref({
  amount: '',
  note: '',
})

const selectedSupplierPendingAmount = computed(() => Number(selectedSupplier.value?.pending_amount || 0))

onMounted(loadSuppliers)

async function loadSuppliers() {
  loading.value = true
  error.value = null
  try {
    suppliers.value = await supplierService.getSuppliers()
  } catch (err) {
    error.value = err.message
    console.error('Failed to load suppliers:', err)
  } finally {
    loading.value = false
  }
}

function togglePaymentPanel(id) {
  if (expandedPayments.value.has(id)) {
    expandedPayments.value.delete(id)
    return
  }
  expandedPayments.value.add(id)
}

function goToAddSupplier() {
  router.push('/suppliers/add')
}

function openPaymentModal(supplier) {
  selectedSupplier.value = supplier
  paymentForm.value = {
    amount: supplier.pending_amount || '',
    note: '',
  }
  paymentError.value = ''
  showPaymentModal.value = true
}

async function startSupplierRazorpayPayment() {
  await ensureRazorpayLoaded()

  const orderResponse = await paymentService.createOrder({
    amount: Number(paymentForm.value.amount),
    receipt: `SUP-${selectedSupplier.value.supplier_id}-${Date.now()}`,
    notes: {
      channel: 'supplier-page',
      supplier_id: selectedSupplier.value.supplier_id,
      payment_method: 'upi',
    },
  })

  const order = orderResponse.data

  return new Promise((resolve, reject) => {
    const razorpayInstance = new window.Razorpay({
      key: order.key_id,
      amount: order.amount,
      currency: order.currency,
      name: 'Sonik General Store',
      description: `Supplier payment for ${selectedSupplier.value.name}`,
      order_id: order.order_id,
      method: {
        upi: true,
        card: false,
        netbanking: false,
        wallet: false,
        emi: false,
      },
      prefill: {
        name: selectedSupplier.value.contact_person || selectedSupplier.value.name,
        email: selectedSupplier.value.email || '',
        contact: selectedSupplier.value.phone || '',
      },
      theme: {
        color: '#2563eb',
      },
      modal: {
        ondismiss: () => reject(new Error('Payment was cancelled before completion')),
      },
      handler: async (paymentResponse) => {
        try {
          const verifyResponse = await paymentService.verifyPayment(paymentResponse)
          resolve({
            ...paymentResponse,
            verification: verifyResponse.data,
          })
        } catch (verificationError) {
          reject(verificationError)
        }
      },
    })

    razorpayInstance.open()
  })
}

async function handleSupplierPayment() {
  paymentError.value = ''
  paymentSuccess.value = ''

  const amount = Number(paymentForm.value.amount)
  if (!selectedSupplier.value) {
    paymentError.value = 'Choose a supplier first'
    return
  }
  if (!Number.isFinite(amount) || amount <= 0) {
    paymentError.value = 'Enter a valid payment amount'
    return
  }

  paymentLoading.value = true
  try {
    const paymentResult = await startSupplierRazorpayPayment()
    await supplierService.recordPayment(selectedSupplier.value.supplier_id, {
      amount,
      mode: 'upi',
      note: [
        paymentForm.value.note?.trim(),
        `Razorpay payment ID: ${paymentResult.razorpay_payment_id}`,
        `Order ID: ${paymentResult.razorpay_order_id}`,
      ].filter(Boolean).join(' | '),
    })
    paymentSuccess.value = 'Supplier payment recorded successfully'
    showPaymentModal.value = false
    await loadSuppliers()
  } catch (err) {
    paymentError.value = err.message || 'Failed to complete supplier payment'
  } finally {
    paymentLoading.value = false
  }
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Suppliers</h1>
          <p class="text-sm text-slate-500 mt-1">Manage supplier relationships and pending payments</p>
        </div>
        <Button variant="primary" @click="goToAddSupplier">
          + Add Supplier
        </Button>
      </div>

      <div v-if="paymentSuccess" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        {{ paymentSuccess }}
      </div>

      <div v-if="loading" class="text-center py-8 text-slate-500">Loading suppliers...</div>
      <div v-else-if="error" class="bg-red-50 border border-red-300 rounded-lg p-4 text-red-700">
        <p>Error loading suppliers: {{ error }}</p>
        <Button variant="secondary" size="sm" @click="loadSuppliers" class="mt-2">Retry</Button>
      </div>
      <div v-else-if="suppliers.length === 0" class="text-center py-8 text-slate-500">
        <p>No suppliers found. Add one to get started!</p>
      </div>
      <div v-else class="grid grid-cols-3 gap-5">
        <Card v-for="supplier in suppliers" :key="supplier.supplier_id" hover>
          <template #header>
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ supplier.name }}</p>
                <p class="text-sm text-slate-500 mt-1">{{ supplier.contact_person || 'Contact unavailable' }}</p>
              </div>
              <div class="text-right">
                <p class="text-lg">*</p>
                <p class="text-xs font-semibold text-slate-700">{{ supplier.rating }}</p>
              </div>
            </div>
          </template>

          <div class="space-y-3 mb-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Location:</span>
              <span class="font-semibold text-sm">{{ supplier.city || '-' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Contact:</span>
              <span class="text-sm font-mono">{{ supplier.phone }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Email:</span>
              <span class="text-sm font-mono">{{ supplier.email || '-' }}</span>
            </div>
            <div class="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <p class="text-xs text-blue-600 font-semibold mb-1">Payment Terms</p>
              <p class="font-mono font-bold text-blue-600">{{ supplier.payment_terms }} days</p>
              <p class="text-xs text-slate-500 mt-2">Pending: {{ formatCurrency(Number(supplier.pending_amount || 0)) }}</p>
            </div>
          </div>

          <template #footer>
            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth>
                Contact
              </Button>
              <Button variant="secondary" size="sm" fullWidth @click="openPaymentModal(supplier)">
                Pay
              </Button>
            </div>
          </template>
        </Card>
      </div>

      <Card v-if="showPaymentPanel && suppliers.length > 0" class="bg-blue-50 border-blue-100">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">$</span>
              <div>
                <p class="font-semibold text-slate-900">Suppliers Management</p>
                <p class="text-xs text-slate-500 mt-0.5">Manage supplier payments and details</p>
              </div>
            </div>
            <button class="text-slate-400 hover:text-slate-600 font-bold" @click="showPaymentPanel = false">
              x
            </button>
          </div>
        </template>

        <div class="space-y-3">
          <div v-for="supplier in suppliers" :key="supplier.supplier_id" class="bg-white rounded-xl p-4 border border-blue-100">
            <div class="flex items-start justify-between mb-3">
              <div>
                <p class="font-semibold text-slate-900">{{ supplier.name }}</p>
                <p class="text-sm text-slate-500">{{ supplier.contact_person || 'Contact unavailable' }} • {{ supplier.phone }}</p>
              </div>
              <p class="font-mono font-bold text-sm text-blue-600">Rating: {{ supplier.rating }}/5</p>
            </div>

            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth @click="togglePaymentPanel(supplier.supplier_id)">
                {{ expandedPayments.has(supplier.supplier_id) ? 'Hide Details' : 'View Details' }}
              </Button>
              <Button variant="primary" size="sm" fullWidth @click="openPaymentModal(supplier)">
                Pay Now
              </Button>
            </div>

            <div v-show="expandedPayments.has(supplier.supplier_id)" class="border-t border-slate-200 pt-3 mt-3 space-y-3">
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600">Status</span>
                <span class="font-semibold">{{ supplier.status }}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600">Email</span>
                <span class="font-semibold">{{ supplier.email || '-' }}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600">City</span>
                <span class="font-semibold">{{ supplier.city || '-' }}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600">Pending Amount</span>
                <span class="font-semibold text-blue-600">{{ formatCurrency(Number(supplier.pending_amount || 0)) }}</span>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <Modal v-model="showPaymentModal" title="Pay Supplier" size="md">
      <div class="space-y-4">
        <div v-if="selectedSupplier" class="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p class="font-semibold text-slate-900">{{ selectedSupplier.name }}</p>
          <p class="text-sm text-slate-500 mt-1">{{ selectedSupplier.contact_person || selectedSupplier.phone }}</p>
          <p class="text-sm text-blue-600 mt-2">Pending amount: {{ formatCurrency(selectedSupplierPendingAmount) }}</p>
        </div>

        <div v-if="paymentError" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ paymentError }}
        </div>

        <Input v-model="paymentForm.amount" label="Payment Amount" type="number" placeholder="Enter amount" />
        <Input v-model="paymentForm.note" label="Note" placeholder="Optional payment note" />
      </div>

      <template #footer>
        <Button variant="secondary" @click="showPaymentModal = false">
          Cancel
        </Button>
        <Button variant="primary" :disabled="paymentLoading" @click="handleSupplierPayment">
          {{ paymentLoading ? 'Processing...' : 'Pay With Razorpay' }}
        </Button>
      </template>
    </Modal>
  </MainLayout>
</template>
