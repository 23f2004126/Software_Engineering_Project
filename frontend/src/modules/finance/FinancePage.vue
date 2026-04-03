<script setup>
import { ref, computed, onMounted } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Table from '../../components/ui/Table.vue'
import { formatCurrency } from '../../utils/currency.js'
import { formatDate } from '../../utils/dateFormatter.js'
import { expenseService } from '../../services/apiService.js'

const form = ref({
  category: 'rent',
  amount: 0,
  date: new Date().toISOString().split('T')[0],
  title: '',
})

const errors = ref({})
const isSubmitting = ref(false)
const loading = ref(false)
const error = ref(null)

const expenses = ref([])

const handleAddExpense = async () => {
  errors.value = {}
  if (!form.value.amount) {
    errors.value.amount = 'Amount is required'
  }
  if (!form.value.title) {
    errors.value.title = 'Title is required'
  }
  if (Object.keys(errors.value).length > 0) return

  isSubmitting.value = true
  try {
    await expenseService.addExpense({
      title: form.value.title,
      amount: form.value.amount,
      category: form.value.category,
      note: form.value.title,
      expense_date: form.value.date,
      recurring: false,
    })
    
    // Reload expenses
    await loadExpenses()
    
    form.value = {
      category: 'rent',
      amount: 0,
      date: new Date().toISOString().split('T')[0],
      title: '',
    }
  } catch (err) {
    error.value = err.message
  } finally {
    isSubmitting.value = false
  }
}

const loadExpenses = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await expenseService.getExpenses({
      limit: 100
    })
    expenses.value = data || []
  } catch (err) {
    error.value = err.message
    console.error('Failed to load expenses:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadExpenses()
})

const totalExpenses = computed(() => {
  return expenses.value.reduce((sum, exp) => sum + (parseFloat(exp.amount) || 0), 0)
})

const categoryExpenses = computed(() => {
  const obj = {}
  expenses.value.forEach((exp) => {
    const category = exp.category || 'other'
    obj[category] = (obj[category] || 0) + (parseFloat(exp.amount) || 0)
  })
  return obj
})

const categoryColors = {
  rent: { bg: 'bg-red-50', text: 'text-red-600', icon: '🏢' },
  salary: { bg: 'bg-blue-50', text: 'text-blue-600', icon: '💰' },
  utilities: { bg: 'bg-yellow-50', text: 'text-yellow-600', icon: '⚡' },
  maintenance: { bg: 'bg-purple-50', text: 'text-purple-600', icon: '🔧' },
  supplies: { bg: 'bg-green-50', text: 'text-green-600', icon: '📦' },
  other: { bg: 'bg-slate-50', text: 'text-slate-600', icon: '📋' },
}

const todayRevenue = 18450
const todayExpenses = computed(() => {
  return expenses.value
    .filter(exp => new Date(exp.expense_date).toDateString() === new Date().toDateString())
    .reduce((sum, exp) => sum + (parseFloat(exp.amount) || 0), 0)
})
const netProfit = computed(() => todayRevenue - todayExpenses.value)
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

            <!-- Title -->
            <Input
              v-model="form.title"
              label="Title"
              placeholder="e.g., Monthly rent - June"
              :error="errors.title"
            />

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
          <div v-if="loading" class="p-8 text-center text-slate-500">Loading expenses...</div>
          <div v-else-if="error" class="p-8 text-center text-red-600">Error: {{ error }}</div>
          <div v-else-if="expenses.length === 0" class="p-8 text-center text-slate-500">No expenses recorded yet</div>
          <Table
            v-else
            :columns="[
              { key: 'expense_date', label: 'Date' },
              { key: 'category', label: 'Category' },
              { key: 'title', label: 'Title' },
              { key: 'amount', label: 'Amount' },
              { key: 'actions', label: '' },
            ]"
            :rows="expenses"
            striped
          >
            <template #expense_date="{ value }">
              <span class="text-sm">{{ new Date(value).toLocaleDateString() }}</span>
            </template>
            <template #category="{ value }">
              <span class="text-sm font-medium">{{ categoryColors[value]?.icon || '📋' }} {{ value }}</span>
            </template>
            <template #title="{ value }">
              <span class="text-sm text-slate-600">{{ value }}</span>
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
