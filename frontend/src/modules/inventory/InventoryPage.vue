<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency, calcMargin, marginColor } from '../../utils/currency.js'
import { formatDate, isExpiringSoon, isExpired } from '../../utils/dateFormatter.js'

const router = useRouter()

const mockProducts = [
  { id: 1, name: 'Amul Butter 100g', category: 'Dairy', cost: 48, price: 58, stock: 14, reorder: 20, expiry: '2025-06-30', aiTag: 'Low Stock' },
  { id: 2, name: 'Tata Salt 1kg', category: 'Grains', cost: 18, price: 22, stock: 48, reorder: 30, expiry: '2026-12-31', aiTag: 'High Demand' },
  { id: 3, name: 'Aashirvaad Atta 5kg', category: 'Grains', cost: 240, price: 285, stock: 2, reorder: 10, expiry: '2025-09-15', aiTag: 'Reorder Now' },
  { id: 4, name: 'Amul Curd 400g', category: 'Dairy', cost: 28, price: 34, stock: 6, reorder: 15, expiry: '2025-06-09', aiTag: 'Expiring' },
  { id: 5, name: 'Britannia Bread', category: 'Bakery', cost: 35, price: 45, stock: 12, reorder: 8, expiry: '2025-06-20', aiTag: null },
  { id: 6, name: 'Amul Gold 500ml', category: 'Dairy', cost: 28, price: 34, stock: 18, reorder: 15, expiry: '2025-08-15', aiTag: null },
  { id: 7, name: 'Parle-G 800g', category: 'Snacks', cost: 68, price: 85, stock: 30, reorder: 20, expiry: '2025-12-31', aiTag: null },
  { id: 8, name: 'Fortune Oil 1L', category: 'Grocery', cost: 115, price: 145, stock: 8, reorder: 12, expiry: '2026-03-15', aiTag: null },
  { id: 9, name: 'Maggi 2-min 12pk', category: 'Snacks', cost: 102, price: 132, stock: 15, reorder: 10, expiry: '2025-11-30', aiTag: null },
  { id: 10, name: 'Colgate 200g', category: 'Personal', cost: 76, price: 98, stock: 20, reorder: 12, expiry: '2026-06-30', aiTag: null },
  { id: 11, name: 'Surf Excel 1kg', category: 'Personal', cost: 168, price: 215, stock: 9, reorder: 8, expiry: '2026-01-15', aiTag: null },
  { id: 12, name: 'Mother Dairy Paneer', category: 'Dairy', cost: 180, price: 220, stock: 3, reorder: 10, expiry: '2025-06-12', aiTag: null },
  { id: 13, name: 'Britannia Marie', category: 'Snacks', cost: 18, price: 25, stock: 0, reorder: 20, expiry: '2025-10-20', aiTag: null },
  { id: 14, name: 'Basmati Rice 5kg', category: 'Grains', cost: 280, price: 380, stock: 5, reorder: 8, expiry: '2026-06-30', aiTag: null },
  { id: 15, name: 'Mustard Oil 1L', category: 'Grocery', cost: 95, price: 130, stock: 11, reorder: 10, expiry: '2025-12-15', aiTag: null },
]

const searchQuery = ref('')
const categoryFilter = ref('all')
const stockFilter = ref('all')
const viewMode = ref('table')
const currentPage = ref(1)
const pageSize = 15

const filteredProducts = computed(() => {
  return mockProducts.filter((p) => {
    if (searchQuery.value && !p.name.toLowerCase().includes(searchQuery.value.toLowerCase())) return false
    if (categoryFilter.value !== 'all' && p.category !== categoryFilter.value) return false
    if (stockFilter.value === 'low' && p.stock > p.reorder) return false
    if (stockFilter.value === 'expiring' && !isExpiringSoon(p.expiry)) return false
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

const lowStockCount = computed(() => mockProducts.filter((p) => p.stock < p.reorder).length)
const expiringCount = computed(() => mockProducts.filter((p) => isExpiringSoon(p.expiry)).length)
const outOfStockCount = computed(() => mockProducts.filter((p) => p.stock === 0).length)

const columns = [
  { key: 'name', label: 'Product' },
  { key: 'category', label: 'Category' },
  { key: 'cost', label: 'Cost' },
  { key: 'price', label: 'Price' },
  { key: 'margin', label: 'Margin %' },
  { key: 'stock', label: 'Stock' },
  { key: 'reorder', label: 'Reorder' },
  { key: 'expiry', label: 'Expiry' },
  { key: 'status', label: 'Status' },
]

const getMarginColor = (cost, price) => {
  return marginColor(calcMargin(cost, price))
}

const getStatusLabel = (product) => {
  if (product.stock === 0) return 'Out of Stock'
  if (product.stock < product.reorder) return 'Low Stock'
  if (isExpiringSoon(product.expiry)) return 'Expiring'
  return 'In Stock'
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Inventory</h1>
          <p class="text-sm text-slate-500 mt-1">{{ mockProducts.length }} products in stock</p>
        </div>
        <Button variant="primary" @click="router.push('/inventory/add')">
          + Add Product
        </Button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Products</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ mockProducts.length }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Low Stock</p>
          <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ lowStockCount }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Expiring Soon</p>
          <p class="font-mono text-3xl font-bold text-amber-600 mt-2">{{ expiringCount }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Out of Stock</p>
          <p class="font-mono text-3xl font-bold text-red-600 mt-2">{{ outOfStockCount }}</p>
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

      <!-- Table View -->
      <Card v-if="viewMode === 'table'" padding="none">
        <Table :columns="columns" :rows="paginatedProducts" striped hoverable>
          <template #margin="{ row }">
            <span :class="`${getMarginColor(row.cost, row.price)} font-semibold`">
              {{ calcMargin(row.cost, row.price).toFixed(1) }}%
            </span>
          </template>
          <template #stock="{ value, row }">
            <span :class="value < row.reorder ? 'bg-red-50 text-red-600 font-semibold' : ''">
              {{ value }}
            </span>
          </template>
          <template #expiry="{ value }">
            <span :class="isExpiringSoon(value) ? 'text-amber-600 font-semibold' : ''">
              {{ formatDate(value, 'short') }}
            </span>
          </template>
          <template #status="{ row }">
            <span
              class="text-xs px-2.5 py-1 rounded-full font-medium"
              :class="{
                'bg-red-100 text-red-700': row.stock === 0,
                'bg-red-100 text-red-700': row.stock < row.reorder,
                'bg-amber-100 text-amber-700': isExpiringSoon(row.expiry),
                'bg-emerald-100 text-emerald-700': row.stock >= row.reorder && !isExpiringSoon(row.expiry),
              }"
            >
              {{ getStatusLabel(row) }}
            </span>
          </template>
          <template #aiTag="{ row }">
            <span v-if="row.aiTag" class="bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs px-2 py-0.5 rounded-full">
              {{ row.aiTag }}
            </span>
          </template>
        </Table>
      </Card>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="grid grid-cols-4 gap-5">
        <Card v-for="product in paginatedProducts" :key="product.id" hover class="cursor-pointer">
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
              <span class="font-semibold" :class="product.stock < product.reorder ? 'text-red-600' : 'text-slate-900'">
                {{ product.stock }}
              </span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-600">Price:</span>
              <span class="font-mono font-semibold text-slate-900">₹{{ product.price }}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
