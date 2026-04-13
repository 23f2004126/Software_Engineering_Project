<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { formatCurrency } from '../../utils/currency.js'
import { customerService, inventoryService, salesService } from '../../services/apiService.js'
import { paymentService } from '../../services/payementService.js'
import { ensureRazorpayLoaded } from '../../utils/razorpay.js'
import { downloadSaleReceiptPdf, openSalePrintView } from '../../utils/receipt.js'

const router = useRouter()

const GST_RATE = 0.05

const searchQuery = ref('')
const selectedCategory = ref('All')
const cartItems = ref([])
const paymentMode = ref('cash')
const discount = ref(0)
const discountType = ref('%')
const gstEnabled = ref(true)
const selectedCustomer = ref(null)
const customerSearch = ref('')
const customerResults = ref([])
const searchResults = ref([])
const allProducts = ref([])
const loading = ref(false)
const customerLoading = ref(false)
const checkoutLoading = ref(false)
const error = ref('')
const showSuccessModal = ref(false)
const generatedBill = ref(null)

const categories = computed(() => {
  const names = new Set()
  for (const product of allProducts.value) {
    if (product.category) {
      names.add(product.category)
    }
  }
  return ['All', ...Array.from(names).sort()]
})

const filteredProducts = computed(() => {
  const source = searchQuery.value.trim() ? searchResults.value : allProducts.value

  return source.filter((product) => {
    const matchesCategory =
      selectedCategory.value === 'All' ||
      product.category === selectedCategory.value

    return matchesCategory
  })
})

const subtotal = computed(() =>
  cartItems.value.reduce(
    (sum, item) => sum + normalizeAmount(item.unit_price) * item.quantity,
    0,
  ),
)

const discountAmount = computed(() => {
  if (discountType.value === '%') {
    return normalizeAmount((subtotal.value * normalizeAmount(discount.value)) / 100)
  }

  return Math.min(normalizeAmount(discount.value), subtotal.value)
})

const taxableAmount = computed(() =>
  Math.max(0, normalizeAmount(subtotal.value - discountAmount.value)),
)

const gstAmount = computed(() => (gstEnabled.value ? normalizeAmount(taxableAmount.value * GST_RATE) : 0))

const total = computed(() =>
  normalizeAmount(taxableAmount.value + gstAmount.value),
)

const canGenerateBill = computed(() => {
  if (cartItems.value.length === 0 || checkoutLoading.value) {
    return false
  }

  if (paymentMode.value === 'credit' && !selectedCustomer.value) {
    return false
  }

  return true
})

function normalizeAmount(value) {
  return Math.round((Number(value) || 0) * 100) / 100
}

function debounce(fn, delay = 300) {
  let timeoutId

  return (...args) => {
    window.clearTimeout(timeoutId)
    timeoutId = window.setTimeout(() => fn(...args), delay)
  }
}

function allocateDiscountAcrossItems(baseItems) {
  const totalBaseAmount = baseItems.reduce((sum, item) => sum + item.baseAmount, 0)
  let remainingDiscount = discountAmount.value

  return baseItems.map((item, index) => {
    let itemDiscount = 0

    if (totalBaseAmount > 0 && remainingDiscount > 0) {
      if (index === baseItems.length - 1) {
        itemDiscount = normalizeAmount(remainingDiscount)
      } else {
        itemDiscount = normalizeAmount((discountAmount.value * item.baseAmount) / totalBaseAmount)
        remainingDiscount = normalizeAmount(remainingDiscount - itemDiscount)
      }
    }

    const taxableLineAmount = Math.max(0, normalizeAmount(item.baseAmount - itemDiscount))
    const lineTax = gstEnabled.value ? normalizeAmount(taxableLineAmount * GST_RATE) : 0

    return {
      ...item,
      itemDiscount,
      lineTax,
      lineTotal: normalizeAmount(taxableLineAmount + lineTax),
    }
  })
}

function buildSaleItems() {
  const baseItems = cartItems.value.map((item) => ({
    product_id: item.product_id,
    name: item.name,
    quantity: item.quantity,
    unit_price: normalizeAmount(item.unit_price),
    baseAmount: normalizeAmount(item.unit_price * item.quantity),
  }))

  return allocateDiscountAcrossItems(baseItems).map((item) => ({
    product_id: item.product_id,
    quantity: item.quantity,
    unit_price: item.unit_price,
    discount: item.itemDiscount,
    tax_amount: item.lineTax,
    subtotal: item.lineTotal,
  }))
}

function enrichBill(sale, paymentDetails = null) {
  return {
    ...sale,
    customer: selectedCustomer.value ? { ...selectedCustomer.value } : null,
    payment_details: paymentDetails
      ? {
          ...paymentDetails,
          amount: total.value,
        }
      : null,
  }
}

async function loadProducts() {
  try {
    loading.value = true
    const response = await inventoryService.getProducts({ limit: 300, status: 'active' })
    allProducts.value = response || []
  } catch (err) {
    console.error('Initial product load error:', err)
    error.value = err.message || 'Failed to load products'
  } finally {
    loading.value = false
  }
}

async function searchProducts(query) {
  if (!query?.trim()) {
    searchResults.value = []
    return
  }

  try {
    loading.value = true
    const response = await salesService.searchProducts(query.trim())
    searchResults.value = response || []
  } catch (err) {
    console.error('Product search error:', err)
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

const debouncedProductSearch = debounce(searchProducts, 250)

function handleSearchInput(value) {
  searchQuery.value = value
  debouncedProductSearch(value)
}

async function searchCustomers(query) {
  if (!query?.trim()) {
    customerResults.value = []
    return
  }

  try {
    customerLoading.value = true
    const response = await customerService.getCustomers({
      search: query.trim(),
      status: 'active',
      limit: 10,
    })
    customerResults.value = response || []
  } catch (err) {
    console.error('Customer search error:', err)
    customerResults.value = []
  } finally {
    customerLoading.value = false
  }
}

const debouncedCustomerSearch = debounce(searchCustomers, 250)

function handleCustomerSearch(value) {
  customerSearch.value = value

  if (!value) {
    selectedCustomer.value = null
  }

  debouncedCustomerSearch(value)
}

function selectCustomer(customer) {
  selectedCustomer.value = customer
  customerSearch.value = customer.name
  customerResults.value = []
}

function addToCart(product) {
  error.value = ''

  const existing = cartItems.value.find((item) => item.product_id === product.product_id)
  const availableStock = Number(product.stock ?? product.quantity ?? 0)

  if (existing) {
    if (existing.quantity >= availableStock) {
      error.value = `Only ${availableStock} units of ${product.name} are in stock.`
      return
    }

    existing.quantity += 1
  } else {
    if (availableStock < 1) {
      error.value = `${product.name} is out of stock.`
      return
    }

    cartItems.value.push({
      ...product,
      product_id: product.product_id,
      quantity: 1,
      unit_price: normalizeAmount(product.price),
    })
  }

  searchQuery.value = ''
  searchResults.value = []
}

function removeFromCart(productId) {
  cartItems.value = cartItems.value.filter((item) => item.product_id !== productId)
}

function updateQuantity(productId, nextQuantity) {
  const item = cartItems.value.find((entry) => entry.product_id === productId)

  if (!item) {
    return
  }

  const availableStock = Number(item.stock ?? item.quantity ?? 0)
  const parsedQuantity = Math.max(1, Number.parseInt(nextQuantity, 10) || 1)

  if (parsedQuantity > availableStock) {
    error.value = `Only ${availableStock} units of ${item.name} are in stock.`
    item.quantity = availableStock
    return
  }

  error.value = ''
  item.quantity = parsedQuantity
}

function selectPaymentMode(mode) {
  paymentMode.value = mode
  error.value = ''

  if (mode !== 'credit') {
    customerSearch.value = ''
    customerResults.value = []
    selectedCustomer.value = null
  }
}

async function createSaleRecord(paymentDetails = null) {
  const saleData = {
    customer_id: selectedCustomer.value?.customer_id || null,
    payment_method: paymentMode.value,
    discount_amount: discountAmount.value,
    items: buildSaleItems(),
  }

  const response = await salesService.createSale(saleData)
  const bill = enrichBill(response, paymentDetails)

  generatedBill.value = bill
  showSuccessModal.value = true
  downloadSaleReceiptPdf(bill)
  resetCheckoutState()
}

function resetCheckoutState() {
  cartItems.value = []
  discount.value = 0
  discountType.value = '%'
  selectedCustomer.value = null
  customerSearch.value = ''
  customerResults.value = []
  paymentMode.value = 'cash'
  searchQuery.value = ''
  searchResults.value = []
}

async function startRazorpayUpiPayment() {
  await ensureRazorpayLoaded()

  const orderResponse = await paymentService.createOrder({
    amount: total.value,
    receipt: `RCP-${Date.now()}`,
    notes: {
      channel: 'billing-page',
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
      description: 'UPI billing payment',
      order_id: order.order_id,
      method: {
        upi: true,
        card: false,
        netbanking: false,
        wallet: false,
        emi: false,
      },
      prefill: {
        name: selectedCustomer.value?.name || 'Walk-in Customer',
        email: selectedCustomer.value?.email || '',
        contact: selectedCustomer.value?.phone || '',
      },
      theme: {
        color: '#10b981',
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

async function handleCheckout() {
  if (!canGenerateBill.value) {
    if (paymentMode.value === 'credit' && !selectedCustomer.value) {
      error.value = 'Select a customer before creating a credit bill.'
    }
    return
  }

  try {
    checkoutLoading.value = true
    error.value = ''

    if (paymentMode.value === 'upi') {
      const paymentResult = await startRazorpayUpiPayment()
      await createSaleRecord({
        payment_id: paymentResult.razorpay_payment_id,
        order_id: paymentResult.razorpay_order_id,
        signature: paymentResult.razorpay_signature,
        status: paymentResult.verification?.status || 'success',
        method: 'upi',
      })
      return
    }

    await createSaleRecord()
  } catch (err) {
    console.error('Checkout error:', err)
    error.value = err.message || 'Failed to complete checkout'
  } finally {
    checkoutLoading.value = false
  }
}

function viewBillDetails() {
  if (!generatedBill.value) {
    return
  }

  showSuccessModal.value = false
  router.push(`/sales/${generatedBill.value.bill_id}`)
}

function downloadLatestBillPdf() {
  if (generatedBill.value) {
    downloadSaleReceiptPdf(generatedBill.value)
  }
}

function printLatestBill() {
  if (generatedBill.value) {
    openSalePrintView(generatedBill.value)
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-1 gap-6 xl:grid-cols-5">
      <div class="space-y-4 xl:col-span-3">
        <div class="space-y-3">
          <Input
            :modelValue="searchQuery"
            @update:modelValue="handleSearchInput"
            type="search"
            placeholder="Search products by name or SKU..."
            icon="search"
          />

          <div class="flex gap-2 overflow-x-auto">
            <button
              v-for="category in categories"
              :key="category"
              class="whitespace-nowrap rounded-full px-3 py-1.5 text-xs transition-colors"
              :class="
                selectedCategory === category
                  ? 'bg-emerald-100 font-medium text-emerald-700'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              "
              @click="selectedCategory = category"
            >
              {{ category }}
            </button>
          </div>
        </div>

        <Card class="max-h-72 overflow-y-auto">
          <div v-if="loading" class="py-4 text-sm text-slate-500">Loading products...</div>
          <div v-else-if="filteredProducts.length === 0" class="py-4 text-sm text-slate-500">
            No matching products found.
          </div>
          <div v-else class="space-y-2">
            <button
              v-for="product in filteredProducts"
              :key="product.product_id"
              class="w-full rounded-lg border-b border-slate-100 px-4 py-3 text-left transition-colors last:border-0 hover:bg-slate-50"
              @click="addToCart(product)"
            >
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-sm font-medium text-slate-900">{{ product.name }}</p>
                  <p class="text-xs text-slate-500">
                    {{ product.category || 'Uncategorized' }}
                    <span v-if="product.unit">· {{ product.unit }}</span>
                  </p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-semibold text-slate-900">{{ formatCurrency(product.price) }}</p>
                  <p class="text-xs text-slate-500">{{ product.stock ?? product.quantity ?? 0 }} in stock</p>
                </div>
              </div>
            </button>
          </div>
        </Card>

        <Card>
          <template #header>
            <div class="flex w-full items-center justify-between">
              <h3 class="font-semibold text-slate-900">Cart Items</h3>
              <span class="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                {{ cartItems.length }}
              </span>
            </div>
          </template>

          <div
            v-if="cartItems.length === 0"
            class="rounded-2xl border-2 border-dashed border-slate-200 py-12 text-center"
          >
            <svg class="mx-auto mb-3 h-12 w-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <p class="text-sm text-slate-400">Cart is empty. Add products to get started.</p>
          </div>

          <div v-else class="space-y-0">
            <div
              v-for="item in cartItems"
              :key="item.product_id"
              class="flex items-center justify-between gap-3 border-b border-slate-100 py-3 last:border-0"
            >
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-slate-900">{{ item.name }}</p>
                <p class="text-xs text-slate-500">
                  {{ formatCurrency(item.unit_price) }} each · {{ item.stock ?? 0 }} in stock
                </p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="flex h-6 w-6 items-center justify-center rounded border border-slate-200 text-sm hover:bg-slate-50"
                  @click="updateQuantity(item.product_id, item.quantity - 1)"
                >
                  -
                </button>
                <input
                  :value="item.quantity"
                  type="number"
                  min="1"
                  class="w-12 rounded border border-slate-200 px-1 text-center text-sm font-semibold"
                  @change="updateQuantity(item.product_id, $event.target.value)"
                />
                <button
                  class="flex h-6 w-6 items-center justify-center rounded border border-slate-200 text-sm hover:bg-slate-50"
                  @click="updateQuantity(item.product_id, item.quantity + 1)"
                >
                  +
                </button>
              </div>
              <p class="w-24 text-right font-mono font-semibold text-slate-900">
                {{ formatCurrency(item.unit_price * item.quantity) }}
              </p>
              <button class="ml-1 text-slate-400 hover:text-red-600" @click="removeFromCart(item.product_id)">
                x
              </button>
            </div>
          </div>
        </Card>
      </div>

      <div class="space-y-4 xl:col-span-2">
        <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <Card>
          <template #header>
            <h3 class="font-semibold text-slate-900">Order Summary</h3>
          </template>

          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <Input
                :modelValue="discount"
                @update:modelValue="discount = $event"
                label="Discount"
                type="number"
                min="0"
              />
              <div class="flex flex-col gap-1">
                <label class="text-sm font-medium text-slate-700">Discount Type</label>
                <select
                  v-model="discountType"
                  class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                >
                  <option value="%">Percent (%)</option>
                  <option value="flat">Flat (INR)</option>
                </select>
              </div>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-600">Subtotal</span>
              <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(subtotal) }}</span>
            </div>

            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-600">Discount</span>
              <span class="font-mono text-slate-900">-{{ formatCurrency(discountAmount) }}</span>
            </div>

            <div class="flex items-center justify-between text-sm">
              <label class="flex cursor-pointer items-center gap-2">
                <input v-model="gstEnabled" type="checkbox" class="h-4 w-4 rounded accent-emerald-500" />
                <span class="text-slate-600">GST (5%)</span>
              </label>
              <span class="font-mono text-slate-900">+{{ formatCurrency(gstAmount) }}</span>
            </div>

            <div class="flex items-center justify-between border-t-2 border-slate-200 pt-3">
              <span class="font-semibold text-slate-900">Total</span>
              <span class="font-mono text-2xl font-bold text-emerald-600">{{ formatCurrency(total) }}</span>
            </div>
          </div>
        </Card>

        <div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">Payment Mode</p>
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="mode in ['cash', 'upi', 'credit']"
              :key="mode"
              class="rounded-xl p-3 text-sm font-medium transition-all"
              :class="
                paymentMode === mode
                  ? 'border-2 border-emerald-500 bg-emerald-50 text-emerald-600'
                  : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              "
              @click="selectPaymentMode(mode)"
            >
              {{ mode.toUpperCase() }}
            </button>
          </div>
          <p v-if="paymentMode === 'upi'" class="mt-2 text-xs text-slate-500">
            UPI checkout opens Razorpay and creates the bill only after successful payment verification.
          </p>
        </div>

        <Card v-if="paymentMode === 'credit'">
          <template #header>
            <h3 class="font-semibold text-slate-900">Customer</h3>
          </template>

          <div class="space-y-3">
            <Input
              :modelValue="customerSearch"
              @update:modelValue="handleCustomerSearch"
              placeholder="Search customer by name or phone..."
              icon="user"
            />

            <div v-if="customerLoading" class="text-sm text-slate-500">Searching customers...</div>

            <div v-else-if="customerResults.length > 0" class="space-y-2 rounded-xl border border-slate-200 p-2">
              <button
                v-for="customer in customerResults"
                :key="customer.customer_id"
                class="w-full rounded-lg px-3 py-2 text-left hover:bg-slate-50"
                @click="selectCustomer(customer)"
              >
                <p class="text-sm font-medium text-slate-900">{{ customer.name }}</p>
                <p class="text-xs text-slate-500">
                  {{ customer.phone }}
                  <span v-if="customer.credit_balance">· Due {{ formatCurrency(customer.credit_balance) }}</span>
                </p>
              </button>
            </div>

            <div v-if="selectedCustomer" class="rounded-xl bg-emerald-50 p-3">
              <p class="text-sm font-semibold text-emerald-900">{{ selectedCustomer.name }}</p>
              <p class="text-xs text-emerald-700">
                Limit {{ formatCurrency(selectedCustomer.credit_limit || 0) }} · Outstanding
                {{ formatCurrency(selectedCustomer.credit_balance || 0) }}
              </p>
            </div>
          </div>
        </Card>

        <Button
          variant="primary"
          size="lg"
          fullWidth
          :loading="checkoutLoading"
          :disabled="!canGenerateBill"
          @click="handleCheckout"
        >
          {{ paymentMode === 'upi' ? 'Pay With Razorpay' : 'Generate Bill' }}
        </Button>

        <div class="grid grid-cols-2 gap-3">
          <Button variant="secondary" size="md" fullWidth :disabled="!generatedBill" @click="printLatestBill">
            Print
          </Button>
          <Button variant="secondary" size="md" fullWidth :disabled="!generatedBill" @click="downloadLatestBillPdf">
            PDF
          </Button>
        </div>
      </div>
    </div>

    <Modal :modelValue="showSuccessModal" @update:modelValue="showSuccessModal = $event" @close="showSuccessModal = false">
      <div class="space-y-4 text-center">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
          <svg class="h-8 w-8 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-slate-900">Bill Generated Successfully</h3>
        <p class="text-sm text-slate-600">Receipt #{{ generatedBill?.receipt_number }}</p>

        <div class="space-y-2 rounded-xl bg-slate-50 p-4 text-left">
          <p class="text-sm">
            <span class="font-semibold">Total Amount:</span>
            {{ formatCurrency(generatedBill?.total_amount || 0) }}
          </p>
          <p class="text-sm">
            <span class="font-semibold">Payment Mode:</span>
            {{ generatedBill?.payment_method }}
          </p>
          <p class="text-sm">
            <span class="font-semibold">Status:</span>
            {{ generatedBill?.status }}
          </p>
          <p v-if="generatedBill?.payment_details?.payment_id" class="text-sm">
            <span class="font-semibold">Payment ID:</span>
            {{ generatedBill.payment_details.payment_id }}
          </p>
        </div>

        <div class="grid grid-cols-3 gap-2">
          <Button variant="secondary" fullWidth @click="printLatestBill">Print</Button>
          <Button variant="secondary" fullWidth @click="downloadLatestBillPdf">PDF</Button>
          <Button variant="primary" fullWidth @click="viewBillDetails">Details</Button>
        </div>
      </div>
    </Modal>
  </MainLayout>
</template>
