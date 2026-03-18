<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import { formatCurrency } from '../../utils/currency.js'

const currentMonth = ref(6) // June
const currentYear = ref(2025)
const selectedDate = ref(null)
const editingEntry = ref(null)
const showEditPopover = ref(false)
const editQuantity = ref(0)

// Mock daily entries
const mockEntries = {
  1: { quantity: 520, temperature: 4, quality: 'A+' },
  2: { quantity: 525, temperature: 4, quality: 'A+' },
  3: { quantity: 515, temperature: 5, quality: 'A' },
  5: { quantity: 530, temperature: 4, quality: 'A+' },
  6: { quantity: 510, temperature: 6, quality: 'A' },
  7: { quantity: 535, temperature: 3, quality: 'A+' },
  8: { quantity: 520, temperature: 4, quality: 'A+' },
  9: { quantity: 545, temperature: 4, quality: 'A+' },
  10: { quantity: 540, temperature: 5, quality: 'A' },
  12: { quantity: 525, temperature: 4, quality: 'A+' },
  13: { quantity: 515, temperature: 4, quality: 'A+' },
  14: { quantity: 550, temperature: 3, quality: 'A+' },
  15: { quantity: 520, temperature: 4, quality: 'A+' },
  16: { quantity: 508, temperature: 5, quality: 'A' },
  17: { quantity: 535, temperature: 4, quality: 'A+' },
  18: { quantity: 542, temperature: 4, quality: 'A+' },
  19: { quantity: 520, temperature: 4, quality: 'A+' },
  20: { quantity: 530, temperature: 3, quality: 'A+' },
  21: { quantity: 518, temperature: 5, quality: 'A' },
  22: { quantity: 545, temperature: 4, quality: 'A+' },
  23: { quantity: 555, temperature: 4, quality: 'A+' },
  24: { quantity: 528, temperature: 4, quality: 'A+' },
  25: { quantity: 540, temperature: 4, quality: 'A+' },
}

const daysInMonth = (month, year) => {
  return new Date(year, month, 0).getDate()
}

const monthName = () => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return months[currentMonth.value - 1]
}

const calendarDays = computed(() => {
  const days = []
  for (let i = 1; i <= daysInMonth(currentMonth.value, currentYear.value); i++) {
    days.push(i)
  }
  return days
})

const totalQuantity = computed(() => {
  return Object.values(mockEntries).reduce((sum, entry) => sum + entry.quantity, 0)
})

const averageQuantity = computed(() => {
  const entries = Object.values(mockEntries)
  return entries.length > 0 ? Math.round(totalQuantity.value / entries.length) : 0
})

const weeklyData = [
  { week: 'Week 1', quantity: 3675 },
  { week: 'Week 2', quantity: 3700 },
  { week: 'Week 3', quantity: 3650 },
  { week: 'Week 4', quantity: 2140 },
]

const maxWeeklyQuantity = Math.max(...weeklyData.map((w) => w.quantity))

const selectDate = (day) => {
  selectedDate.value = day
  if (mockEntries[day]) {
    editingEntry.value = { ...mockEntries[day] }
    editQuantity.value = mockEntries[day].quantity
  } else {
    editingEntry.value = null
  }
}

const handleEdit = () => {
  if (selectedDate.value && editQuantity.value > 0) {
    mockEntries[selectedDate.value] = {
      ...mockEntries[selectedDate.value],
      quantity: editQuantity.value,
    }
    showEditPopover.value = false
  }
}

const handleDelete = () => {
  if (selectedDate.value) {
    delete mockEntries[selectedDate.value]
    selectedDate.value = null
    showEditPopover.value = false
  }
}
</script>

<template>
  <MainLayout>
    <div class="grid grid-cols-5 gap-6">
      <!-- LEFT: Calendar -->
      <div class="col-span-3">
        <Card padding="lg">
          <!-- Month Navigation -->
          <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
            <h3 class="font-semibold text-slate-900">{{ monthName() }} {{ currentYear }}</h3>
            <div class="flex gap-2">
              <button class="px-3 py-1 rounded-lg hover:bg-slate-100 text-slate-600 font-semibold">←</button>
              <button class="px-3 py-1 rounded-lg hover:bg-slate-100 text-slate-600 font-semibold">→</button>
            </div>
          </div>

          <!-- Day Headers -->
          <div class="grid grid-cols-7 gap-2 mb-4">
            <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="text-center text-xs font-semibold text-slate-500 uppercase py-2">
              {{ day }}
            </div>
          </div>

          <!-- Calendar Grid -->
          <div class="grid grid-cols-7 gap-2">
            <button
              v-for="day in calendarDays"
              :key="day"
              class="aspect-square rounded-lg border-2 p-2 text-center transition-all hover:border-emerald-400"
              :class="{
                'border-emerald-500 bg-emerald-50': selectedDate === day,
                'border-slate-200 hover:border-slate-300': selectedDate !== day && mockEntries[day],
                'border-slate-100 bg-slate-50 hover:border-slate-200': !mockEntries[day],
              }"
              @click="selectDate(day)"
            >
              <p class="text-xs font-semibold text-slate-900">{{ day }}</p>
              <p v-if="mockEntries[day]" class="text-xs text-emerald-600 font-semibold mt-1">
                {{ mockEntries[day].quantity }}L
              </p>
              <p v-else class="text-xs text-slate-400 mt-1">—</p>
            </button>
          </div>
        </Card>

        <!-- Weekly Summary -->
        <Card class="mt-6">
          <p class="font-semibold text-slate-900 mb-4">Weekly Summary</p>
          <div class="space-y-4">
            <div v-for="(week, idx) in weeklyData" :key="idx">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-slate-600">{{ week.week }}</span>
                <span class="font-semibold text-slate-900">{{ week.quantity }}L</span>
              </div>
              <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-emerald-500 transition-all"
                  :style="{ width: `${(week.quantity / maxWeeklyQuantity) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- RIGHT: Entry Details & AI Insight -->
      <div class="col-span-2 space-y-6">
        <!-- Summary Stats -->
        <Card class="bg-emerald-50 border-emerald-100">
          <p class="text-xs font-semibold text-emerald-400 uppercase mb-3">June Summary</p>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Total Quantity:</span>
              <span class="font-mono font-bold text-emerald-700">{{ totalQuantity }}L</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Daily Average:</span>
              <span class="font-mono font-bold text-emerald-700">{{ averageQuantity }}L</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-600">Days Recorded:</span>
              <span class="font-mono font-bold text-emerald-700">{{ Object.keys(mockEntries).length }}</span>
            </div>
          </div>
        </Card>

        <!-- Entry Editor -->
        <Card v-if="selectedDate" padding="lg">
          <p class="font-semibold text-slate-900 mb-4">{{ monthName() }} {{ selectedDate }}, {{ currentYear }}</p>

          <div v-if="editingEntry" class="space-y-4">
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Current Quantity</p>
              <p class="text-3xl font-bold text-emerald-600">{{ editingEntry.quantity }}L</p>
            </div>
            <div class="flex gap-4">
              <div class="flex-1">
                <p class="text-xs text-slate-600 mb-1">Temperature</p>
                <p class="font-semibold text-slate-900">{{ editingEntry.temperature }}°C</p>
              </div>
              <div class="flex-1">
                <p class="text-xs text-slate-600 mb-1">Quality</p>
                <p class="font-semibold text-slate-900">{{ editingEntry.quality }}</p>
              </div>
            </div>

            <div class="pt-4 border-t border-slate-200">
              <p class="text-sm font-medium text-slate-700 mb-3">Edit Quantity</p>
              <div class="flex gap-2 mb-4">
                <button
                  class="w-10 h-10 rounded-lg border border-slate-200 hover:bg-slate-50"
                  @click="editQuantity = Math.max(0, editQuantity - 5)"
                >
                  −
                </button>
                <input
                  v-model.number="editQuantity"
                  type="number"
                  class="flex-1 border border-slate-200 rounded-lg px-3 py-2 text-center font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-400"
                />
                <button
                  class="w-10 h-10 rounded-lg border border-slate-200 hover:bg-slate-50"
                  @click="editQuantity += 5"
                >
                  +
                </button>
              </div>
              <Button variant="primary" fullWidth class="mb-2" @click="handleEdit">
                Save Changes
              </Button>
              <Button variant="danger" fullWidth @click="handleDelete">
                Delete Entry
              </Button>
            </div>
          </div>

          <div v-else class="text-center py-4">
            <p class="text-slate-500 text-sm mb-3">No entry recorded for this date</p>
            <Button variant="secondary" fullWidth @click="showEditPopover = true">
              + Add Entry
            </Button>
          </div>
        </Card>

        <!-- AI Insight -->
        <Card class="bg-emerald-50 border-emerald-100">
          <div class="flex gap-3">
            <span class="text-2xl">💡</span>
            <div>
              <p class="font-semibold text-emerald-900 text-sm">Supply Trending Up</p>
              <p class="text-xs text-emerald-700 mt-1">
                Daily supply increased by 5% this week. Consider adjusting customer quotas or finding additional suppliers.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
