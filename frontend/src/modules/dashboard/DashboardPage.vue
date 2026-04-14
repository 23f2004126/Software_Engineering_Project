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
    const [kpisResult, alertsResult] = await Promise.allSettled([
      dashboardService.getKPIs(),
      dashboardService.getAlerts()
    ])
    const kpis = kpisResult.status === 'fulfilled' ? kpisResult.value : null
    const alerts = alertsResult.status === 'fulfilled' ? alertsResult.value : null
    
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
    if (alerts && typeof alerts === 'object') {
      const alertsArray = []
      
      if (alerts.alert_counts?.low_stock > 0) {
        alertsArray.push({
          type: 'warning',
          icon: 'cube-transparent',
          title: `${alerts.alert_counts.low_stock} Items Low on Stock`,
          message: 'Some products are running low on inventory',
          linkLabel: 'View',
          linkRoute: '/inventory'
        })
      }
      
      if (alerts.alert_counts?.expiring_soon > 0) {
        alertsArray.push({
          type: 'danger',
          icon: 'hourglass',
          title: `${alerts.alert_counts.expiring_soon} Items Expiring Soon`,
          message: 'Some products are nearing their expiry date',
          linkLabel: 'View',
          linkRoute: '/inventory'
        })
      }
      
      if (alerts.alert_counts?.high_risk_customers > 0) {
        alertsArray.push({
          type: 'danger',
          icon: 'exclamation-triangle',
          title: `${alerts.alert_counts.high_risk_customers} High-Risk Customers`,
          message: 'Some customers have high credit utilization',
          linkLabel: 'View',
          linkRoute: '/customers'
        })
      }
      
      aiInsights.value = alertsArray
    }
    
    // Load recent sales transactions
    try {
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
    } catch (summaryErr) {
      console.error('Failed to load dashboard summary:', summaryErr)
    }

    // Set notifications from alerts
    if (alerts && alerts.alert_counts) {
      const notificationsArray = []
      
      if (alerts.low_stock && alerts.low_stock.length > 0) {
        notificationsArray.push(...alerts.low_stock.map(item => ({
          id: `low-stock-${item.product_id}`,
          icon: 'cube-transparent',
          title: `Low Stock: ${item.name}`,
          message: `Current: ${item.current_stock} | Reorder: ${item.reorder_level}`,
          type: 'warning'
        })))
      }
      
      if (alerts.expiring_soon && alerts.expiring_soon.length > 0) {
        notificationsArray.push(...alerts.expiring_soon.map(item => ({
          id: `expiring-${item.product_id}`,
          icon: 'hourglass',
          title: `Expiring Soon: ${item.name}`,
          message: `${item.days_left} days left | Stock: ${item.stock}`,
          type: 'danger'
        })))
      }
      
      if (alerts.high_risk_customers && alerts.high_risk_customers.length > 0) {
        notificationsArray.push(...alerts.high_risk_customers.map(cust => ({
          id: `high-risk-${cust.customer_id}`,
          icon: 'exclamation-triangle',
          title: `High Risk: ${cust.name}`,
          message: `${cust.usage_pct}% credit utilization`,
          type: 'danger'
        })))
      }
      
      notifications.value = notificationsArray
    }
    if (kpisResult.status === 'rejected' && alertsResult.status === 'rejected') {
      error.value = 'Failed to load dashboard data. Please try again.'
    }
  } catch (err) {
    error.value = err.message || 'Failed to load dashboard data'
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
  warning: { bg: 'bg-amber-100', text: 'text-amber-600' },
  danger: { bg: 'bg-red-100', text: 'text-red-600' },
}

const queryConvertorCard = {
  badge: 'Coming Soon',
  title: 'Query Convertor',
  description: 'Turn plain-language store questions into smart chatbot-ready queries from one focused dashboard entry point.',
  highlights: ['Natural language', 'Retail-friendly prompts', 'Frontend ready for chatbot hookup'],
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
          <h1 class="text-xl font-semibold text-slate-900">Good morning, {{ authStore.user?.name || authStore.user?.username || 'User' }}  👋</h1>
          <div class="bg-slate-100 text-slate-600 text-sm rounded-full px-3 py-1.5 font-medium">
            {{ new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'short', day: 'numeric' }) }}
          </div>
        </div>

        <div class="relative overflow-hidden rounded-3xl border border-emerald-200 bg-[radial-gradient(circle_at_top_left,_rgba(16,185,129,0.18),_transparent_35%),linear-gradient(135deg,#f7fee7_0%,#ecfdf5_45%,#eff6ff_100%)] p-6 shadow-sm">
          <div class="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-emerald-200/40 blur-2xl"></div>
          <div class="absolute bottom-0 right-20 h-20 w-20 rounded-full bg-sky-200/40 blur-2xl"></div>
          <div class="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div class="max-w-2xl">
              <div class="inline-flex items-center rounded-full border border-emerald-300 bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-emerald-700">
                {{ queryConvertorCard.badge }}
              </div>
              <h2 class="mt-3 text-2xl font-bold text-slate-900">{{ queryConvertorCard.title }}</h2>
              <p class="mt-2 text-sm leading-6 text-slate-600">{{ queryConvertorCard.description }}</p>
              <div class="mt-4 flex flex-wrap gap-2">
                <span
                  v-for="highlight in queryConvertorCard.highlights"
                  :key="highlight"
                  class="rounded-full bg-white/80 px-3 py-1 text-xs font-medium text-slate-700 shadow-sm ring-1 ring-slate-200"
                >
                  {{ highlight }}
                </span>
              </div>
            </div>
            <div class="flex flex-col items-start gap-3 lg:items-end">
              <button
                type="button"
                class="group inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:-translate-y-0.5 hover:bg-emerald-600"
              >
                <span>Open Query Convertor</span>
                <svg class="h-4 w-4 transition group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
              <p class="text-xs font-medium text-slate-500">Frontend preview only. We can wire the chatbot backend into this next.</p>
            </div>
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
                :class="`${(notificationColors[notif.type] || notificationColors.warning).bg}`"
                >
                  <component
                    :is="getIcon(notif.icon)"
                    class="w-4 h-4"
                  :class="`${(notificationColors[notif.type] || notificationColors.warning).text}`"
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
