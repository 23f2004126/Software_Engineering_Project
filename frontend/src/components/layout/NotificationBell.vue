<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { notificationService } from '../../services/apiService.js'

const router = useRouter()
const isOpen = ref(false)
const notifications = ref([])
const readNotificationIds = ref(new Set())
const storageKey = 'sonik_notification_reads'

const unreadCount = computed(() => notifications.value.filter((notification) => !notification.read).length)

function syncReadState(items) {
  notifications.value = items.map((notification) => ({
    ...notification,
    read: readNotificationIds.value.has(notification.id),
  }))
}

async function loadNotifications() {
  try {
    const items = await notificationService.getNotifications()
    syncReadState(items)
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
}

function markAllRead() {
  notifications.value.forEach((notification) => {
    readNotificationIds.value.add(notification.id)
  })
  localStorage.setItem(storageKey, JSON.stringify([...readNotificationIds.value]))
  syncReadState(notifications.value)
}

function getIconColor(type) {
  const colors = {
    stock: { bg: 'bg-red-100', text: 'text-red-600' },
    credit: { bg: 'bg-amber-100', text: 'text-amber-600' },
    expiry: { bg: 'bg-amber-100', text: 'text-amber-600' },
  }
  return colors[type] || colors.stock
}

function handleClickOutside(event) {
  const trigger = document.querySelector('[data-notification-trigger]')
  const dropdown = document.querySelector('[data-notification-dropdown]')
  if (trigger && !trigger.contains(event.target) && dropdown && !dropdown.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  const storedIds = JSON.parse(localStorage.getItem(storageKey) || '[]')
  readNotificationIds.value = new Set(storedIds)
  loadNotifications()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="relative">
    <button
      data-notification-trigger
      class="w-10 h-10 rounded-xl hover:bg-slate-100 flex items-center justify-center relative transition-colors"
      @click="isOpen = !isOpen"
    >
      <svg class="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <div v-if="unreadCount > 0" class="-top-0.5 -right-0.5 absolute w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-semibold">
        {{ unreadCount }}
      </div>
    </button>

    <Transition name="notification">
      <div
        v-show="isOpen"
        data-notification-dropdown
        class="absolute right-0 top-12 w-80 bg-white rounded-2xl shadow-xl border border-slate-200 z-50 overflow-hidden flex flex-col max-h-96"
      >
        <div class="px-4 py-3 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <h3 class="font-semibold text-slate-900">Notifications</h3>
          <button class="text-xs text-emerald-600 hover:text-emerald-700 font-medium" @click="markAllRead">
            Mark all read
          </button>
        </div>

        <div class="overflow-y-auto flex-1">
          <div v-if="notifications.length === 0" class="px-4 py-6 text-sm text-slate-500 text-center">
            No notifications right now
          </div>
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="flex items-start gap-3 px-4 py-3 border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors"
            :class="!notification.read ? 'bg-emerald-50/40' : ''"
          >
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              :class="getIconColor(notification.type).bg"
            >
              <svg class="w-4 h-4" :class="getIconColor(notification.type).text" fill="currentColor" viewBox="0 0 20 20">
                <circle cx="10" cy="10" r="8" />
              </svg>
            </div>

            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-slate-900">{{ notification.title }}</p>
              <p class="text-xs text-slate-500 mt-0.5 line-clamp-2">{{ notification.message }}</p>
              <p class="text-xs text-slate-400 mt-1">{{ notification.time }}</p>
            </div>

            <div v-if="!notification.read" class="w-2 h-2 bg-emerald-500 rounded-full flex-shrink-0 mt-2"></div>
          </div>
        </div>

        <div
          class="px-4 py-3 border-t border-slate-100 text-center hover:bg-slate-50 cursor-pointer transition-colors flex-shrink-0"
          @click="router.push('/notifications')"
        >
          <p class="text-sm text-emerald-600 font-medium">View all notifications</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.2s ease;
  transform-origin: top right;
}

.notification-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-8px);
}

.notification-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(-8px);
}
</style>
