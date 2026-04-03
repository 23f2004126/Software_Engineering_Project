<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/authStore.js'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import SalesTrendChart from '../../components/charts/SalesTrendChart.vue'
import RevenueExpenseChart from '../../components/charts/RevenueExpenseChart.vue'
import AIInsightCard from '../../components/ai/AIInsightCard.vue'
import { formatCurrency } from '../../utils/currency.js'
import { getIcon } from '../../utils/iconMap.js'
import { dashboardService } from '../../services/apiService.js'

const authStore = useAuthStore()

const kpiCards = ref([
  { label: "Today's Sales", value: 0, displayValue: 0, change: 0, icon: 'shopping-cart', color: 'emerald' },
  { label: "Today's Net Profit", value: 0, displayValue: 0, change: 0, icon: 'arrow-trending-up', color: 'teal' },
  { label: 'Monthly Revenue', value: 0, displayValue: 0, change: 0, icon: 'currency-rupee', color: 'blue' },
  { label: 'Outstanding Credit', value: 0, displayValue: 0, change: 0, icon: 'document-text', color: 'amber' },
  { label: 'Low Stock Items', value: 0, displayValue: 0, change: null, icon: 'cube-transparent', color: 'red' },
  { label: 'Expiring Soon', value: 0, displayValue: 0, change: null, icon: 'hourglass', color: 'amber' },
])

const loading = ref(false)
const error = ref(null)

// Employee view cards (only Today's Sales and Low Stock)
const employeeKpiCards = computed(() => {
  return kpiCards.value.filter(card => 
    card.label === "Today's Sales" || card.label === 'Low Stock Items'
  )
})

const aiInsights = ref([])
const recentTransactions = ref([])
const notifications = ref([])
const dismissedInsights = ref(new Set())

// Load dashboard data
onMounted(async () => {
  await loadDashboardData()
  // Animate KPI count-up
  animateKPIs()
})

const loadDashboardData = async () => {
  loading.value = true
  error.value = null
  try {
    const [kpis, alerts] = await Promise.all([
      dashboardService.getKPIs(),
      dashboardService.getAlerts()
    ])
    
    // Update KPI cards with real data
    if (kpis) {
      kpiCards.value[0].value = kpis.today_sales || 0
      kpiCards.value[1].value = kpis.today_profit || 0
      kpiCards.value[2].value = kpis.monthly_revenue || 0
      kpiCards.value[3].value = kpis.outstanding_credit || 0
      kpiCards.value[4].value = kpis.low_stock_count || 0
      kpiCards.value[5].value = kpis.expiring_count || 0
    }
    
    // Map alerts to insights format
    if (alerts && alerts.length > 0) {
      aiInsights.value = alerts.slice(0, 4).map((alert, idx) => ({
        type: alert.type || (idx === 0 ? 'warning' : idx === 1 ? 'danger' : 'success'),
        icon: alert.icon || 'sparkles',
        title: alert.title || 'Alert',
        message: alert.message || '',
        linkLabel: 'View',
        linkRoute: '/inventory'
      }))
    }
    
    // Load recent sales transactions
    const summary = await dashboardService.getSummary()
    if (summary && summary.recent_sales) {
      recentTransactions.value = summary.recent_sales.slice(0, 5).map(sale => ({
        id: `#BL-${sale.bill_id}`,
        customer: sale.customer_name || 'Walk-in Customer',
        amount: sale.total_amount,
        mode: sale.payment_method || 'cash',
        time: new Date(sale.bill_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }))
    }

    // Set notifications from alerts
    if (alerts && alerts.length > 0) {
      notifications.value = alerts.map(alert => ({
        id: alert.id,
        icon: alert.icon || 'sparkles',
        title: alert.title,
        message: alert.message,
        type: alert.type
      }))
    }
  } catch (err) {
    error.value = err.message
    console.error('Failed to load dashboard:', err)
  } finally {
    loading.value = false
  }
}

const animateKPIs = () => {
  kpiCards.value.forEach((card, index) => {
    setTimeout(() => {
      const max = card.value
      const increment = Math.ceil(max / 40)
      const interval = setInterval(() => {
        if (card.displayValue < max) {
          card.displayValue += increment
          if (card.displayValue > max) card.displayValue = max
        } else {
          clearInterval(interval)
        }
      }, 20)
    }, index * 60)
  })
}

const handleDismissInsight = (index) => {
  dismissedInsights.value.add(index)
}

const colorClasses = {
  emerald: { bg: 'bg-emerald-100', text: 'text-emerald-600' },
  teal: { bg: 'bg-teal-100', text: 'text-teal-600' },
  blue: { bg: 'bg-blue-100', text: 'text-blue-600' },
  amber: { bg: 'bg-amber-100', text: 'text-amber-600' },
  red: { bg: 'bg-red-100', text: 'text-red-600' },
}

const notificationColors = {
  stock: { bg: 'bg-red-100', text: 'text-red-600' },
  credit: { bg: 'bg-amber-100', text: 'text-amber-600' },
  expiry: { bg: 'bg-amber-100', text: 'text-amber-600' },
  shift: { bg: 'bg-blue-100', text: 'text-blue-600' },
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Error state -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <p class="font-medium">Failed to load dashboard</p>
        <p class="text-sm mt-1">{{ error }}</p>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block">
          <div class="animate-spin w-8 h-8 border-4 border-slate-200 border-t-emerald-600 rounded-full"></div>
        </div>
        <p class="text-slate-500 mt-4">Loading dashboard data...</p>
      </div>

      <!-- Main content -->
      <template v-else>
        <!-- Greeting -->
        <div class="flex items-center justify-between">
          <h1 class="text-xl font-semibold text-slate-900">Good morning, Anjali 👋</h1>
          <div class="bg-slate-100 text-slate-600 text-sm rounded-full px-3 py-1.5 font-medium">
            {{ new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'short', day: 'numeric' }) }}
          </div>
        </div>

        <!-- KPI Cards -->
        <div v-if="authStore.isOwner" class="grid grid-cols-3 gap-5">
        <Card
          v-for="(card, index) in kpiCards"
          :key="index"
          hover
          :style="{ '--animation-delay': `${index * 60}ms` }"
          class="animate-slide-up"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{{ card.label }}</p>
              <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ card.displayValue }}</p>
              <div v-if="card.change !== null" class="flex items-center gap-1 mt-2 text-xs">
                <svg
                  v-if="card.change > 0"
                  class="w-3 h-3 text-emerald-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z" clip-rule="evenodd" />
                </svg>
                <svg v-else class="w-3 h-3 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M12 13a1 1 0 110 2H7a1 1 0 01-1-1V9a1 1 0 112 0v3.586l4.293-4.293a1 1 0 011.414 1.414L9.414 13H12z" clip-rule="evenodd" />
                </svg>
                <span :class="card.change > 0 ? 'text-emerald-600' : 'text-red-600'">
                  {{ Math.abs(card.change) }}%
                </span>
              </div>
            </div>
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="`${colorClasses[card.color].bg}`"
            >
              <component
                :is="getIcon(card.icon)"
                class="w-5 h-5"
                :class="`${colorClasses[card.color].text}`"
              />
            </div>
          </div>
        </Card>
      </div>

      <!-- Employee KPI Cards (simplified) -->
      <div v-if="authStore.isEmployee" class="grid grid-cols-2 gap-5">
        <Card hover v-for="(card, index) in employeeKpiCards" :key="index">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{{ card.label }}</p>
              <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ card.displayValue }}</p>
              <div v-if="card.change !== null" class="flex items-center gap-1 mt-2 text-xs">
                <svg
                  v-if="card.change > 0"
                  class="w-3 h-3 text-emerald-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z" clip-rule="evenodd" />
                </svg>
                <span :class="card.change > 0 ? 'text-emerald-600' : 'text-red-600'">
                  {{ Math.abs(card.change) }}%
                </span>
              </div>
            </div>
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="`${colorClasses[card.color].bg}`"
            >
              <component
                :is="getIcon(card.icon)"
                class="w-5 h-5"
                :class="`${colorClasses[card.color].text}`"
              />
            </div>
          </div>
        </Card>
      </div>

      <!-- Charts row (owner only) -->
      <div v-if="authStore.isOwner" class="grid grid-cols-5 gap-5">
        <div class="col-span-3">
          <Card>
            <SalesTrendChart :showToggle="true" />
          </Card>
        </div>
        <div class="col-span-2">
          <Card>
            <RevenueExpenseChart :showLegend="true" />
          </Card>
        </div>
      </div>

      <!-- AI Insights (owner only) -->
      <Card v-if="authStore.isOwner">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" />
              </svg>
              <h3 class="font-semibold text-slate-900">AI Insights</h3>
            </div>
            <a href="#" class="text-emerald-600 text-xs font-medium hover:underline">View All</a>
          </div>
        </template>
        <div class="space-y-1 -mx-6 -my-5">
          <AIInsightCard
            v-for="(insight, index) in aiInsights"
            v-show="!dismissedInsights.has(index)"
            :key="index"
            v-bind="insight"
            @dismiss="handleDismissInsight(index)"
          />
        </div>
      </Card>

      <!-- Bottom grid -->
      <div class="grid grid-cols-5 gap-5">
        <!-- Recent transactions -->
        <div class="col-span-3">
          <Card>
            <template #header>
              <h3 class="font-semibold text-slate-900">Recent Transactions</h3>
            </template>
            <div class="space-y-0">
              <div
                v-for="txn in recentTransactions"
                :key="txn.id"
                class="flex items-center justify-between py-3 border-b border-slate-100 last:border-0 px-0"
              >
                <div class="flex-1">
                  <p class="text-sm font-medium text-slate-900">{{ txn.id }}</p>
                  <p class="text-xs text-slate-500">{{ txn.customer }}</p>
                </div>
                <p class="font-mono font-semibold text-slate-900">₹{{ txn.amount.toLocaleString('en-IN') }}</p>
                <span
                  class="text-xs px-2 py-1 rounded-full ml-4"
                  :class="{
                    'bg-emerald-100 text-emerald-700': txn.mode === 'cash',
                    'bg-blue-100 text-blue-700': txn.mode === 'upi',
                    'bg-amber-100 text-amber-700': txn.mode === 'credit',
                  }"
                >
                  {{ txn.mode.toUpperCase() }}
                </span>
                <p class="text-xs text-slate-400 ml-3 w-16 text-right">{{ txn.time }}</p>
              </div>
            </div>
            <a href="/sales" class="text-emerald-600 text-sm font-medium hover:underline inline-block mt-4">
              View All Sales →
            </a>
          </Card>
        </div>

        <!-- Notifications -->
        <div class="col-span-2">
          <Card>
            <template #header>
              <h3 class="font-semibold text-slate-900">Notifications</h3>
            </template>
            <div class="space-y-0 -mx-6 -my-5">
              <div
                v-for="notif in notifications"
                :key="notif.id"
                class="flex items-start gap-3 px-6 py-3 border-b border-slate-100 last:border-0"
              >
                <div
                  class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                  :class="`${notificationColors[notif.type].bg}`"
                >
                  <component
                    :is="getIcon(notif.icon)"
                    class="w-4 h-4"
                    :class="`${notificationColors[notif.type].text}`"
                  />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-900">{{ notif.title }}</p>
                  <p class="text-xs text-slate-500 mt-0.5 line-clamp-2">{{ notif.message }}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
      </template>
    </div>
  </MainLayout>
</template>

<style scoped>
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slide-up 0.3s ease forwards;
  animation-delay: var(--animation-delay, 0ms);
}
</style>
