<script setup>
import { useRoute } from 'vue-router'
import { ref, computed } from 'vue'
import NotificationBell from './NotificationBell.vue'

const route = useRoute()
const searchQuery = ref('')
const showUserMenu = ref(false)

const titleMap = {
  Dashboard: 'Dashboard',
  Billing: 'Billing',
  SalesHistory: 'Sales History',
  SaleDetails: 'Sale Details',
  Inventory: 'Inventory',
  AddProduct: 'Add Product',
  EditProduct: 'Edit Product',
  DamageLoss: 'Damage & Loss',
  Finance: 'Finance',
  CreditManagement: 'Credit Management',
  CustomerProfile: 'Customer Profile',
  MilkSubscribers: 'Milk Subscribers',
  MilkDailyEntry: 'Milk Daily Entry',
  Suppliers: 'Suppliers',
  PurchaseOrders: 'Purchase Orders',
  Employees: 'Employees',
  ShiftReport: 'Shift Report',
  Settings: 'Settings',
}

const pageTitle = computed(() => {
  return titleMap[route.name] || 'Page'
})

const breadcrumb = computed(() => {
  const sections = {
    Dashboard: 'Dashboard',
    Billing: 'Manage',
    SalesHistory: 'Reports',
    SaleDetails: 'Reports',
    Inventory: 'Manage',
    AddProduct: 'Manage',
    EditProduct: 'Manage',
    DamageLoss: 'Reports',
    Finance: 'Reports',
    CreditManagement: 'Manage',
    CustomerProfile: 'Manage',
    MilkSubscribers: 'Manage',
    MilkDailyEntry: 'Manage',
    Suppliers: 'Manage',
    PurchaseOrders: 'Manage',
    Employees: 'Manage',
    ShiftReport: 'Reports',
    Settings: 'Settings',
  }
  return sections[route.name] || 'Page'
})
</script>

<template>
  <header class="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10">
    <!-- Left side -->
    <div>
      <h1 class="text-xl font-semibold text-slate-900">{{ pageTitle }}</h1>
      <p class="text-xs text-slate-400 mt-0.5">Sonik / {{ breadcrumb }}</p>
    </div>

    <!-- Right side -->
    <div class="flex items-center gap-4">
      <!-- Search bar -->
      <div class="relative w-72">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search anything..."
          class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 pl-9 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent transition-all"
        />
      </div>

      <!-- Notification bell -->
      <NotificationBell />

      <!-- User avatar -->
      <div class="relative">
        <button
          class="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white text-xs font-semibold hover:shadow-lg transition-shadow"
          @click="showUserMenu = !showUserMenu"
        >
          RK
        </button>
        <Transition name="fade">
          <div
            v-show="showUserMenu"
            class="absolute right-0 top-12 bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden min-w-48"
          >
            <button class="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 transition-colors">
              My Profile
            </button>
            <button class="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 border-t border-slate-100 transition-colors">
              Settings
            </button>
            <button class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 border-t border-slate-100 transition-colors"
              @click="
                () => {
                  localStorage.removeItem('sonik_auth')
                  $router.push('/login')
                }
              ">
              Logout
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
