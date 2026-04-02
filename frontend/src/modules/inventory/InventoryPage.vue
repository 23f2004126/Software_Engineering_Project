<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency, calcMargin, marginColor } from '../../utils/currency.js'
import { formatDate, isExpiringSoon, isExpired } from '../../utils/dateFormatter.js'
import { inventoryService } from '../../services/apiService.js'

const router = useRouter()
const authStore = useAuthStore()

// State management
const products = ref([])
const lowStockAlerts = ref([])
const expiringAlerts = ref([])
const inventoryStats = ref({})
const loading = ref(false)
const error = ref('')

const searchQuery = ref('')
const categoryFilter = ref('all')
const stockFilter = ref('all')
const viewMode = ref('table')
const currentPage = ref(1)
const pageSize = 15

// Computed properties
const filteredProducts = computed(() => {
  return products.value.filter((p) => {
    if (searchQuery.value && !p.name.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    if (categoryFilter.value !== 'all' && p.category !== categoryFilter.value) return false
    if (stockFilter.value === 'low' && p.stock >= p.reorder_level) return false
    if (stockFilter.value === 'expiring' && !isExpiringSoon(p.expiry_date)) return false
    if (stockFilter.value === 'out' && p.stock > 0) return false
    return true
  })
})

const paginatedProducts = computed(() => {
  if (viewMode.value === 'grid') {
    return filteredProducts.value
  }
  const start = (currentPage.value - 1) * pageSize
  return filteredProducts.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.ceil(filteredProducts.value.length / pageSize)
})

const lowStockCount = computed(() => products.value.filter((p) => p.stock < p.reorder_level).length)
const expiringCount = computed(() => products.value.filter((p) => isExpiringSoon(p.expiry_date)).length)
const outOfStockCount = computed(() => products.value.filter((p) => p.stock === 0).length)

const columns = [
  { key: 'name', label: 'Product' },
  { key: 'category', label: 'Category' },
  { key: 'cost_price', label: 'Cost' },
  { key: 'price', label: 'Price' },
  { key: 'margin', label: 'Margin %' },
  { key: 'stock', label: 'Stock' },
  { key: 'reorder_level', label: 'Reorder' },
  { key: 'expiry_date', label: 'Expiry' },
  { key: 'status', label: 'Status' },
]

// Methods
const getMarginColor = (cost, price) => {
  return marginColor(calcMargin(cost, price))
}

const getStatusLabel = (product) => {
  if (product.stock === 0) return 'Out of Stock'
  if (product.stock < product.reorder_level) return 'Low Stock'
  if (isExpiringSoon(product.expiry_date)) return 'Expiring'
  return 'In Stock'
}

const fetchProducts = async () => {
  try {
    loading.value = true
    error.value = ''
    const data = await inventoryService.getProducts({
      skip: 0,
      limit: 1000,
      status: 'active'
    })
    products.value = data || []
  } catch (err) {
    error.value = err.message || 'Failed to fetch products'
    console.error('Fetch products error:', err)
  } finally {
    loading.value = false
  }
}

const fetchLowStockAlerts = async () => {
  try {
    const data = await inventoryService.getLowStockProducts()
    lowStockAlerts.value = data || []
  } catch (err) {
    console.error('Fetch low stock alerts error:', err)
  }
}

const fetchExpiringAlerts = async () => {
  try {
    const data = await inventoryService.getExpiringProducts(30)
    expiringAlerts.value = data || []
  } catch (err) {
    console.error('Fetch expiring alerts error:', err)
  }
}

const fetchInventoryStats = async () => {
  try {
    const data = await inventoryService.getInventoryStats()
    inventoryStats.value = data || {}
  } catch (err) {
    console.error('Fetch inventory stats error:', err)
  }
}

const loadInventoryData = async () => {
  await Promise.all([
    fetchProducts(),
    fetchLowStockAlerts(),
    fetchExpiringAlerts(),
    fetchInventoryStats()
  ])
}

const handleProductClick = (product) => {
  if (authStore.isOwner) {
    router.push(`/inventory/edit/${product.product_id}`)
  } else {
    router.push(`/inventory/${product.product_id}`)
  }
}

const handleAddProduct = () => {
  router.push('/inventory/add')
}

// Lifecycle
onMounted(() => {
  loadInventoryData()
})

</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Error Alert -->
      <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        <p class="font-semibold">Error loading inventory</p>
        <p class="text-sm mt-1">{{ error }}</p>
      </div>

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Inventory</h1>
          <p class="text-sm text-slate-500 mt-1">
            {{ loading ? 'Loading...' : products.length }} products in stock
          </p>
        </div>
        <Button v-if="authStore.isOwner" variant="primary" @click="handleAddProduct">
          + Add Product
        </Button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Products</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">
            {{ loading ? '—' : products.length }}
          </p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Low Stock</p>
          <p class="font-mono text-3xl font-bold text-red-600 mt-2">
            {{ loading ? '—' : lowStockCount }}
          </p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Expiring Soon</p>
          <p class="font-mono text-3xl font-bold text-amber-600 mt-2">
            {{ loading ? '—' : expiringCount }}
          </p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Out of Stock</p>
          <p class="font-mono text-3xl font-bold text-red-600 mt-2">
            {{ loading ? '—' : outOfStockCount }}
          </p>
        </Card>
      </div>

      <!-- Controls -->
      <Card>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <Input v-model="searchQuery" placeholder="Search products..." icon="search" />
          </div>
          <select
            v-model="categoryFilter"
            class="border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="all">All Categories</option>
            <option>Dairy</option>
            <option>Grains</option>
            <option>Bakery</option>
            <option>Snacks</option>
            <option>Grocery</option>
            <option>Personal</option>
          </select>

          <select
            v-model="stockFilter"
            class="border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option value="all">All Stock</option>
            <option value="low">Low Stock</option>
            <option value="expiring">Expiring Soon</option>
            <option value="out">Out of Stock</option>
          </select>

          <div class="flex gap-2">
            <button
              class="w-10 h-10 rounded-xl border transition-colors"
              :class="viewMode === 'table' ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200 hover:bg-slate-50'"
              @click="viewMode = 'table'"
            >
              📊
            </button>
            <button
              class="w-10 h-10 rounded-xl border transition-colors"
              :class="viewMode === 'grid' ? 'border-emerald-500 bg-emerald-50' : 'border-slate-200 hover:bg-slate-50'"
              @click="viewMode = 'grid'"
            >
              🔲
            </button>
          </div>
        </div>
      </Card>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-slate-500">Loading inventory data...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="products.length === 0" class="text-center py-12 border-2 border-dashed border-slate-200 rounded-2xl">
        <p class="text-slate-400">No products found</p>
      </div>

      <!-- Table View -->
      <Card v-else-if="viewMode === 'table'" padding="none">
        <Table :columns="columns" :rows="paginatedProducts" striped hoverable>
          <template #margin="{ row }">
            <span :class="`${getMarginColor(row.cost_price, row.price)} font-semibold`">
              {{ calcMargin(row.cost_price, row.price).toFixed(1) }}%
            </span>
          </template>
          <template #cost_price="{ value }">
            {{ formatCurrency(value) }}
          </template>
          <template #price="{ value }">
            {{ formatCurrency(value) }}
          </template>
          <template #stock="{ value, row }">
            <span :class="value < row.reorder_level ? 'bg-red-50 text-red-600 font-semibold' : ''">
              {{ value }}
            </span>
          </template>
          <template #reorder_level="{ value }">
            {{ value }}
          </template>
          <template #expiry_date="{ value }">
            <span :class="isExpiringSoon(value) ? 'text-amber-600 font-semibold' : ''">
              {{ formatDate(value, 'short') }}
            </span>
          </template>
          <template #status="{ row }">
            <span
              class="text-xs px-2.5 py-1 rounded-full font-medium"
              :class="{
                'bg-red-100 text-red-700': row.stock === 0,
                'bg-amber-100 text-amber-700': isExpiringSoon(row.expiry_date),
                'bg-emerald-100 text-emerald-700': row.stock > 0 && !isExpiringSoon(row.expiry_date),
              }"
            >
              {{ getStatusLabel(row) }}
            </span>
          </template>
        </Table>
      </Card>

      <!-- Grid View -->
      <div v-else-if="viewMode === 'grid'" class="grid grid-cols-4 gap-5">
        <Card
          v-for="product in paginatedProducts"
          :key="product.product_id"
          :class="authStore.isOwner ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''"
          @click="handleProductClick(product)"
        >
          <div class="text-center mb-3">
            <div class="w-full aspect-video rounded-xl mb-3 flex items-center justify-center text-3xl bg-slate-100">
              📦
            </div>
            <p class="font-semibold text-slate-900 text-sm">{{ product.name }}</p>
            <p class="text-xs text-slate-500 mt-1">{{ product.category }}</p>
          </div>
          <div class="space-y-2 pt-2 border-t border-slate-100">
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-600">Stock:</span>
              <span class="font-semibold" :class="product.stock < product.reorder_level ? 'text-red-600' : 'text-slate-900'">
                {{ product.stock }}
              </span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-600">Price:</span>
              <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(product.price) }}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
