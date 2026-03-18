<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const mockProducts = [
  { id: 1, name: 'Amul Butter 100g', category: 'Dairy', cost: 48, stock: 14 },
  { id: 2, name: 'Tata Salt 1kg', category: 'Grains', cost: 18, stock: 48 },
  { id: 3, name: 'Aashirvaad Atta 5kg', category: 'Grains', cost: 240, stock: 2 },
  { id: 4, name: 'Amul Curd 400g', category: 'Dairy', cost: 28, stock: 6 },
  { id: 5, name: 'Britannia Bread', category: 'Bakery', cost: 35, stock: 12 },
]

const form = ref({
  productId: null,
  quantity: 0,
  reason: 'damaged',
  date: new Date().toISOString().split('T')[0],
  notes: '',
})

const errors = ref({})
const isSubmitting = ref(false)
const logFilter = ref('7d')

const mockLogs = [
  { id: 1, product: 'Amul Butter 100g', quantity: 3, reason: 'expired', date: '2025-06-05', notes: 'Expired on Jun 3', cost: 48 },
  { id: 2, product: 'Tata Salt 1kg', quantity: 1, reason: 'damaged', date: '2025-06-04', notes: 'Package torn', cost: 18 },
  { id: 3, product: 'Britannia Bread', quantity: 2, reason: 'damaged', date: '2025-06-03', notes: 'Mold growth', cost: 35 },
]

const selectedProduct = computed(() => {
  return mockProducts.find((p) => p.id === form.value.productId)
})

const remainingStock = computed(() => {
  return (selectedProduct.value?.stock || 0) - form.value.quantity
})

const selectedProductName = computed(() => {
  return selectedProduct.value?.name || 'Select a product'
})

const handleSubmit = () => {
  errors.value = {}

  if (!form.value.productId) {
    errors.value.productId = 'Select a product'
  }
  if (form.value.quantity <= 0) {
    errors.value.quantity = 'Quantity must be greater than 0'
  }
  if (form.value.quantity > (selectedProduct.value?.stock || 0)) {
    errors.value.quantity = 'Exceeds available stock'
  }

  if (Object.keys(errors.value).length > 0) return

  isSubmitting.value = true
  setTimeout(() => {
    isSubmitting.value = false
    form.value = {
      productId: null,
      quantity: 0,
      reason: 'damaged',
      date: new Date().toISOString().split('T')[0],
      notes: '',
    }
  }, 1000)
}

const totalLost = computed(() => {
  return mockLogs.reduce((sum, log) => sum + log.quantity * log.cost, 0)
})
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-5 gap-6">
      <!-- LEFT: Entry Form -->
      <div class="col-span-2">
        <Card padding="lg">
          <div class="flex items-center gap-2 mb-6 pb-4 border-b border-slate-100">
            <svg class="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <h3 class="font-semibold text-slate-900">Log Stock Loss</h3>
          </div>

          <form class="space-y-4" @submit.prevent="handleSubmit">
            <!-- Product -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Product</label>
              <select
                v-model.number="form.productId"
                class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option :value="null">Select a product...</option>
                <option v-for="product in mockProducts" :key="product.id" :value="product.id">
                  {{ product.name }}
                </option>
              </select>
              <p v-if="selectedProduct" class="text-xs text-slate-500 mt-1">
                Stock: {{ selectedProduct.stock }} units
              </p>
            </div>

            <!-- Quantity -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Quantity Lost</label>
              <div class="flex gap-2">
                <button
                  type="button"
                  class="w-10 h-10 rounded-lg border border-slate-200 hover:bg-slate-50 flex items-center justify-center"
                  @click="form.quantity = Math.max(0, form.quantity - 1)"
                >
                  −
                </button>
                <input
                  v-model.number="form.quantity"
                  type="number"
                  class="flex-1 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                />
                <button
                  type="button"
                  class="w-10 h-10 rounded-lg border border-slate-200 hover:bg-slate-50 flex items-center justify-center"
                  @click="form.quantity++"
                >
                  +
                </button>
              </div>
              <p v-if="selectedProduct" :class="`text-xs mt-1 ${remainingStock < 0 ? 'text-red-600' : 'text-slate-500'}`">
                Remaining: {{ remainingStock }} units
              </p>
            </div>

            <!-- Reason -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Reason</label>
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="reason in ['expired', 'damaged', 'theft']"
                  :key="reason"
                  type="button"
                  class="p-3 rounded-xl text-sm font-medium border text-center transition-all cursor-pointer"
                  :class="
                    form.reason === reason
                      ? reason === 'expired'
                        ? 'border-amber-500 bg-amber-50 text-amber-600'
                        : reason === 'damaged'
                          ? 'border-red-500 bg-red-50 text-red-600'
                          : 'border-purple-500 bg-purple-50 text-purple-600'
                      : 'border-slate-200 bg-white hover:bg-slate-50'
                  "
                  @click="form.reason = reason"
                >
                  {{ reason === 'expired' ? '🗓' : reason === 'damaged' ? '💥' : '🚨' }}
                  {{ reason.charAt(0).toUpperCase() + reason.slice(1) }}
                </button>
              </div>
            </div>

            <!-- Date -->
            <Input v-model="form.date" label="Date" type="date" />

            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Notes</label>
              <textarea
                v-model="form.notes"
                rows="2"
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 resize-none"
                placeholder="Any additional notes..."
              ></textarea>
            </div>

            <Button variant="danger" fullWidth size="lg" :loading="isSubmitting" @click="handleSubmit">
              Log Loss
            </Button>
          </form>
        </Card>
      </div>

      <!-- RIGHT: Loss History -->
      <div class="col-span-3">
        <Card>
          <template #header>
            <div class="flex items-center justify-between">
              <h3 class="font-semibold text-slate-900">Loss History</h3>
              <div class="flex gap-2">
                <button
                  v-for="period in ['7d', '30d', 'all']"
                  :key="period"
                  class="px-3 py-1 text-xs rounded-full transition-colors"
                  :class="
                    logFilter === period
                      ? 'bg-emerald-100 text-emerald-700 font-semibold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  "
                  @click="logFilter = period"
                >
                  {{ period === '7d' ? '7 Days' : period === '30d' ? '30 Days' : 'All' }}
                </button>
              </div>
            </div>
          </template>

          <Table
            :columns="[
              { key: 'date', label: 'Date' },
              { key: 'product', label: 'Product' },
              { key: 'reason', label: 'Reason' },
              { key: 'quantity', label: 'Qty' },
              { key: 'estValue', label: 'Est. Value' },
              { key: 'notes', label: 'Notes' },
            ]"
            :rows="mockLogs"
            striped
          >
            <template #reason="{ value }">
              <span
                class="text-xs px-2.5 py-1 rounded-full font-medium"
                :class="{
                  'bg-amber-100 text-amber-700': value === 'expired',
                  'bg-red-100 text-red-700': value === 'damaged',
                  'bg-purple-100 text-purple-700': value === 'theft',
                }"
              >
                {{ value.charAt(0).toUpperCase() + value.slice(1) }}
              </span>
            </template>
            <template #estValue="{ row }">
              <span class="font-mono font-semibold">{{ formatCurrency(row.quantity * row.cost) }}</span>
            </template>
          </Table>
        </Card>

        <!-- Summary -->
        <div class="grid grid-cols-3 gap-4 mt-5">
          <Card class="bg-red-50 border-red-100">
            <p class="text-xs font-semibold text-red-400 uppercase">Total Items Lost</p>
            <p class="font-mono text-2xl font-bold text-red-600 mt-2">{{ mockLogs.length }}</p>
          </Card>
          <Card class="bg-red-50 border-red-100">
            <p class="text-xs font-semibold text-red-400 uppercase">Est. Value Lost</p>
            <p class="font-mono text-2xl font-bold text-red-600 mt-2">{{ formatCurrency(totalLost) }}</p>
          </Card>
          <Card class="bg-red-50 border-red-100">
            <p class="text-xs font-semibold text-red-400 uppercase">Most Common</p>
            <p class="font-mono text-2xl font-bold text-red-600 mt-2">Damaged</p>
          </Card>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
