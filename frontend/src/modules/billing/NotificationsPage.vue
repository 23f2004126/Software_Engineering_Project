<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'

const filterType = ref('all')
const searchQuery = ref('')

const notifications = ref([
  {
    id: 1,
    type: 'low-stock',
    title: 'Low Stock Alert',
    message: 'Rice (20KG) has fallen below threshold',
    time: '2 minutes ago',
    icon: '📦',
    urgency: 'medium',
    read: false,
  },
  {
    id: 2,
    type: 'expiry',
    title: 'Product Expiry Warning',
    message: 'Milk (1L) expires in 2 days',
    time: '15 minutes ago',
    icon: '⏰',
    urgency: 'high',
    read: false,
  },
  {
    id: 3,
    type: 'credit',
    title: 'Overdue Credit',
    message: 'Customer "Prakash Mart" credit overdue by 5 days',
    time: '1 hour ago',
    icon: '💳',
    urgency: 'high',
    read: false,
  },
  {
    id: 4,
    type: 'sales',
    title: 'Unusual Sales Fluctuation',
    message: 'Sales dropped 35% compared to last week',
    time: '3 hours ago',
    icon: '📉',
    urgency: 'medium',
    read: true,
  },
  {
    id: 5,
    type: 'low-stock',
    title: 'Low Stock Alert',
    message: 'Bread (1units) below threshold - reorder recommended',
    time: '5 hours ago',
    icon: '📦',
    urgency: 'low',
    read: true,
  },
  {
    id: 6,
    type: 'credit',
    title: 'Credit Limit Warning',
    message: 'Customer "Super Market" approaching credit limit (92%)',
    time: '1 day ago',
    icon: '⚠️',
    urgency: 'medium',
    read: true,
  },
])

const filteredNotifications = computed(() => {
  let filtered = notifications.value

  if (filterType.value !== 'all') {
    filtered = filtered.filter(n => n.type === filterType.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(n => 
      n.title.toLowerCase().includes(query) || 
      n.message.toLowerCase().includes(query)
    )
  }

  return filtered
})

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const markAsRead = (id) => {
  const notif = notifications.value.find(n => n.id === id)
  if (notif) notif.read = true
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}

const deleteNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
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
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header with Actions -->
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
          @click="markAllAsRead"
          class="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-semibold hover:bg-emerald-700 transition-colors"
        >
          Mark All as Read
        </button>
      </div>

      <!-- Filters -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <!-- Search -->
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

        <!-- Filter Dropdown -->
        <select
          v-model="filterType"
          class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <option value="all">All Notifications</option>
          <option value="low-stock">Low Stock</option>
          <option value="expiry">Expiry Alerts</option>
          <option value="credit">Credit Issues</option>
          <option value="sales">Sales Alerts</option>
        </select>

        <!-- Read Status Filter -->
        <select class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500">
          <option>All Status</option>
          <option>Unread Only</option>
          <option>Read Only</option>
        </select>
      </div>

      <!-- Notifications List -->
      <div class="space-y-3">
        <div 
          v-if="filteredNotifications.length === 0" 
          class="flex items-center justify-center py-12"
        >
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
            notification.read 
              ? 'bg-slate-50 border-l-slate-300' 
              : 'bg-blue-50 border-l-blue-500 shadow-sm'
          ]"
          @click="markAsRead(notification.id)"
        >
          <div class="flex items-start gap-4">
            <!-- Icon -->
            <div :class="['text-2xl flex-shrink-0', urgencyBg[notification.urgency], 'p-2 rounded-lg']">
              {{ notification.icon }}
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1">
                  <h3 class="font-semibold text-slate-900">{{ notification.title }}</h3>
                  <p class="text-sm text-slate-600 mt-1">{{ notification.message }}</p>
                  <p class="text-xs text-slate-400 mt-2">{{ notification.time }}</p>
                </div>

                <!-- Unread Badge -->
                <div class="flex items-center gap-2 flex-shrink-0">
                  <span 
                    v-if="!notification.read"
                    class="w-2 h-2 rounded-full bg-blue-600 flex-shrink-0"
                  ></span>
                  <span :class="['text-xs font-semibold px-2 py-1 rounded', urgencyBg[notification.urgency], urgencyColor[notification.urgency]]">
                    {{ notification.urgency }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Delete Button -->
            <button
              @click.stop="deleteNotification(notification.id)"
              class="flex-shrink-0 p-2 text-slate-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-all"
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
