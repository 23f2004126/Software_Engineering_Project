<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { salesService } from '../../services/apiService.js'

const router = useRouter()

const searchQuery = ref('')
const cartItems = ref([])
const paymentMode = ref('cash')
const discount = ref(0)
const discountType = ref('%')
const gstEnabled = ref(true)
const selectedCustomer = ref(null)
const customerSearch = ref('')
const showCustomerDropdown = ref(false)
const searchResults = ref([])
const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const showSuccessModal = ref(false)
const generatedBill = ref(null)

// Computed properties
const filteredProducts = computed(() => {
  return searchResults.value.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const subtotal = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.quantity * (item.unit_price || item.price), 0)
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

// API calls
const searchProducts = async (query) => {
  if (!query || query.length < 1) {
    searchResults.value = []
    return
  }

  try {
    loading.value = true
    const response = await salesService.searchProducts(query)
    searchResults.value = response || []
  } catch (err) {
    console.error('Product search error:', err)
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const addToCart = (product) => {
  const existing = cartItems.value.find((item) => item.product_id === product.product_id)
  if (existing) {
    existing.quantity++
  } else {
    cartItems.value.push({ 
      ...product, 
      product_id: product.product_id,
      quantity: 1,
      unit_price: product.price 
    })
  }
  searchQuery.value = ''
  searchResults.value = []
}

const removeFromCart = (productId) => {
  cartItems.value = cartItems.value.filter((item) => item.product_id !== productId)
}

const updateQuantity = (productId, newQty) => {
  const item = cartItems.value.find((i) => i.product_id === productId)
  if (item) item.quantity = Math.max(1, parseInt(newQty) || 1)
}

const generateBill = async () => {
  if (cartItems.value.length === 0) {
    error.value = 'Cart is empty. Add products to generate a bill.'
    return
  }

  try {
    submitting.value = true
    error.value = ''

    // Prepare sale items
    const items = cartItems.value.map(item => ({
      product_id: item.product_id,
      quantity: item.quantity,
      unit_price: parseFloat(item.unit_price || item.price),
      discount: 0,
      tax_amount: ((item.unit_price || item.price) * item.quantity * 0.05),
      subtotal: (item.unit_price || item.price) * item.quantity
    }))

    // Prepare sale data
    const saleData = {
      customer_id: selectedCustomer.value?.customer_id || null,
      payment_method: paymentMode.value,
      discount_amount: parseFloat(discountAmount.value) || 0,
      items: items
    }

    // Create sale via API
    const response = await salesService.createSale(saleData)
    
    generatedBill.value = response
    showSuccessModal.value = true
    
    // Clear cart after successful bill generation
    cartItems.value = []
    discount.value = 0
    selectedCustomer.value = null
    paymentMode.value = 'cash'
  } catch (err) {
    error.value = err.message || 'Failed to generate bill'
    console.error('Bill generation error:', err)
  } finally {
    submitting.value = false
  }
}

const viewBillDetails = () => {
  if (generatedBill.value) {
    router.push(`/sales/${generatedBill.value.bill_id}`)
    showSuccessModal.value = false
  }
}

// Watchers
const handleSearchInput = (value) => {
  searchQuery.value = value
  searchProducts(value)
}

onMounted(() => {
  // Load initial products or categories if needed
})
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-5 gap-6">
      <!-- LEFT COLUMN: Products -->
      <div class="col-span-3 space-y-4">
        <!-- Search and filters -->
        <div class="space-y-3">
          <Input 
            :value="searchQuery" 
            @input="handleSearchInput"
            type="search" 
            placeholder="Search products..." 
            icon="search" 
          />

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
              :key="prod.product_id"
              class="w-full text-left px-4 py-2.5 hover:bg-slate-50 rounded-lg transition-colors border-b border-slate-100 last:border-0"
              @click="addToCart(prod)"
            >
              <p class="text-sm font-medium text-slate-900">{{ prod.name }}</p>
              <p class="text-xs text-slate-500">₹{{ prod.price }} × {{ prod.stock_quantity }} in stock</p>
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
              :key="item.product_id"
              class="flex items-center justify-between py-3 border-b border-slate-100 last:border-0"
            >
              <div class="flex-1">
                <p class="text-sm font-medium text-slate-900">{{ item.name }}</p>
                <p class="text-xs text-slate-500">₹{{ item.unit_price || item.price }} each</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="w-6 h-6 rounded border border-slate-200 hover:bg-slate-50 flex items-center justify-center text-sm"
                  @click="updateQuantity(item.product_id, item.quantity - 1)"
                >
                  −
                </button>
                <input
                  :value="item.quantity"
                  type="number"
                  class="w-10 text-center text-sm font-semibold border border-slate-200 rounded px-1"
                  @change="updateQuantity(item.product_id, $event.target.value)"
                />
                <button
                  class="w-6 h-6 rounded border border-slate-200 hover:bg-slate-50 flex items-center justify-center text-sm"
                  @click="updateQuantity(item.product_id, item.quantity + 1)"
                >
                  +
                </button>
              </div>
              <p class="font-mono font-semibold text-slate-900 w-20 text-right">
                ₹{{ ((item.unit_price || item.price) * item.quantity).toLocaleString('en-IN') }}
              </p>
              <button
                class="text-slate-400 hover:text-red-600 ml-2"
                @click="removeFromCart(item.product_id)"
              >
                ×
              </button>
            </div>
          </div>
        </Card>
      </div>

      <!-- RIGHT COLUMN: Summary & Payment -->
      <div class="col-span-2 space-y-4">
        <!-- Error message -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

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
        <Button 
          variant="primary" 
          size="lg" 
          fullWidth
          :disabled="submitting || cartItems.length === 0"
          @click="generateBill"
        >
          {{ submitting ? '⏳ Generating...' : 'Generate Bill' }}
        </Button>

        <div class="grid grid-cols-2 gap-3">
          <Button variant="secondary" size="md" fullWidth disabled>
            🖨 Print
          </Button>
          <Button variant="secondary" size="md" fullWidth disabled>
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

    <!-- Success Modal -->
    <Modal v-if="showSuccessModal" @close="showSuccessModal = false">
      <div class="text-center space-y-4">
        <div class="w-16 h-16 mx-auto bg-emerald-100 rounded-full flex items-center justify-center">
          <svg class="w-8 h-8 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-slate-900">Bill Generated Successfully!</h3>
        <p class="text-sm text-slate-600">
          Receipt #{{ generatedBill?.receipt_number }}
        </p>
        <div class="bg-slate-50 rounded-xl p-4 text-left space-y-2">
          <p class="text-sm"><span class="font-semibold">Total Amount:</span> ₹{{ formatCurrency(generatedBill?.total_amount) }}</p>
          <p class="text-sm"><span class="font-semibold">Payment Mode:</span> {{ generatedBill?.payment_method }}</p>
          <p class="text-sm"><span class="font-semibold">Status:</span> {{ generatedBill?.status }}</p>
        </div>
        <Button variant="primary" fullWidth @click="viewBillDetails">View Bill Details</Button>
      </div>
    </Modal>
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
