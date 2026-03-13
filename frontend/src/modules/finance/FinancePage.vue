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
  category: 'rent',
  amount: 0,
  date: new Date().toISOString().split('T')[0],
  description: '',
})

const errors = ref({})
const isSubmitting = ref(false)

const mockExpenses = [
  { id: 1, date: '2025-06-05', category: 'rent', amount: 15000, description: 'Shop rent - June', recurring: true },
  { id: 2, date: '2025-06-04', category: 'salary', amount: 18000, description: 'Salary - Ravi Kumar', recurring: false },
  { id: 3, date: '2025-06-03', category: 'utilities', amount: 2500, description: 'Electricity bill', recurring: true },
  { id: 4, date: '2025-06-02', category: 'maintenance', amount: 1200, description: 'Fridge cooling repair', recurring: false },
  { id: 5, date: '2025-06-01', category: 'supplies', amount: 3400, description: 'Packaging materials', recurring: false },
]

const handleAddExpense = () => {
  errors.value = {}
  if (!form.value.amount) {
    errors.value.amount = 'Amount is required'
  }
  if (Object.keys(errors.value).length > 0) return

  isSubmitting.value = true
  setTimeout(() => {
    isSubmitting.value = false
    form.value = {
      category: 'rent',
      amount: 0,
      date: new Date().toISOString().split('T')[0],
      description: '',
    }
  }, 800)
}

const totalExpenses = computed(() => {
  return mockExpenses.reduce((sum, exp) => sum + exp.amount, 0)
})

const categoryExpenses = computed(() => {
  const obj = {}
  mockExpenses.forEach((exp) => {
    obj[exp.category] = (obj[exp.category] || 0) + exp.amount
  })
  return obj
})

const categoryColors = {
  rent: { bg: 'bg-red-50', text: 'text-red-600', icon: '🏢' },
  salary: { bg: 'bg-blue-50', text: 'text-blue-600', icon: '💰' },
  utilities: { bg: 'bg-yellow-50', text: 'text-yellow-600', icon: '⚡' },
  maintenance: { bg: 'bg-purple-50', text: 'text-purple-600', icon: '🔧' },
  supplies: { bg: 'bg-green-50', text: 'text-green-600', icon: '📦' },
}

const todayRevenue = 18450
const todayExpenses = 2200
const netProfit = computed(() => todayRevenue - todayExpenses)
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-5 gap-6">
      <!-- LEFT: Add Expense Form -->
      <div class="col-span-2">
        <Card padding="lg">
          <div class="flex items-center gap-2 mb-6 pb-4 border-b border-slate-100">
            <svg class="w-5 h-5 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
            </svg>
            <h3 class="font-semibold text-slate-900">Record Expense</h3>
          </div>

          <form class="space-y-4" @submit.prevent="handleAddExpense">
            <!-- Category -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">Category</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="(category, key) in categoryColors"
                  :key="key"
                  type="button"
                  class="p-3 rounded-xl text-sm font-medium border text-center transition-all cursor-pointer"
                  :class="
                    form.category === key
                      ? `border-emerald-500 bg-emerald-50 text-emerald-600`
                      : `border-slate-200 bg-white hover:bg-slate-50`
                  "
                  @click="form.category = key"
                >
                  {{ category.icon }}
                  {{ key.charAt(0).toUpperCase() + key.slice(1) }}
                </button>
              </div>
            </div>

            <!-- Amount -->
            <Input
              v-model.number="form.amount"
              label="Amount"
              type="number"
              prefix="₹"
              placeholder="0.00"
              :error="errors.amount"
            />

            <!-- Date -->
            <Input v-model="form.date" label="Date" type="date" />

            <!-- Description -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
              <input
                v-model="form.description"
                type="text"
                class="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                placeholder="e.g., Monthly rent - June"
              />
            </div>

            <!-- Recurring -->
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" class="w-4 h-4 rounded border-slate-300" />
              <span class="text-sm text-slate-600">Mark as recurring</span>
            </label>

            <Button variant="primary" fullWidth :loading="isSubmitting" @click="handleAddExpense">
              Add Expense
            </Button>
          </form>
        </Card>

        <!-- Summary -->
        <Card class="mt-5">
          <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Today's Summary</p>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Revenue</span>
              <span class="font-mono font-semibold text-slate-900">{{ formatCurrency(todayRevenue) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Expenses</span>
              <span class="font-mono font-semibold text-red-600">- {{ formatCurrency(todayExpenses) }}</span>
            </div>
            <div class="border-t border-slate-100 pt-3 flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-900">Net Profit</span>
              <span class="font-mono font-bold text-emerald-600 text-lg">{{ formatCurrency(netProfit) }}</span>
            </div>
          </div>
        </Card>
      </div>

      <!-- RIGHT: Expenses List & Analytics -->
      <div class="col-span-3 space-y-6">
        <!-- Category Breakdown -->
        <div class="grid grid-cols-3 gap-4">
          <Card v-for="(amount, category) in categoryExpenses" :key="category" :class="categoryColors[category].bg">
            <p class="text-xs font-semibold text-slate-400 uppercase">{{ category }}</p>
            <p :class="`font-mono text-2xl font-bold ${categoryColors[category].text} mt-2`">{{ formatCurrency(amount) }}</p>
          </Card>
        </div>

        <!-- Expenses Table -->
        <Card padding="none">
          <Table
            :columns="[
              { key: 'date', label: 'Date' },
              { key: 'category', label: 'Category' },
              { key: 'description', label: 'Description' },
              { key: 'amount', label: 'Amount' },
              { key: 'actions', label: '' },
            ]"
            :rows="mockExpenses"
            striped
          >
            <template #category="{ value }">
              <span class="text-sm font-medium">{{ categoryColors[value]?.icon }} {{ value }}</span>
            </template>
            <template #amount="{ value }">
              <span class="font-mono font-semibold text-red-600">- {{ formatCurrency(value) }}</span>
            </template>
            <template #actions>
              <button class="text-slate-400 hover:text-red-600 transition-colors">✕</button>
            </template>
          </Table>
        </Card>

        <!-- Expense Breakdown Bar -->
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase mb-4">Category Distribution</p>
          <div class="space-y-3">
            <div v-for="(amount, category) in categoryExpenses" :key="category" class="space-y-1">
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-600">{{ category }}</span>
                <span class="font-semibold text-slate-900">{{ ((amount / totalExpenses) * 100).toFixed(0) }}%</span>
              </div>
              <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  :class="categoryColors[category].bg.replace('50', '500')"
                  class="h-full transition-all"
                  :style="{ width: `${(amount / totalExpenses) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
