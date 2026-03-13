<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({
  data: Array,
  showLegend: {
    type: Boolean,
    default: true,
  },
})

const mockData = [
  { month: 'Jan', revenue: 285000, expenses: 198000 },
  { month: 'Feb', revenue: 312000, expenses: 210000 },
  { month: 'Mar', revenue: 298000, expenses: 205000 },
  { month: 'Apr', revenue: 341000, expenses: 224000 },
  { month: 'May', revenue: 318000, expenses: 218000 },
  { month: 'Jun', revenue: 324800, expenses: 221000 },
]

const chartData = computed(() => props.data || mockData)

const maxVal = computed(() => {
  return Math.max(...chartData.value.map((d) => Math.max(d.revenue, d.expenses)))
})

const hoveredIndex = ref(null)

const tooltip = ref({
  show: false,
  index: null,
})

const animatedHeights = ref(
  chartData.value.map(() => ({
    revenue: 0,
    expenses: 0,
  }))
)

onMounted(() => {
  // Stagger the animation
  chartData.value.forEach((_, i) => {
    setTimeout(() => {
      animatedHeights.value[i].revenue = chartData.value[i].revenue
      animatedHeights.value[i].expenses = chartData.value[i].expenses
    }, i * 80)
  })
})

const getBarHeight = (value) => {
  return (value / maxVal.value) * 100
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Header -->
    <h3 class="font-semibold text-slate-900">Revenue vs Expenses</h3>

    <!-- Legend -->
    <div v-if="showLegend" class="flex items-center gap-6">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-emerald-400"></div>
        <span class="text-xs text-slate-600">Revenue</span>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 rounded-full bg-slate-200"></div>
        <span class="text-xs text-slate-600">Expenses</span>
      </div>
    </div>

    <!-- Chart -->
    <div class="relative h-48 flex items-end gap-3 px-2">
      <div v-for="(item, i) in chartData" :key="`month-${i}`" class="flex flex-col items-center gap-1 flex-1 relative">
        <!-- Bars -->
        <div class="flex items-end gap-1 h-full w-full relative" @mouseenter="hoveredIndex = i" @mouseleave="hoveredIndex = null">
          <!-- Revenue bar -->
          <div
            class="bg-emerald-400 rounded-t-lg transition-all duration-500 flex-1"
            :style="{ height: `${getBarHeight(animatedHeights[i].revenue)}%` }"
            :class="hoveredIndex === i ? 'bg-emerald-500' : ''"
          ></div>

          <!-- Expense bar -->
          <div
            class="bg-slate-200 rounded-t-lg transition-all duration-500 flex-1"
            :style="{ height: `${getBarHeight(animatedHeights[i].expenses)}%` }"
            :class="hoveredIndex === i ? 'bg-slate-300' : ''"
          ></div>
        </div>

        <!-- Month label -->
        <p class="text-xs text-slate-400 mt-2">{{ item.month }}</p>

        <!-- Tooltip -->
        <div
          v-show="hoveredIndex === i"
          class="absolute -top-20 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-xs px-3 py-2 rounded-xl shadow-xl whitespace-nowrap pointer-events-none"
        >
          <p class="font-medium">{{ item.month }}</p>
          <p class="text-emerald-200">Revenue: ₹{{ (item.revenue / 100000).toFixed(2) }}L</p>
          <p class="text-slate-300">Expenses: ₹{{ (item.expenses / 100000).toFixed(2) }}L</p>
          <p class="text-yellow-200 mt-1">
            Net: ₹{{ ((item.revenue - item.expenses) / 100000).toFixed(2) }}L
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
