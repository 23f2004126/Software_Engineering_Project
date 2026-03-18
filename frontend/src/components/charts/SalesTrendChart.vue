<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: Array,
  period: {
    type: String,
    default: '7d',
  },
  height: {
    type: Number,
    default: 160,
  },
  showToggle: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['period-change'])

const currentPeriod = ref(props.period)

const mockData7d = [
  { label: 'Mon', value: 12400 },
  { label: 'Tue', value: 18200 },
  { label: 'Wed', value: 9800 },
  { label: 'Thu', value: 21500 },
  { label: 'Fri', value: 16300 },
  { label: 'Sat', value: 24800 },
  { label: 'Sun', value: 14100 },
]

const mockData30d = Array.from({ length: 30 }, (_, i) => ({
  label: `Day ${i + 1}`,
  value: Math.floor(Math.random() * 15000) + 10000,
}))

const chartData = computed(() => {
  return props.data || (currentPeriod.value === '30d' ? mockData30d : mockData7d)
})

const maxVal = computed(() => Math.max(...chartData.value.map((d) => d.value)))
const minVal = computed(() => Math.min(...chartData.value.map((d) => d.value)))

const svgWidth = 400
const svgHeight = props.height

const points = computed(() => {
  const padding = 20
  const chartWidth = svgWidth - padding * 2
  const chartHeight = svgHeight - padding * 2
  const range = maxVal.value - minVal.value || 1

  return chartData.value.map((d, i) => ({
    x: padding + (i / (chartData.value.length - 1)) * chartWidth,
    y: svgHeight - padding - ((d.value - minVal.value) / range) * chartHeight,
  }))
})

const polylineString = computed(() => {
  return points.value.map((p) => `${p.x},${p.y}`).join(' ')
})

const areaPoints = computed(() => {
  if (points.value.length === 0) return ''
  const padding = 20
  const chartWidth = svgWidth - padding * 2
  const firstPoint = points.value[0]
  const lastPoint = points.value[points.value.length - 1]

  return (
    polylineString.value +
    ` ${padding + chartWidth},${svgHeight - padding} ${padding},${svgHeight - padding}`
  )
})

const hoveredIndex = ref(null)

const changePeriod = (period) => {
  currentPeriod.value = period
  emit('period-change', period)
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Header with toggle -->
    <div v-if="showToggle" class="flex items-center justify-between">
      <h3 class="font-semibold text-slate-900">Sales Trend</h3>
      <div class="flex items-center gap-2">
        <button
          @click="changePeriod('7d')"
          class="text-xs px-3 py-1.5 rounded-full transition-all"
          :class="
            currentPeriod === '7d'
              ? 'bg-emerald-500 text-white'
              : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
          "
        >
          7 Days
        </button>
        <button
          @click="changePeriod('30d')"
          class="text-xs px-3 py-1.5 rounded-full transition-all"
          :class="
            currentPeriod === '30d'
              ? 'bg-emerald-500 text-white'
              : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
          "
        >
          30 Days
        </button>
      </div>
    </div>

    <!-- Chart -->
    <div class="relative">
      <svg :viewBox="`0 0 ${svgWidth} ${svgHeight}`" class="w-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" style="stop-color: #10b981; stop-opacity: 0.2" />
            <stop offset="100%" style="stop-color: #10b981; stop-opacity: 0" />
          </linearGradient>
        </defs>

        <!-- Gridlines -->
        <line
          v-for="i in 4"
          :key="`grid-${i}`"
          :x1="20"
          :y1="(svgHeight / 5) * i"
          :x2="svgWidth - 20"
          :y2="(svgHeight / 5) * i"
          stroke="#E2E8F0"
          stroke-dasharray="4 4"
          stroke-width="1"
        />

        <!-- Area fill -->
        <polygon v-if="points.length > 0" :points="areaPoints" fill="url(#areaGrad)" />

        <!-- Line -->
        <polyline
          v-if="points.length > 0"
          :points="polylineString"
          stroke="#10B981"
          stroke-width="2"
          fill="none"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Data points -->
        <circle
          v-for="(point, i) in points"
          :key="`point-${i}`"
          :cx="point.x"
          :cy="point.y"
          r="4"
          fill="white"
          stroke="#10B981"
          stroke-width="2"
          @mouseenter="hoveredIndex = i"
          @mouseleave="hoveredIndex = null"
          class="cursor-pointer transition-all"
        />
      </svg>

      <!-- Tooltip -->
      <div
        v-if="hoveredIndex !== null"
        class="absolute bg-slate-900 text-white text-xs px-2.5 py-1.5 rounded-lg shadow-lg whitespace-nowrap pointer-events-none"
        :style="{
          left: `${(points[hoveredIndex].x / svgWidth) * 100}%`,
          top: `${(points[hoveredIndex].y / svgHeight) * 100}%`,
          transform: 'translate(-50%, -120%)',
        }"
      >
        <p class="font-medium">{{ chartData[hoveredIndex].label }}</p>
        <p class="text-emerald-200">₹{{ chartData[hoveredIndex].value.toLocaleString('en-IN') }}</p>
      </div>
    </div>

    <!-- X-axis labels -->
    <div class="flex justify-between px-2 text-xs text-slate-400">
      <span v-for="(label, i) in chartData" :key="`label-${i}`">
        {{ i === 0 || i === chartData.length - 1 || i % Math.ceil(chartData.length / 5) === 0 ? label.label : '' }}
      </span>
    </div>
  </div>
</template>
