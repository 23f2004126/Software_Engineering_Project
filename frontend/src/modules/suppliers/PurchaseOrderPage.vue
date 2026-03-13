<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const form = ref({
  supplier: '',
  deliveryDate: '',
  notes: '',
})

const cartItems = ref([
  { id: 1, name: 'Amul Butter 100g', quantity: 20, cost: 48, total: 960 },
  { id: 2, name: 'Tata Salt 1kg', quantity: 50, cost: 18, total: 900 },
])

const mockSuppliers = ['Fresh Farms Dairy', 'Pure Milk Co', 'Organic Suppliers']
const mockHistory = [
  { id: 'PO-2541', supplier: 'Fresh Farms Dairy', date: '2025-06-01', items: 2, total: 45000, status: 'delivered' },
  { id: 'PO-2540', supplier: 'Pure Milk Co', date: '2025-05-28', items: 3, total: 32000, status: 'delivered' },
  { id: 'PO-2539', supplier: 'Organic Suppliers', date: '2025-05-20', items: 5, total: 68000, status: 'pending' },
]

const subtotal = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.total, 0)
})

const addProduct = () => {
  cartItems.value.push({
    id: Math.max(...cartItems.value.map((i) => i.id), 0) + 1,
    name: 'New Product',
    quantity: 1,
    cost: 0,
    total: 0,
  })
}

const removeProduct = (id) => {
  cartItems.value = cartItems.value.filter((item) => item.id !== id)
}

const updateItemTotal = (item) => {
  item.total = item.quantity * item.cost
}

const handleCreatePO = () => {
  // In real app, would send to backend
}
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-5 gap-6">
      <!-- LEFT: PO Form -->
      <div class="col-span-2">
        <Card padding="lg">
          <div class="flex items-center gap-2 mb-6 pb-4 border-b border-slate-100">
            <span class="text-2xl">📋</span>
            <h3 class="font-semibold text-slate-900">Create Purchase Order</h3>
          </div>

          <form class="space-y-4" @submit.prevent="handleCreatePO">
            <!-- Supplier -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Supplier</label>
              <select
                v-model="form.supplier"
                class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option value="">Select supplier...</option>
                <option v-for="supplier in mockSuppliers" :key="supplier" :value="supplier">
                  {{ supplier }}
                </option>
              </select>
            </div>

            <!-- Delivery Date -->
            <Input v-model="form.deliveryDate" label="Expected Delivery" type="date" />

            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Special Instructions</label>
              <textarea
                v-model="form.notes"
                rows="3"
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 resize-none"
                placeholder="e.g., Cold storage required..."
              ></textarea>
            </div>

            <!-- Summary -->
            <div class="bg-emerald-50 rounded-lg p-4 border border-emerald-100">
              <p class="text-xs font-semibold text-emerald-400 uppercase mb-2">Order Total</p>
              <p class="font-mono text-2xl font-bold text-emerald-700">{{ formatCurrency(subtotal) }}</p>
              <p class="text-xs text-emerald-600 mt-1">{{ cartItems.length }} items</p>
            </div>

            <Button variant="primary" fullWidth size="lg" @click="handleCreatePO">
              Create Purchase Order
            </Button>
          </form>
        </Card>
      </div>

      <!-- RIGHT: PO Items & History -->
      <div class="col-span-3 space-y-6">
        <!-- Add Items -->
        <Card>
          <template #header>
            <div class="flex items-center justify-between">
              <p class="font-semibold text-slate-900">Order Items</p>
              <Button variant="secondary" size="sm" @click="addProduct">
                + Add Item
              </Button>
            </div>
          </template>

          <div class="space-y-3">
            <div v-for="item in cartItems" :key="item.id" class="border border-slate-200 rounded-lg p-4 space-y-3">
              <div class="grid grid-cols-3 gap-3">
                <Input v-model="item.name" label="Product Name" />
                <Input
                  v-model.number="item.quantity"
                  label="Quantity"
                  type="number"
                  @input="updateItemTotal(item)"
                />
                <Input
                  v-model.number="item.cost"
                  label="Cost Price"
                  prefix="₹"
                  @input="updateItemTotal(item)"
                />
              </div>
              <div class="flex items-center justify-between">
                <span class="font-semibold text-slate-900">Total: {{ formatCurrency(item.total) }}</span>
                <button
                  type="button"
                  class="text-red-600 hover:text-red-700 font-semibold text-sm"
                  @click="removeProduct(item.id)"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>

          <template #footer>
            <div class="flex items-center justify-between text-lg">
              <span class="font-semibold text-slate-900">Order Total</span>
              <span class="font-mono font-bold text-emerald-600">{{ formatCurrency(subtotal) }}</span>
            </div>
          </template>
        </Card>

        <!-- PO History -->
        <Card padding="none">
          <template #header>
            <p class="font-semibold text-slate-900">Recent Purchase Orders</p>
          </template>

          <Table
            :columns="[
              { key: 'id', label: 'PO ID' },
              { key: 'supplier', label: 'Supplier' },
              { key: 'date', label: 'Date' },
              { key: 'items', label: 'Items' },
              { key: 'total', label: 'Total' },
              { key: 'status', label: 'Status' },
            ]"
            :rows="mockHistory"
            striped
          >
            <template #id="{ value }">
              <a href="#" class="text-emerald-600 hover:underline font-semibold">{{ value }}</a>
            </template>
            <template #date="{ value }">
              {{ formatDate(value, 'short') }}
            </template>
            <template #total="{ value }">
              <span class="font-mono font-semibold">{{ formatCurrency(value) }}</span>
            </template>
            <template #status="{ value }">
              <span
                class="text-xs px-2.5 py-1 rounded-full font-semibold"
                :class="value === 'delivered' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
              >
                {{ value }}
              </span>
            </template>
          </Table>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
