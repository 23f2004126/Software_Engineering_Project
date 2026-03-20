<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/authStore.js'
import { MENU_ITEMS } from '../../constants/menuItems.js'
import { getIcon } from '../../utils/iconMap.js'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Filter menu items based on role
const filteredMenuItems = computed(() => {
  if (authStore.isEmployee) {
    // Employees see only: Dashboard, Billing, Inventory, Milk Daily Entry, Shift Report
    return MENU_ITEMS.filter(item => {
      const employeeAllowed = ['Dashboard', 'Billing', 'Inventory', 'Milk Daily Entry', 'Shift Report']
      return employeeAllowed.includes(item.label)
    })
  }
  // Owners see all items
  return MENU_ITEMS
})

// Group menu items by section
const groupedMenuItems = computed(() => {
  const groups = {}
  filteredMenuItems.value.forEach((item) => {
    if (!groups[item.section]) {
      groups[item.section] = []
    }
    groups[item.section].push(item)
  })
  return groups
})

// Determine which sections to display based on role
const visibleSections = computed(() => {
  if (authStore.isEmployee) {
    return ['MAIN', 'MANAGE', 'SHIFT']
  }
  return ['MAIN', 'MANAGE', 'REPORTS']
})

const isActive = (path) => {
  if (path === '/dashboard') {
    return route.path === '/dashboard'
  }
  return route.path.startsWith(path)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

// Get user initials for avatar
const userInitials = computed(() => {
  if (authStore.user?.name) {
    return authStore.user.name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
  }
  return 'UK'
})

// Get role display text
const roleDisplay = computed(() => {
  return authStore.isOwner ? 'Owner' : 'Employee'
})
</script>

<template>
  <aside class="w-64 h-screen bg-white border-r border-slate-200 flex flex-col flex-shrink-0">
    <!-- Logo -->
    <div class="px-6 py-5 border-b border-slate-100 flex items-center gap-2">
      <div class="w-8 h-8 bg-emerald-500 rounded-xl flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" />
        </svg>
      </div>
      <span class="text-xl font-bold text-slate-900">Sonik</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-6">
      <div v-for="section in visibleSections" :key="section">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3 py-2 mt-2">
          {{ section }}
        </p>
        <div class="space-y-1">
          <RouterLink
            v-for="item in groupedMenuItems[section]"
            v-if="groupedMenuItems[section]"
            :key="item.path"
            :to="item.path"
            class="relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors"
            :class="
              isActive(item.path)
                ? 'bg-emerald-50 text-emerald-600 font-semibold'
                : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
            "
          >
            <!-- Active indicator bar -->
            <div v-if="isActive(item.path)" class="absolute left-0 top-1 bottom-1 w-1 bg-emerald-500 rounded-r-full"></div>

            <!-- Icon from Lucide -->
            <component
              :is="getIcon(item.icon)"
              class="w-4 h-4 flex-shrink-0"
              :stroke-width="2"
            />

            <!-- Label -->
            <span class="truncate">{{ item.label }}</span>
          </RouterLink>
        </div>
      </div>
    </nav>

    <!-- User Card -->
    <div class="px-4 py-4 border-t border-slate-100">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0">
          {{ userInitials }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-900 truncate">{{ authStore.user?.name || 'User' }}</p>
          <span class="inline-block bg-emerald-100 text-emerald-700 text-xs px-1.5 py-0.5 rounded font-medium mt-0.5">
            {{ roleDisplay }}
          </span>
        </div>
      </div>
      <button
        class="w-full text-left text-xs text-slate-400 hover:text-red-500 flex items-center gap-1 mt-3 transition-colors"
        @click="logout"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Logout
      </button>
    </div>
  </aside>
</template>
