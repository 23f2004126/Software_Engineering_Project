<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'

const mockProducts = [
  { id: 1, name: 'Amul Butter 100g', category: 'Dairy', price: 58, stock: 24 },
  { id: 2, name: 'Tata Salt 1kg', category: 'Grains', price: 22, stock: 48 },
  { id: 3, name: 'Aashirvaad Atta 5kg', category: 'Grains', price: 285, stock: 6 },
  { id: 4, name: 'Britannia Bread', category: 'Bakery', price: 45, stock: 12 },
  { id: 5, name: 'Amul Gold 500ml', category: 'Dairy', price: 34, stock: 18 },
  { id: 6, name: 'Parle-G 800g', category: 'Snacks', price: 85, stock: 30 },
  { id: 7, name: 'Fortune Oil 1L', category: 'Grocery', price: 145, stock: 8 },
  { id: 8, name: 'Maggi 2-min 12pk', category: 'Snacks', price: 132, stock: 15 },
  { id: 9, name: 'Colgate 200g', category: 'Personal', price: 98, stock: 20 },
  { id: 10, name: 'Surf Excel 1kg', category: 'Personal', price: 215, stock: 9 },
]

const searchQuery = ref('')
const cartItems = ref([])
const paymentMode = ref('cash')
const discount = ref(0)
const discountType = ref('%')
const gstEnabled = ref(true)
const selectedCustomer = ref(null)
const customerSearch = ref('')
const showCustomerDropdown = ref(false)

const filteredProducts = computed(() => {
  return mockProducts.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const subtotal = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.quantity * item.price, 0)
})

const discountAmount = computed(() => {
  if (discountType.value === '%') {
    return (subtotal.value * discount.value) / 100
  }
  return discount.value
})

const gstAmount = computed(() => {
  if (gstEnabled.value) {
    return (subtotal.value - discountAmount.value) * 0.05
  }
  return 0
})

const total = computed(() => {
  return subtotal.value - discountAmount.value + gstAmount.value
})

const addToCart = (product) => {
  const existing = cartItems.value.find((item) => item.id === product.id)
  if (existing) {
    existing.quantity++
  } else {
    cartItems.value.push({ ...product, quantity: 1 })
  }
  searchQuery.value = ''
}

const removeFromCart = (productId) => {
  cartItems.value = cartItems.value.filter((item) => item.id !== productId)
}

const updateQuantity = (productId, newQty) => {
  const item = cartItems.value.find((i) => i.id === productId)
  if (item) item.quantity = Math.max(1, newQty)
}
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-5 gap-6">
      <!-- LEFT COLUMN: Products -->
      <div class="col-span-3 space-y-4">
        <!-- Search and filters -->
        <div class="space-y-3">
          <Input v-model="searchQuery" type="search" placeholder="Search products..." icon="search" />

          <!-- Category chips -->
          <div class="flex gap-2 overflow-x-auto">
            <button
              v-for="cat in ['All', 'Dairy', 'Grains', 'Bakery', 'Snacks', 'Personal']"
              :key="cat"
              class="px-3 py-1.5 text-xs rounded-full whitespace-nowrap transition-colors"
              :class="
                cat === 'All'
                  ? 'bg-emerald-100 text-emerald-700 font-medium'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              "
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <!-- Product list / Autocomplete dropdown -->
        <Card v-if="searchQuery.length >= 1 && filteredProducts.length > 0" class="max-h-64 overflow-y-auto">
          <div class="space-y-2">
            <button
              v-for="prod in filteredProducts"
              :key="prod.id"
              class="w-full text-left px-4 py-2.5 hover:bg-slate-50 rounded-lg transition-colors border-b border-slate-100 last:border-0"
              @click="addToCart(prod)"
            >
              <p class="text-sm font-medium text-slate-900">{{ prod.name }}</p>
              <p class="text-xs text-slate-500">₹{{ prod.price }} × {{ prod.stock }} in stock</p>
            </button>
          </div>
        </Card>

        <!-- Cart section -->
        <Card>
          <template #header>
            <div class="flex items-center justify-between w-full">
              <h3 class="font-semibold text-slate-900">Cart Items</h3>
              <span class="bg-emerald-100 text-emerald-700 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                {{ cartItems.length }}
              </span>
            </div>
          </template>

          <!-- Empty state -->
          <div v-if="cartItems.length === 0" class="text-center py-12 border-2 border-dashed border-slate-200 rounded-2xl">
            <svg class="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <p class="text-sm text-slate-400">Cart is empty. Add products to get started.</p>
          </div>

          <!-- Cart items -->
          <div v-else class="space-y-0">
            <div
              v-for="item in cartItems"
              :key="item.id"
              class="flex items-center justify-between py-3 border-b border-slate-100 last:border-0"
            >
              <div class="flex-1">
                <p class="text-sm font-medium text-slate-900">{{ item.name }}</p>
                <p class="text-xs text-slate-500">₹{{ item.price }} each</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="w-6 h-6 rounded border border-slate-200 hover:bg-slate-50 flex items-center justify-center text-sm"
                  @click="updateQuantity(item.id, item.quantity - 1)"
                >
                  −
                </button>
                <input
                  :value="item.quantity"
                  type="number"
                  class="w-10 text-center text-sm font-semibold border border-slate-200 rounded px-1"
                  @change="updateQuantity(item.id, $event.target.value)"
                />
                <button
                  class="w-6 h-6 rounded border border-slate-200 hover:bg-slate-50 flex items-center justify-center text-sm"
                  @click="updateQuantity(item.id, item.quantity + 1)"
                >
                  +
                </button>
              </div>
              <p class="font-mono font-semibold text-slate-900 w-20 text-right">
                ₹{{ (item.price * item.quantity).toLocaleString('en-IN') }}
              </p>
              <button
                class="text-slate-400 hover:text-red-600 ml-2"
                @click="removeFromCart(item.id)"
              >
                ×
              </button>
            </div>
          </div>
        </Card>
      </div>

      <!-- RIGHT COLUMN: Summary & Payment -->
      <div class="col-span-2 space-y-4">
        <!-- Order summary -->
        <Card>
          <template #header>
            <h3 class="font-semibold text-slate-900">Order Summary</h3>
          </template>

          <div class="space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-600">Subtotal</span>
              <span class="font-mono font-semibold text-slate-900">₹{{ formatCurrency(subtotal) }}</span>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-600">Discount</span>
              <span class="font-mono text-slate-900">−₹{{ formatCurrency(discountAmount) }}</span>
            </div>

            <div class="flex items-center justify-between text-sm">
              <label class="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" v-model="gstEnabled" class="w-4 h-4 rounded accent-emerald-500" />
                <span class="text-slate-600">GST (5%)</span>
              </label>
              <span class="font-mono text-slate-900">+₹{{ formatCurrency(gstAmount) }}</span>
            </div>

            <div class="border-t-2 border-slate-200 pt-3 flex items-center justify-between">
              <span class="font-semibold text-slate-900">Total</span>
              <span class="font-mono text-2xl font-bold text-emerald-600">₹{{ formatCurrency(total) }}</span>
            </div>
          </div>
        </Card>

        <!-- Payment mode -->
        <div>
          <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Payment Mode</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="mode in ['cash', 'upi', 'credit']"
              :key="mode"
              class="p-3 rounded-xl text-sm font-medium transition-all"
              :class="
                paymentMode === mode
                  ? 'bg-emerald-50 border-2 border-emerald-500 text-emerald-600'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              "
              @click="paymentMode = mode"
            >
              {{ mode.toUpperCase() }}
            </button>
          </div>
        </div>

        <!-- Customer section (for credit) -->
        <Transition name="slide">
          <Card v-show="paymentMode === 'credit'">
            <template #header>
              <h3 class="font-semibold text-slate-900">Customer</h3>
            </template>
            <Input v-model="customerSearch" placeholder="Search customer..." icon="user" />
          </Card>
        </Transition>

        <!-- Action buttons -->
        <Button variant="primary" size="lg" fullWidth>
          Generate Bill
        </Button>

        <div class="grid grid-cols-2 gap-3">
          <Button variant="secondary" size="md" fullWidth>
            🖨 Print
          </Button>
          <Button variant="secondary" size="md" fullWidth>
            ⬇ PDF
          </Button>
        </div>

        <!-- AI Suggestions -->
        <div class="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 rounded-xl p-4">
          <p class="text-sm font-semibold text-emerald-900 mb-3">✦ Smart Suggestions</p>
          <div class="space-y-2">
            <button class="w-full text-left bg-white border border-emerald-200 text-emerald-700 text-xs px-3 py-1.5 rounded-full hover:bg-emerald-50 transition-colors">
              Add Parle-G 800g (trending)
            </button>
            <button class="w-full text-left bg-white border border-emerald-200 text-emerald-700 text-xs px-3 py-1.5 rounded-full hover:bg-emerald-50 transition-colors">
              Bundle: Amul Butter + Tata Salt (18% off)
            </button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
