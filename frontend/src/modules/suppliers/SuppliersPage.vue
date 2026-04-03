<script setup>
import { ref, onMounted } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { supplierService } from '../../services/apiService.js'

const suppliers = ref([])
const loading = ref(false)
const error = ref(null)
const showAddModal = ref(false)
const showPaymentPanel = ref(true)
const expandedPayments = ref(new Set())

const newSupplier = ref({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  city: '',
  rating: 4.5,
  payment_terms: 30,
  status: 'active',
})

// Load suppliers on mount
onMounted(async () => {
  await loadSuppliers()
})

const loadSuppliers = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await supplierService.getSuppliers()
    suppliers.value = data
  } catch (err) {
    error.value = err.message
    console.error('Failed to load suppliers:', err)
  } finally {
    loading.value = false
  }
}

const handleAddSupplier = async () => {
  try {
    await supplierService.createSupplier({
      name: newSupplier.value.name,
      contact_person: newSupplier.value.contact_person,
      phone: newSupplier.value.phone,
      email: newSupplier.value.email,
      city: newSupplier.value.city,
      rating: newSupplier.value.rating,
      payment_terms: newSupplier.value.payment_terms,
      status: newSupplier.value.status,
    })
    await loadSuppliers()
    showAddModal.value = false
    newSupplier.value = {
      name: '',
      contact_person: '',
      phone: '',
      email: '',
      city: '',
      rating: 4.5,
      payment_terms: 30,
      status: 'active',
    }
  } catch (err) {
    error.value = err.message
    console.error('Failed to create supplier:', err)
  }
}

const togglePaymentPanel = (id) => {
  if (expandedPayments.value.has(id)) {
    expandedPayments.value.delete(id)
  } else {
    expandedPayments.value.add(id)
  }
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Suppliers</h1>
          <p class="text-sm text-slate-500 mt-1">Manage supplier relationships and pending payments</p>
        </div>
        <Button variant="primary" @click="showAddModal = true">
          + Add Supplier
        </Button>
      </div>

      <!-- Supplier Cards Grid -->
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
                <p class="text-lg">⭐</p>
                <p class="text-xs font-semibold text-slate-700">{{ supplier.rating }}</p>
              </div>
            </div>
          </template>

          <div class="space-y-3 mb-4">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">📍 Location:</span>
              <span class="font-semibold text-sm">{{ supplier.city }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">📞 Contact:</span>
              <span class="text-sm font-mono">{{ supplier.phone }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">📧 Email:</span>
              <span class="text-sm font-mono">{{ supplier.email }}</span>
            </div>
            <div class="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <p class="text-xs text-blue-600 font-semibold mb-1">Payment Terms</p>
              <p class="font-mono font-bold text-blue-600">{{ supplier.payment_terms }} days</p>
            </div>
          </div>

          <template #footer>
            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth>
                Contact
              </Button>
              <Button variant="secondary" size="sm" fullWidth @click="togglePaymentPanel(supplier.supplier_id)">
                {{ expandedPayments.has(supplier.supplier_id) ? 'Hide' : 'Pay' }}
              </Button>
            </div>
          </template>
        </Card>
      </div>

      <!-- Pending Payments Panel -->
      <Card v-if="showPaymentPanel && suppliers.length > 0" class="bg-blue-50 border-blue-100">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">💳</span>
              <div>
                <p class="font-semibold text-slate-900">Suppliers Management</p>
                <p class="text-xs text-slate-500 mt-0.5">Manage supplier payments and details</p>
              </div>
            </div>
            <button class="text-slate-400 hover:text-slate-600 font-bold" @click="showPaymentPanel = false">
              ✕
            </button>
          </div>
        </template>

        <div class="space-y-3">
          <div v-for="supplier in suppliers" :key="supplier.supplier_id" class="bg-white rounded-xl p-4 border border-blue-100">
            <div class="flex items-start justify-between mb-3">
              <div>
                <p class="font-semibold text-slate-900">{{ supplier.name }}</p>
                <p class="text-sm text-slate-500">{{ supplier.contact_person }} • {{ supplier.phone }}</p>
              </div>
              <p class="font-mono font-bold text-sm text-blue-600">Rating: {{ supplier.rating }}/5</p>
            </div>

            <div v-show="expandedPayments.has(supplier.supplier_id)" class="border-t border-slate-200 pt-3 mt-3">
              <div class="space-y-3 mb-4">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Status</span>
                  <span class="font-semibold">{{ supplier.status }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Email</span>
                  <span class="font-semibold">{{ supplier.email }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">City</span>
                  <span class="font-semibold">{{ supplier.city }}</span>
                </div>
              </div>
              <div class="flex gap-2">
                <Button variant="primary" size="sm" fullWidth @click="togglePaymentPanel(supplier.supplier_id)">
                  Record Payment
                </Button>
                <Button variant="secondary" size="sm" fullWidth>
                  Edit
                </Button>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Add Supplier Modal -->
    <Modal v-model="showAddModal" title="Add New Supplier" size="md">
      <div class="space-y-4">
        <Input v-model="newSupplier.name" label="Supplier Name" placeholder="e.g., Fresh Farms Dairy" />
        <Input v-model="newSupplier.contact" label="Contact Person" placeholder="e.g., Rajesh Kumar" />
        <Input v-model="newSupplier.phone" label="Phone Number" placeholder="10-digit mobile number" />
        <Input v-model="newSupplier.email" label="Email" type="email" />
        <Input v-model="newSupplier.city" label="City" placeholder="e.g., Pune" />
      </div>

      <template #footer>
        <Button variant="secondary" @click="showAddModal = false">
          Cancel
        </Button>
        <Button variant="primary" @click="handleAddSupplier">
          Add Supplier
        </Button>
      </template>
    </Modal>
  </MainLayout>
</template>
