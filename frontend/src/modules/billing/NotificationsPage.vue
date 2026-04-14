<script setup>
import { computed, onMounted, ref } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import { notificationService } from '../../services/apiService.js'

const filterType = ref('all')
const searchQuery = ref('')
const notifications = ref([])
const loading = ref(false)
const error = ref('')
const storageKey = 'sonik_notification_reads'
const readNotificationIds = ref(new Set())

function getIcon(type) {
  const icons = {
    stock: '📦',
    expiry: '⏰',
    credit: '💳',
  }
  return icons[type] || '🔔'
}

function syncReadState(items) {
  notifications.value = items.map((notification) => ({
    ...notification,
    icon: getIcon(notification.type),
    read: readNotificationIds.value.has(notification.id),
  }))
}

async function loadNotifications() {
  loading.value = true
  error.value = ''
  try {
    const items = await notificationService.getNotifications()
    syncReadState(items)
  } catch (err) {
    error.value = err.message || 'Failed to load notifications'
  } finally {
    loading.value = false
  }
}

const filteredNotifications = computed(() => {
  let filtered = notifications.value

  if (filterType.value !== 'all') {
    filtered = filtered.filter((notification) => notification.category === filterType.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter((notification) =>
      notification.title.toLowerCase().includes(query) ||
      notification.message.toLowerCase().includes(query)
    )
  }

  return filtered
})

const unreadCount = computed(() => notifications.value.filter((notification) => !notification.read).length)

function markAsRead(id) {
  const notification = notifications.value.find((item) => item.id === id)
  if (!notification) return

  notification.read = true
  readNotificationIds.value.add(id)
  localStorage.setItem(storageKey, JSON.stringify([...readNotificationIds.value]))
}

function markAllAsRead() {
  notifications.value.forEach((notification) => {
    notification.read = true
    readNotificationIds.value.add(notification.id)
  })
  localStorage.setItem(storageKey, JSON.stringify([...readNotificationIds.value]))
}

function deleteNotification(id) {
  const index = notifications.value.findIndex((notification) => notification.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const urgencyColor = {
  high: 'text-red-600',
  medium: 'text-amber-600',
  low: 'text-slate-600',
}

const urgencyBg = {
  high: 'bg-red-100',
  medium: 'bg-amber-100',
  low: 'bg-slate-100',
}

onMounted(() => {
  const storedIds = JSON.parse(localStorage.getItem(storageKey) || '[]')
  readNotificationIds.value = new Set(storedIds)
  loadNotifications()
})
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Notifications</h1>
          <p class="text-sm text-slate-500 mt-1" v-if="unreadCount > 0">
            You have <span class="font-semibold">{{ unreadCount }}</span> unread notifications
          </p>
          <p class="text-sm text-slate-500 mt-1" v-else>
            All notifications read
          </p>
        </div>
        <button
          v-if="unreadCount > 0"
          class="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition-colors"
          @click="markAllAsRead"
        >
          Mark All as Read
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div class="lg:col-span-2">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search notifications..."
              class="w-full bg-white border border-slate-200 rounded-lg px-4 py-2 pl-9 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <select
          v-model="filterType"
          class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <option value="all">All Notifications</option>
          <option value="low-stock">Low Stock</option>
          <option value="expiry">Expiry Alerts</option>
          <option value="credit">Credit Issues</option>
        </select>

        <button class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm hover:bg-slate-50" @click="loadNotifications">
          Refresh
        </button>
      </div>

      <div class="space-y-3">
        <div v-if="loading" class="flex items-center justify-center py-12 text-slate-500">
          Loading notifications...
        </div>
        <div v-else-if="error" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {{ error }}
        </div>
        <div v-else-if="filteredNotifications.length === 0" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="text-4xl mb-2">🔔</div>
            <p class="text-slate-500 font-medium">No notifications found</p>
            <p class="text-slate-400 text-sm mt-1">You're all caught up!</p>
          </div>
        </div>

        <div
          v-for="notification in filteredNotifications"
          :key="notification.id"
          :class="[
            'group p-4 rounded-lg border-l-4 transition-all hover:shadow-md cursor-pointer',
            notification.read ? 'bg-slate-50 border-l-slate-300' : 'bg-blue-50 border-l-blue-500 shadow-sm'
          ]"
          @click="markAsRead(notification.id)"
        >
          <div class="flex items-start gap-4">
            <div :class="['text-2xl flex-shrink-0', urgencyBg[notification.urgency], 'p-2 rounded-lg']">
              {{ notification.icon }}
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <h3 class="font-semibold text-slate-900">{{ notification.title }}</h3>
                  <p class="text-sm text-slate-600 mt-1">{{ notification.message }}</p>
                  <p class="text-xs text-slate-400 mt-2">{{ notification.time }}</p>
                </div>

                <div class="flex items-center gap-2 flex-shrink-0">
                  <span v-if="!notification.read" class="w-2 h-2 rounded-full bg-blue-600 flex-shrink-0"></span>
                  <span :class="['text-xs font-semibold px-2 py-1 rounded', urgencyBg[notification.urgency], urgencyColor[notification.urgency]]">
                    {{ notification.urgency }}
                  </span>
                </div>
              </div>
            </div>

            <button
              class="flex-shrink-0 p-2 text-slate-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all"
              @click.stop="deleteNotification(notification.id)"
            >
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<style scoped>
</style>
