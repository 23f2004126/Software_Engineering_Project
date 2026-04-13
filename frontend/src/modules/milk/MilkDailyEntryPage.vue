<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import { milkSubscriberService } from '../../services/apiService.js'

const route = useRoute()

const currentDate = new Date()
const currentMonth = ref(currentDate.getMonth() + 1)
const currentYear = ref(currentDate.getFullYear())
const selectedDate = ref(null)
const selectedEntry = ref(null)
const editQuantity = ref(0)
const editTemperature = ref(4)
const editQuality = ref('A+')
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const subscriber = ref(null)
const entries = ref([])

const subscriberId = computed(() => Number(route.params.id))

const daysInMonth = (month, year) => new Date(year, month, 0).getDate()

const monthName = computed(() => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return months[currentMonth.value - 1]
})

const calendarDays = computed(() => {
  const days = []
  for (let i = 1; i <= daysInMonth(currentMonth.value, currentYear.value); i += 1) {
    days.push(i)
  }
  return days
})

const entriesByDay = computed(() => {
  const map = {}
  for (const entry of entries.value) {
    const day = Number(entry.entry_date?.split('-')[2] || 0)
    if (day) {
      map[day] = entry
    }
  }
  return map
})

const totalQuantity = computed(() => {
  return entries.value.reduce((sum, entry) => sum + Number(entry.quantity || 0), 0)
})

const averageQuantity = computed(() => {
  return entries.value.length ? Number((totalQuantity.value / entries.value.length).toFixed(2)) : 0
})

const weeklyData = computed(() => {
  const weeks = [
    { week: 'Week 1', quantity: 0 },
    { week: 'Week 2', quantity: 0 },
    { week: 'Week 3', quantity: 0 },
    { week: 'Week 4', quantity: 0 },
    { week: 'Week 5', quantity: 0 },
  ]
  for (const entry of entries.value) {
    const day = Number(entry.entry_date?.split('-')[2] || 1)
    const weekIndex = Math.min(Math.floor((day - 1) / 7), weeks.length - 1)
    weeks[weekIndex].quantity += Number(entry.quantity || 0)
  }
  return weeks.filter((week) => week.quantity > 0)
})

const maxWeeklyQuantity = computed(() => {
  return weeklyData.value.length ? Math.max(...weeklyData.value.map((week) => week.quantity)) : 1
})

const formattedSelectedDate = computed(() => {
  if (!selectedDate.value) return ''
  return `${monthName.value} ${selectedDate.value}, ${currentYear.value}`
})

const resetEditor = () => {
  selectedEntry.value = null
  editQuantity.value = Number(subscriber.value?.quantity || 0.5)
  editTemperature.value = 4
  editQuality.value = 'A+'
}

const loadSubscriber = async () => {
  subscriber.value = await milkSubscriberService.getSubscriber(subscriberId.value)
}

const loadEntries = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    entries.value = await milkSubscriberService.getEntries(subscriberId.value, {
      month: currentMonth.value,
      year: currentYear.value,
    })
    if (selectedDate.value) {
      selectDate(selectedDate.value)
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load entries'
  } finally {
    loading.value = false
  }
}

const selectDate = (day) => {
  selectedDate.value = day
  const entry = entriesByDay.value[day]
  if (entry) {
    selectedEntry.value = entry
    editQuantity.value = Number(entry.quantity || 0)
    editTemperature.value = entry.temperature ?? 4
    editQuality.value = entry.quality || 'A+'
    return
  }
  resetEditor()
}

const selectedDateIso = computed(() => {
  if (!selectedDate.value) return null
  return `${currentYear.value}-${String(currentMonth.value).padStart(2, '0')}-${String(selectedDate.value).padStart(2, '0')}`
})

const saveEntry = async () => {
  if (!selectedDateIso.value) return
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const saved = await milkSubscriberService.saveEntry(subscriberId.value, {
      entry_date: selectedDateIso.value,
      quantity: editQuantity.value,
      temperature: editTemperature.value,
      quality: editQuality.value,
    })
    const existingIndex = entries.value.findIndex((entry) => entry.entry_id === saved.entry_id)
    if (existingIndex >= 0) {
      entries.value.splice(existingIndex, 1, saved)
    } else {
      entries.value.push(saved)
      entries.value.sort((a, b) => a.entry_date.localeCompare(b.entry_date))
    }
    selectedEntry.value = saved
    successMessage.value = 'Milk entry saved successfully'
  } catch (error) {
    errorMessage.value = error.message || 'Failed to save entry'
  } finally {
    saving.value = false
  }
}

const deleteEntry = async () => {
  if (!selectedEntry.value?.entry_id) return
  saving.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await milkSubscriberService.deleteEntry(subscriberId.value, selectedEntry.value.entry_id)
    entries.value = entries.value.filter((entry) => entry.entry_id !== selectedEntry.value.entry_id)
    resetEditor()
    successMessage.value = 'Milk entry deleted successfully'
  } catch (error) {
    errorMessage.value = error.message || 'Failed to delete entry'
  } finally {
    saving.value = false
  }
}

const goToPreviousMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value -= 1
  } else {
    currentMonth.value -= 1
  }
}

const goToNextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value += 1
  } else {
    currentMonth.value += 1
  }
}

watch([currentMonth, currentYear], loadEntries)

onMounted(async () => {
  await loadSubscriber()
  await loadEntries()
})
</script>

<template>
  <MainLayout>
    <div class="space-y-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Milk Daily Entry</h1>
        <p class="text-sm text-slate-500 mt-1">
          {{ subscriber?.name || 'Subscriber' }} <span v-if="subscriber?.phone">- {{ subscriber.phone }}</span>
        </p>
      </div>

      <div v-if="successMessage" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {{ errorMessage }}
      </div>
    </div>

    <div class="grid grid-cols-5 gap-6 mt-6">
      <div class="col-span-3">
        <Card padding="lg">
          <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
            <h3 class="font-semibold text-slate-900">{{ monthName }} {{ currentYear }}</h3>
            <div class="flex gap-2">
              <button class="px-3 py-1 rounded-lg hover:bg-slate-100 text-slate-600 font-semibold" @click="goToPreviousMonth">&larr;</button>
              <button class="px-3 py-1 rounded-lg hover:bg-slate-100 text-slate-600 font-semibold" @click="goToNextMonth">&rarr;</button>
            </div>
          </div>

          <div class="grid grid-cols-7 gap-2 mb-4">
            <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="text-center text-xs font-semibold text-slate-500 uppercase py-2">
              {{ day }}
            </div>
          </div>

          <div v-if="loading" class="py-10 text-center text-slate-500">Loading entries...</div>

          <div v-else class="grid grid-cols-7 gap-2">
            <button
              v-for="day in calendarDays"
              :key="day"
              class="aspect-square rounded-lg border-2 p-2 text-center transition-all hover:border-emerald-400"
              :class="{
                'border-emerald-500 bg-emerald-50': selectedDate === day,
                'border-slate-200 hover:border-slate-300': selectedDate !== day && entriesByDay[day],
                'border-slate-100 bg-slate-50 hover:border-slate-200': !entriesByDay[day],
              }"
              @click="selectDate(day)"
            >
              <p class="text-xs font-semibold text-slate-900">{{ day }}</p>
              <p v-if="entriesByDay[day]" class="text-xs text-emerald-600 font-semibold mt-1">
                {{ entriesByDay[day].quantity }}L
              </p>
              <p v-else class="text-xs text-slate-400 mt-1">-</p>
            </button>
          </div>
        </Card>

        <Card class="mt-6">
          <p class="font-semibold text-slate-900 mb-4">Weekly Summary</p>
          <div v-if="weeklyData.length === 0" class="text-sm text-slate-500">No entries recorded for this month.</div>
          <div v-else class="space-y-4">
            <div v-for="week in weeklyData" :key="week.week">
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

      <div class="col-span-2 space-y-6">
        <Card class="bg-emerald-50 border-emerald-100">
          <p class="text-xs font-semibold text-emerald-400 uppercase mb-3">{{ monthName }} Summary</p>
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
              <span class="font-mono font-bold text-emerald-700">{{ entries.length }}</span>
            </div>
          </div>
        </Card>

        <Card v-if="selectedDate" padding="lg">
          <p class="font-semibold text-slate-900 mb-4">{{ formattedSelectedDate }}</p>

          <div class="space-y-4">
            <div>
              <p class="text-xs font-semibold text-slate-400 uppercase mb-2">Quantity</p>
              <p class="text-3xl font-bold text-emerald-600">{{ editQuantity }}L</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-slate-600 mb-1">Temperature</label>
                <input
                  v-model.number="editTemperature"
                  type="number"
                  step="0.1"
                  class="w-full border border-slate-200 rounded-lg px-3 py-2 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-400"
                />
              </div>
              <div>
                <label class="block text-xs text-slate-600 mb-1">Quality</label>
                <select
                  v-model="editQuality"
                  class="w-full border border-slate-200 rounded-lg px-3 py-2 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-400"
                >
                  <option value="A+">A+</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                </select>
              </div>
            </div>

            <div class="pt-4 border-t border-slate-200">
              <p class="text-sm font-medium text-slate-700 mb-3">Edit Quantity</p>
              <div class="flex gap-2 mb-4">
                <button
                  class="w-10 h-10 rounded-lg border border-slate-200 hover:bg-slate-50"
                  @click="editQuantity = Math.max(0, Number((editQuantity - 0.5).toFixed(2)))"
                >
                  -
                </button>
                <input
                  v-model.number="editQuantity"
                  type="number"
                  min="0"
                  step="0.1"
                  class="flex-1 border border-slate-200 rounded-lg px-3 py-2 text-center font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-400"
                />
                <button
                  class="w-10 h-10 rounded-lg border border-slate-200 hover:bg-slate-50"
                  @click="editQuantity = Number((editQuantity + 0.5).toFixed(2))"
                >
                  +
                </button>
              </div>
              <Button variant="primary" fullWidth class="mb-2" :disabled="saving" @click="saveEntry">
                {{ saving ? 'Saving...' : (selectedEntry ? 'Save Changes' : 'Add Entry') }}
              </Button>
              <Button v-if="selectedEntry" variant="danger" fullWidth :disabled="saving" @click="deleteEntry">
                Delete Entry
              </Button>
            </div>
          </div>
        </Card>

        <Card v-else class="bg-slate-50 border-slate-200">
          <p class="text-sm text-slate-500">Select a date to add or edit milk delivery entries.</p>
        </Card>
      </div>
    </div>
  </MainLayout>
</template>
