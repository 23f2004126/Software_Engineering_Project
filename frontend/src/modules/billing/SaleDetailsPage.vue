<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { salesService } from '../../services/apiService.js'
import { downloadSaleReceiptPdf, openSalePrintView } from '../../utils/receipt.js'

const router = useRouter()
const route = useRoute()

const bill = ref(null)
const loading = ref(true)
const error = ref('')

const billId = route.params.id

const subtotal = computed(() => {
  if (!bill.value || !bill.value.items) return 0
  return bill.value.items.reduce((sum, item) => sum + (parseFloat(item.subtotal) || 0), 0)
})

const fetchBillDetails = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await salesService.getSaleDetails(billId)
    bill.value = response
  } catch (err) {
    error.value = err.message || 'Failed to fetch bill details'
    console.error('Fetch bill error:', err)
  } finally {
    loading.value = false
  }
}

const reverseSale = async () => {
  if (!window.confirm('Are you sure you want to reverse this sale? This action cannot be undone.')) {
    return
  }

  try {
    await salesService.reverseSale(billId)
    alert('Sale reversed successfully')
    router.push('/sales')
  } catch (err) {
    alert('Failed to reverse sale: ' + (err.message || 'Unknown error'))
    console.error('Reverse error:', err)
  }
}

const downloadPdf = () => {
  if (bill.value) {
    downloadSaleReceiptPdf(bill.value)
  }
}

const printBill = () => {
  if (bill.value) {
    openSalePrintView(bill.value)
  }
}

onMounted(() => {
  fetchBillDetails()
})
</script>

<template>
  <MainLayout>
    <div class="max-w-3xl mx-auto space-y-6">
      <!-- Breadcrumb & Actions -->
      <div class="flex items-center justify-between">
        <div class="text-sm text-slate-500">
          <a href="/sales" class="text-emerald-600 hover:underline">Sales History</a>
          <span class="mx-2">â†’</span>
          {{ bill?.receipt_number || 'Loading...' }}
        </div>
        <div class="flex gap-3">
          <Button variant="secondary" size="sm" :disabled="!bill" @click="printBill">
            Print
          </Button>
          <Button variant="secondary" size="sm" :disabled="!bill" @click="downloadPdf">
            PDF
          </Button>
          <Button 
            v-if="bill?.status !== 'cancelled'"
            variant="secondary" 
            size="sm" 
            @click="reverseSale"
          >
            â†© Reverse
          </Button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-slate-500">Loading bill details...</p>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
        <p class="text-sm text-red-700">{{ error }}</p>
      </div>

      <!-- Invoice Card -->
      <Card v-else-if="bill" padding="none" :bordered="false">
        <!-- Header band -->
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
              </svg>
            </div>
            <div>
              <p class="text-lg font-bold">SONIK</p>
              <p class="text-xs text-white/70">Tax Invoice</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-lg font-bold">{{ bill.receipt_number }}</p>
            <p class="text-sm text-white/80">{{ formatDate(bill.bill_date, 'datetime') }}</p>
          </div>
        </div>

        <!-- Body -->
        <div class="p-6 space-y-6">
          <!-- Badges -->
          <div class="flex gap-2 flex-wrap">
            <span 
              v-if="bill.user_id"
              class="bg-blue-100 text-blue-700 text-xs px-3 py-1 rounded-full font-medium">
              Employee #{{ bill.user_id }}
            </span>
            <span
              class="text-xs px-3 py-1 rounded-full font-medium capitalize"
              :class="{
                'bg-emerald-100 text-emerald-700': bill.payment_method === 'cash',
                'bg-blue-100 text-blue-700': bill.payment_method === 'upi' || bill.payment_method === 'card',
                'bg-amber-100 text-amber-700': bill.payment_method === 'credit',
              }"
            >
              {{ bill.payment_method }}
            </span>
            <span
              class="text-xs px-3 py-1 rounded-full font-medium capitalize"
              :class="{
                'bg-emerald-100 text-emerald-700': bill.status === 'paid',
                'bg-amber-100 text-amber-700': bill.status === 'pending',
                'bg-red-100 text-red-700': bill.status === 'cancelled',
              }"
            >
              âœ“ {{ bill.status }}
            </span>
          </div>

          <!-- Store & Customer -->
          <div class="grid grid-cols-2 gap-6">
            <div class="bg-slate-50 rounded-xl p-4">
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Billed From</p>
              <p class="font-semibold text-slate-900">Sonik General Store</p>
              <p class="text-sm text-slate-600">Shop 12, MG Road, Hyderabad</p>
              <p class="text-xs text-slate-500 mt-2">GST: 36ABCDE1234F1Z5</p>
            </div>
            <div class="bg-slate-50 rounded-xl p-4">
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Billed To</p>
              <p class="font-semibold text-slate-900">{{ bill.customer?.name || 'Walk-in Customer' }}</p>
              <p class="text-sm text-slate-600">Over Counter</p>
            </div>
          </div>

          <!-- Items Table -->
          <div>
            <table class="w-full text-sm border-collapse">
              <thead>
                <tr class="border-b-2 border-slate-200">
                  <th class="text-left py-2 font-semibold text-slate-900 w-8">#</th>
                  <th class="text-left py-2 font-semibold text-slate-900">Product</th>
                  <th class="text-center py-2 font-semibold text-slate-900 w-16">Qty</th>
                  <th class="text-right py-2 font-semibold text-slate-900 w-20">Unit Price</th>
                  <th class="text-right py-2 font-semibold text-slate-900 w-24">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, i) in bill.items" :key="i" class="border-b border-slate-100">
                  <td class="py-3">{{ i + 1 }}</td>
                  <td class="py-3">{{ item.product?.name || 'Unknown Product' }}</td>
                  <td class="text-center py-3">{{ item.quantity }}</td>
                  <td class="text-right py-3 font-mono">â‚¹{{ item.unit_price }}</td>
                  <td class="text-right py-3 font-mono font-semibold">â‚¹{{ formatCurrency(item.subtotal) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Totals -->
          <div class="flex justify-end">
            <div class="w-64 space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-slate-600">Subtotal</span>
                <span class="font-mono font-semibold">{{ formatCurrency(subtotal) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-slate-600">GST (5%)</span>
                <span class="font-mono font-semibold">+{{ formatCurrency(bill.tax_amount) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-slate-600">Discount</span>
                <span class="font-mono font-semibold">âˆ’{{ formatCurrency(bill.discount_amount) }}</span>
              </div>
              <div class="border-t-2 border-slate-200 pt-2 flex justify-between">
                <span class="font-bold text-slate-900">Total</span>
                <span class="font-mono text-2xl font-bold text-emerald-600">{{ formatCurrency(bill.total_amount) }}</span>
              </div>
            </div>
          </div>

          <!-- Transaction Details -->
          <div v-if="bill.transactions && bill.transactions.length > 0" class="border-t-2 border-slate-200 pt-6">
            <h4 class="font-semibold text-slate-900 mb-3">Payment Transactions</h4>
            <div class="space-y-2">
              <div 
                v-for="(txn, i) in bill.transactions" 
                :key="i"
                class="flex justify-between items-center bg-slate-50 p-3 rounded-lg text-sm"
              >
                <div>
                  <p class="font-medium text-slate-900">{{ txn.payment_mode }}</p>
                  <p class="text-xs text-slate-500">{{ formatDate(txn.created_at, 'datetime') }}</p>
                </div>
                <span class="font-mono font-semibold">{{ formatCurrency(txn.amount) }}</span>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="border-t-2 border-slate-200 pt-6 text-center text-xs text-slate-500">
            <p>Thank you for your business!</p>
            <p class="mt-1">This is a computer-generated receipt.</p>
          </div>
        </div>
      </Card>
    </div>
  </MainLayout>
</template>
