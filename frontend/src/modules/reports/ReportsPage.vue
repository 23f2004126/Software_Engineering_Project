<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import { downloadBusinessReportPdf } from '../../utils/reportDownload.js'

const selectedReport = ref('daily')
const dateRange = ref('last-7-days')
const selectedReportId = ref(null)

const reports = ref([
  {
    id: 1,
    type: 'daily',
    name: 'Daily Sales Report - 2025-06-05',
    date: '2025-06-05',
    generatedAt: '2025-06-05 18:30',
    metrics: {
      totalSales: 45000,
      totalTransactions: 128,
      avgTransactionValue: 351,
      topProduct: 'Rice (20KG)',
      topCategory: 'Groceries',
    },
    status: 'completed',
  },
  {
    id: 2,
    type: 'daily',
    name: 'Daily Sales Report - 2025-06-04',
    date: '2025-06-04',
    generatedAt: '2025-06-04 18:30',
    metrics: {
      totalSales: 52000,
      totalTransactions: 145,
      avgTransactionValue: 359,
      topProduct: 'Milk (1L)',
      topCategory: 'Dairy',
    },
    status: 'completed',
  },
  {
    id: 3,
    type: 'weekly',
    name: 'Weekly Summary - Week 23',
    date: '2025-06-08',
    generatedAt: '2025-06-08 20:00',
    metrics: {
      totalSales: 325000,
      totalTransactions: 892,
      avgTransactionValue: 364,
      topProduct: 'Rice (20KG)',
      topCategory: 'Groceries',
    },
    status: 'completed',
  },
  {
    id: 4,
    type: 'monthly',
    name: 'Monthly Summary - June 2025',
    date: '2025-06-30',
    generatedAt: 'Scheduled for 2025-06-30',
    metrics: {
      totalSales: 1450000,
      totalTransactions: 3850,
      avgTransactionValue: 376,
      topProduct: 'Bread (500g)',
      topCategory: 'Bakery',
    },
    status: 'scheduled',
  },
  {
    id: 5,
    type: 'inventory',
    name: 'Inventory Status Report',
    date: '2025-06-05',
    generatedAt: '2025-06-05 19:15',
    metrics: {
      totalItems: 245,
      lowStockItems: 12,
      expiringItems: 5,
      totalValue: 450000,
      avgStockLevel: '78%',
    },
    status: 'completed',
  },
  {
    id: 6,
    type: 'credit',
    name: 'Credit Analysis Report',
    date: '2025-06-05',
    generatedAt: '2025-06-05 19:45',
    metrics: {
      totalOutstanding: 245000,
      totalCustomers: 5,
      overdue: 1,
      atRisk: 2,
      goodStanding: 2,
    },
    status: 'completed',
  },
])

const filteredReports = computed(() => {
  return reports.value.filter(r => {
    if (selectedReport.value !== 'all' && r.type !== selectedReport.value) return false
    return true
  })
})

const reportDetails = computed(() => {
  return reports.value.find(r => r.id === selectedReportId.value)
})

const downloadReport = (reportId) => {
  const report = reports.value.find(r => r.id === reportId)
  if (!report) return
  downloadBusinessReportPdf(report)
}

const viewDetails = (reportId) => {
  selectedReportId.value = reportId
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Business Reports</h1>
          <p class="text-sm text-slate-500 mt-1">
            View auto-generated structured business reports and analytics
          </p>
        </div>
        <button class="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition-colors">
          Generate Custom Report
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Reports List -->
        <div class="lg:col-span-2 space-y-4">
          <!-- Filters -->
          <div class="flex gap-3">
            <select
              v-model="selectedReport"
              class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="all">All Reports</option>
              <option value="daily">Daily Sales</option>
              <option value="weekly">Weekly Summary</option>
              <option value="monthly">Monthly Summary</option>
              <option value="inventory">Inventory Status</option>
              <option value="credit">Credit Analysis</option>
            </select>
            <select
              v-model="dateRange"
              class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="last-7-days">Last 7 days</option>
              <option value="last-30-days">Last 30 days</option>
              <option value="last-90-days">Last 90 days</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>

          <!-- Reports Grid -->
          <div class="space-y-3">
            <div
              v-for="report in filteredReports"
              :key="report.id"
              @click="viewDetails(report.id)"
              :class="[
                'p-4 rounded-lg border cursor-pointer transition-all',
                selectedReportId === report.id
                  ? 'bg-emerald-50 border-emerald-300 shadow-md'
                  : 'bg-white border-slate-200 hover:shadow-md'
              ]"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <h3 class="font-semibold text-slate-900">{{ report.name }}</h3>
                  <p class="text-xs text-slate-500 mt-1">Generated: {{ report.generatedAt }}</p>
                  <div class="flex items-center gap-2 mt-3">
                    <span :class="['text-xs px-2 py-1 rounded font-semibold', report.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700']">
                      {{ report.status }}
                    </span>
                    <span class="text-xs text-slate-400">
                      {{ report.type === 'daily' ? '📊' : report.type === 'weekly' ? '📈' : report.type === 'monthly' ? '📉' : report.type === 'inventory' ? '📦' : '💳' }}
                    </span>
                  </div>
                </div>
                <button
                  @click.stop="downloadReport(report.id)"
                  class="flex-shrink-0 p-2 text-slate-400 hover:text-emerald-600 transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Report Details -->
        <div v-if="reportDetails" class="lg:col-span-1">
          <Card padding="lg" class="sticky top-20">
            <h3 class="font-bold text-slate-900 mb-4">Report Details</h3>

            <div class="space-y-4">
              <div>
                <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold">Report Name</p>
                <p class="text-sm font-semibold text-slate-900 mt-1">{{ reportDetails.name }}</p>
              </div>

              <div class="border-t border-slate-200 pt-4">
                <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold">Key Metrics</p>
                <div class="space-y-2 mt-3">
                  <div v-for="(value, key) in reportDetails.metrics" :key="key" class="flex justify-between items-center">
                    <span class="text-xs text-slate-600 capitalize">
                      {{ key.replace(/([A-Z])/g, ' $1').trim() }}
                    </span>
                    <span class="text-sm font-semibold text-slate-900">{{ value }}</span>
                  </div>
                </div>
              </div>

              <div class="border-t border-slate-200 pt-4">
                <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold">Actions</p>
                <div class="space-y-2 mt-3">
                  <button @click="downloadReport(reportDetails.id)" class="w-full px-3 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition-colors">
                    ⬇ Download PDF
                  </button>
                  <button class="w-full px-3 py-2 rounded-lg bg-slate-100 text-slate-700 text-sm font-semibold hover:bg-slate-200 transition-colors">
                    📧 Email Report
                  </button>
                  <button class="w-full px-3 py-2 rounded-lg bg-slate-100 text-slate-700 text-sm font-semibold hover:bg-slate-200 transition-colors">
                    🔄 Regenerate
                  </button>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Empty State -->
        <div v-if="!reportDetails && filteredReports.length > 0" class="lg:col-span-1">
          <Card padding="lg" class="h-full flex items-center justify-center">
            <div class="text-center">
              <div class="text-4xl mb-2">📋</div>
              <p class="text-slate-500 font-medium text-sm">Select a report to view details</p>
            </div>
          </Card>
        </div>
      </div>

      <!-- Empty State for No Reports -->
      <div v-if="filteredReports.length === 0" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="text-4xl mb-2">📊</div>
          <p class="text-slate-500 font-medium">No reports found</p>
          <p class="text-slate-400 text-sm mt-1">Try adjusting your filters</p>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<style scoped>
</style>
