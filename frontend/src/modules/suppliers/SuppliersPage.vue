<script setup>
import { ref } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const mockSuppliers = ref([
  { id: 1, name: 'Fresh Farms Dairy', contact: 'Rajesh Kumar', phone: '9876543210', email: 'fresh@farm.com', city: 'Pune', rating: 4.8, pending: 45000, nextDelivery: '2025-06-08' },
  { id: 2, name: 'Pure Milk Co', contact: 'Priya Sharma', phone: '9876543211', email: 'pure@milk.com', city: 'Mumbai', rating: 4.5, pending: 32000, nextDelivery: '2025-06-10' },
  { id: 3, name: 'Organic Suppliers', contact: 'Vikram Singh', phone: '9876543212', email: 'organic@supply.com', city: 'Delhi', rating: 4.2, pending: 68000, nextDelivery: '2025-06-15' },
  { id: 4, name: 'Dairy Direct', contact: 'Neha Patel', phone: '9876543213', email: 'direct@dairy.com', city: 'Bangalore', rating: 4.6, pending: 21000, nextDelivery: '2025-06-07' },
  { id: 5, name: 'Premium Milk Hub', contact: 'Amit Verma', phone: '9876543214', email: 'premium@hub.com', city: 'Ahmedabad', rating: 4.3, pending: 38500, nextDelivery: '2025-06-12' },
  { id: 6, name: 'Valley Dairy Farm', contact: 'Ananya Das', phone: '9876543215', email: 'valley@farm.com', city: 'Jaipur', rating: 4.7, pending: 55000, nextDelivery: '2025-06-09' },
])

const showAddModal = ref(false)
const showPaymentPanel = ref(true)
const expandedPayments = ref(new Set())

const newSupplier = ref({
  name: '',
  contact: '',
  phone: '',
  email: '',
  city: '',
})

const handleAddSupplier = () => {
  mockSuppliers.value.push({
    id: mockSuppliers.value.length + 1,
    ...newSupplier.value,
    rating: 4.5,
    pending: 0,
    nextDelivery: new Date().toISOString().split('T')[0],
  })
  showAddModal.value = false
  newSupplier.value = {
    name: '',
    contact: '',
    phone: '',
    email: '',
    city: '',
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
      <div class="grid grid-cols-3 gap-5">
        <Card v-for="supplier in mockSuppliers" :key="supplier.id" hover>
          <template #header>
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ supplier.name }}</p>
                <p class="text-sm text-slate-500 mt-1">{{ supplier.contact }}</p>
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
              <span class="text-sm text-slate-600">🚚 Next Delivery:</span>
              <span class="text-sm font-semibold">{{ formatDate(supplier.nextDelivery, 'short') }}</span>
            </div>
            <div class="bg-red-50 rounded-lg p-3 border border-red-100">
              <p class="text-xs text-red-600 font-semibold mb-1">Pending Payment</p>
              <p class="font-mono font-bold text-red-600">{{ formatCurrency(supplier.pending) }}</p>
            </div>
          </div>

          <template #footer>
            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth>
                Contact
              </Button>
              <Button variant="secondary" size="sm" fullWidth @click="togglePaymentPanel(supplier.id)">
                {{ expandedPayments.has(supplier.id) ? 'Hide' : 'Pay' }}
              </Button>
            </div>
          </template>
        </Card>
      </div>

      <!-- Pending Payments Panel -->
      <Card v-if="showPaymentPanel" class="bg-red-50 border-red-100">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">💳</span>
              <div>
                <p class="font-semibold text-slate-900">Pending Payments Overview</p>
                <p class="text-xs text-slate-500 mt-0.5">Pay suppliers for pending orders</p>
              </div>
            </div>
            <button class="text-slate-400 hover:text-slate-600 font-bold" @click="showPaymentPanel = false">
              ✕
            </button>
          </div>
        </template>

        <div class="space-y-3">
          <div v-for="supplier in mockSuppliers" :key="supplier.id" class="bg-white rounded-xl p-4 border border-red-100">
            <div class="flex items-start justify-between mb-3">
              <div>
                <p class="font-semibold text-slate-900">{{ supplier.name }}</p>
                <p class="text-sm text-slate-500">{{ supplier.contact }} • {{ supplier.phone }}</p>
              </div>
              <p class="font-mono font-bold text-2xl text-red-600">{{ formatCurrency(supplier.pending) }}</p>
            </div>

            <div v-show="expandedPayments.has(supplier.id)" class="border-t border-slate-200 pt-3 mt-3">
              <div class="space-y-3 mb-4">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Order #SO-2541</span>
                  <span class="font-semibold">{{ formatCurrency(15000) }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Order #SO-2540</span>
                  <span class="font-semibold">{{ formatCurrency(18000) }}</span>
                </div>
                <div class="flex items-center justify-between text-sm">
                  <span class="text-slate-600">Order #SO-2539</span>
                  <span class="font-semibold">{{ formatCurrency(12000) }}</span>
                </div>
              </div>
              <div class="flex gap-2">
                <Button variant="primary" size="sm" fullWidth>
                  Make Payment
                </Button>
                <Button variant="secondary" size="sm" fullWidth>
                  Send Invoice
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
