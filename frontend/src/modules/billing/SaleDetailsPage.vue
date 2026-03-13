<script setup>
import { useRouter } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'

const router = useRouter()

const mockBill = {
  id: '#BL-00234',
  date: '2025-06-07T11:32:00',
  employee: 'Ravi Kumar',
  mode: 'upi',
  status: 'paid',
  store: {
    name: 'Sonik General Store',
    address: 'Shop 12, MG Road, Hyderabad',
    gst: '36ABCDE1234F1Z5',
  },
  customer: null,
  items: [
    { name: 'Amul Butter 100g', qty: 2, price: 58 },
    { name: 'Tata Salt 1kg', qty: 3, price: 22 },
    { name: 'Britannia Bread', qty: 1, price: 45 },
    { name: 'Parle-G 800g', qty: 2, price: 85 },
  ],
  discount: 20,
  gstRate: 5,
}

const subtotal = mockBill.items.reduce((sum, item) => sum + item.qty * item.price, 0)
const gstAmount = (subtotal - mockBill.discount) * (mockBill.gstRate / 100)
const total = subtotal - mockBill.discount + gstAmount
</script>

<template>
  <MainLayout>
    <div class="max-w-3xl mx-auto space-y-6">
      <!-- Breadcrumb & Actions -->
      <div class="flex items-center justify-between">
        <div class="text-sm text-slate-500">
          <a href="/sales" class="text-emerald-600 hover:underline">Sales History</a>
          <span class="mx-2">→</span>
          {{ mockBill.id }}
        </div>
        <div class="flex gap-3">
          <Button variant="secondary" size="sm">
            🖨 Print
          </Button>
          <Button variant="secondary" size="sm">
            ⬇ PDF
          </Button>
        </div>
      </div>

      <!-- Invoice Card -->
      <Card padding="none" bordered={false}>
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
            <p class="text-lg font-bold">{{ mockBill.id }}</p>
            <p class="text-sm text-white/80">{{ formatDate(mockBill.date, 'datetime') }}</p>
          </div>
        </div>

        <!-- Body -->
        <div class="p-6 space-y-6">
          <!-- Badges -->
          <div class="flex gap-2 flex-wrap">
            <span class="bg-blue-100 text-blue-700 text-xs px-3 py-1 rounded-full font-medium">
              {{ mockBill.employee }}
            </span>
            <span class="bg-amber-100 text-amber-700 text-xs px-3 py-1 rounded-full font-medium capitalize">
              {{ mockBill.mode }}
            </span>
            <span class="bg-emerald-100 text-emerald-700 text-xs px-3 py-1 rounded-full font-medium">
              ✓ {{ mockBill.status }}
            </span>
          </div>

          <!-- Store & Customer -->
          <div class="grid grid-cols-2 gap-6">
            <div class="bg-slate-50 rounded-xl p-4">
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Billed From</p>
              <p class="font-semibold text-slate-900">{{ mockBill.store.name }}</p>
              <p class="text-sm text-slate-600">{{ mockBill.store.address }}</p>
              <p class="text-xs text-slate-500 mt-2">GST: {{ mockBill.store.gst }}</p>
            </div>
            <div class="bg-slate-50 rounded-xl p-4">
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Billed To</p>
              <p v-if="mockBill.customer" class="font-semibold text-slate-900">{{ mockBill.customer.name }}</p>
              <p v-else class="font-semibold text-slate-900">Walk-in Customer</p>
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
                <tr v-for="(item, i) in mockBill.items" :key="i" class="border-b border-slate-100">
                  <td class="py-3">{{ i + 1 }}</td>
                  <td class="py-3">{{ item.name }}</td>
                  <td class="text-center py-3">{{ item.qty }}</td>
                  <td class="text-right py-3 font-mono">₹{{ item.price }}</td>
                  <td class="text-right py-3 font-mono font-semibold">₹{{ item.qty * item.price }}</td>
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
                <span class="text-slate-600">GST ({{ mockBill.gstRate }}%)</span>
                <span class="font-mono font-semibold">+{{ formatCurrency(gstAmount) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-slate-600">Discount</span>
                <span class="font-mono font-semibold">−₹{{ mockBill.discount }}</span>
              </div>
              <div class="border-t-2 border-slate-200 pt-2 flex justify-between">
                <span class="font-bold text-slate-900">Total</span>
                <span class="font-mono text-xl font-bold text-emerald-600">{{ formatCurrency(total) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-slate-50 border-t text-center text-xs text-slate-500 py-4">
          Thank you for shopping at Sonik! Returns accepted within 3 days.
        </div>
      </Card>
    </div>
  </MainLayout>
</template>
