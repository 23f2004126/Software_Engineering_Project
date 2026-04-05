<script setup>
import { ref, computed, onMounted } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { inventoryService } from '../../services/apiService.js'

const products = ref([])
const damageLogs = ref([])
const isLoadingProducts = ref(false)
const isLoadingLogs = ref(false)
const submitError = ref('')
const loadError = ref('')

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

const selectedProduct = computed(() => {
  return products.value.find((p) => p.id === form.value.productId)
})

const remainingStock = computed(() => {
  return (selectedProduct.value?.quantity || 0) - form.value.quantity
})

const selectedProductName = computed(() => {
  return selectedProduct.value?.name || 'Select a product'
})

const filteredLogs = computed(() => {
  const now = new Date()
  const logDate = new Date(form.value.date)
  
  return damageLogs.value.filter((log) => {
    const logTime = new Date(log.date)
    const daysDiff = Math.floor((now - logTime) / (1000 * 60 * 60 * 24))
    
    if (logFilter.value === '7d') return daysDiff <= 7
    if (logFilter.value === '30d') return daysDiff <= 30
    return true
  })
})

const totalLost = computed(() => {
  return filteredLogs.value.reduce((sum, log) => sum + (log.quantity * log.cost_price || 0), 0)
})

const loadData = async () => {
  isLoadingProducts.value = true
  isLoadingLogs.value = true
  loadError.value = ''
  
  try {
    const [productsData, logsData] = await Promise.all([
      inventoryService.getProducts(),
      inventoryService.getDamageLossReport()
    ])
    products.value = productsData
    damageLogs.value = logsData
  } catch (err) {
    loadError.value = 'Failed to load data: ' + (err.message || 'Unknown error')
  } finally {
    isLoadingProducts.value = false
    isLoadingLogs.value = false
  }
}

const handleSubmit = async () => {
  errors.value = {}

  if (!form.value.productId) {
    errors.value.productId = 'Select a product'
  }
  if (form.value.quantity <= 0) {
    errors.value.quantity = 'Quantity must be greater than 0'
  }
  if (form.value.quantity > (selectedProduct.value?.quantity || 0)) {
    errors.value.quantity = 'Exceeds available stock'
  }

  if (Object.keys(errors.value).length > 0) return

  isSubmitting.value = true
  submitError.value = ''
  
  try {
    await inventoryService.logDamageLoss({
      product_id: form.value.productId,
      quantity: form.value.quantity,
      reason: form.value.reason,
      date: form.value.date,
      notes: form.value.notes,
    })
    
    // Reload logs
    damageLogs.value = await inventoryService.getDamageLossReport()
    
    // Reset form
    form.value = {
      productId: null,
      quantity: 0,
      reason: 'damaged',
      date: new Date().toISOString().split('T')[0],
      notes: '',
    }
  } catch (err) {
    submitError.value = 'Failed to log loss: ' + (err.message || 'Unknown error')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <MainLayout>
    <!-- Error Alert -->
    <div v-if="loadError" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
      {{ loadError }}
    </div>

    <div v-if="!isLoadingProducts && !isLoadingLogs" class="grid grid-cols-5 gap-6">
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
            <!-- Submit Error -->
            <div v-if="submitError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {{ submitError }}
            </div>

            <!-- Product -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Product</label>
              <select
                v-model.number="form.productId"
                class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option :value="null">Select a product...</option>
                <option v-for="product in products" :key="product.id" :value="product.id">
                  {{ product.name }}
                </option>
              </select>
              <p v-if="selectedProduct" class="text-xs text-slate-500 mt-1">
                Stock: {{ selectedProduct.quantity }} units
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
              { key: 'product_name', label: 'Product' },
              { key: 'reason', label: 'Reason' },
              { key: 'quantity', label: 'Qty' },
              { key: 'estValue', label: 'Est. Value' },
              { key: 'notes', label: 'Notes' },
            ]"
            :rows="filteredLogs"
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
              <span class="font-mono font-semibold">{{ formatCurrency(row.quantity * (row.cost_price || 0)) }}</span>
            </template>
          </Table>
        </Card>

        <!-- Summary -->
        <div class="grid grid-cols-3 gap-4 mt-5">
          <Card class="bg-red-50 border-red-100">
            <p class="text-xs font-semibold text-red-400 uppercase">Total Items Lost</p>
            <p class="font-mono text-2xl font-bold text-red-600 mt-2">{{ filteredLogs.length }}</p>
          </Card>
          <Card class="bg-red-50 border-red-100">
            <p class="text-xs font-semibold text-red-400 uppercase">Est. Value Lost</p>
            <p class="font-mono text-2xl font-bold text-red-600 mt-2">{{ formatCurrency(totalLost) }}</p>
          </Card>
          <Card class="bg-red-50 border-red-100">
            <p class="text-xs font-semibold text-red-400 uppercase">Most Common</p>
            <p class="font-mono text-2xl font-bold text-red-600 mt-2">
              {{ filteredLogs.length > 0 ? (filteredLogs.reduce((acc, log) => {
                if (!acc[log.reason]) acc[log.reason] = 0
                acc[log.reason]++
                return acc
              }, {})[filteredLogs[0]?.reason] || 'N/A') : 'N/A' }}
            </p>
          </Card>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="flex items-center justify-center h-96">
      <div class="text-center">
        <p class="text-slate-600">Loading inventory data...</p>
      </div>
    </div>
  </MainLayout>
</template>
