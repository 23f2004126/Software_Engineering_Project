import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // AUTH ROUTES
    {
      path: '/login',
      name: 'Login',
      component: () => import('../modules/auth/LoginPage.vue'),
    },
    {
      path: '/shift-login',
      name: 'ShiftLogin',
      component: () => import('../modules/shift/ShiftLoginPage.vue'),
    },

    // MAIN APP ROUTES
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../modules/dashboard/DashboardPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/billing',
      name: 'Billing',
      component: () => import('../modules/billing/BillingPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/sales',
      name: 'SalesHistory',
      component: () => import('../modules/billing/SalesHistoryPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/sales/:id',
      name: 'SaleDetails',
      component: () => import('../modules/billing/SaleDetailsPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/inventory',
      name: 'Inventory',
      component: () => import('../modules/inventory/InventoryPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/inventory/add',
      name: 'AddProduct',
      component: () => import('../modules/inventory/AddEditProductPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/inventory/:id',
      name: 'EditProduct',
      component: () => import('../modules/inventory/AddEditProductPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/damage-loss',
      name: 'DamageLoss',
      component: () => import('../modules/inventory/DamageLossPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/finance',
      name: 'Finance',
      component: () => import('../modules/finance/FinancePage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/credit',
      name: 'CreditManagement',
      component: () => import('../modules/credit/CreditManagementPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/credit/:id',
      name: 'CustomerProfile',
      component: () => import('../modules/credit/CustomerProfilePage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/milk',
      name: 'MilkSubscribers',
      component: () => import('../modules/milk/MilkSubscribersPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/milk/:id',
      name: 'MilkDailyEntry',
      component: () => import('../modules/milk/MilkDailyEntryPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/suppliers',
      name: 'Suppliers',
      component: () => import('../modules/suppliers/SuppliersPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/purchase-orders',
      name: 'PurchaseOrders',
      component: () => import('../modules/suppliers/PurchaseOrderPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/employees',
      name: 'Employees',
      component: () => import('../modules/employees/EmployeesPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/shift-report',
      name: 'ShiftReport',
      component: () => import('../modules/shift/ShiftReportPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/shift-reports',
      redirect: '/shift-report',
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../modules/auth/RegistrationPage.vue'),
    },
    {
      path: '/notifications',
      name: 'Notifications',
      component: () => import('../modules/billing/NotificationsPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/customers',
      name: 'CustomerList',
      component: () => import('../modules/credit/CustomerListPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('../modules/reports/ReportsPage.vue'),
      meta: { requiresAuth: true, ownerOnly: true },
    },
  ],
})

// Navigation guard to handle authentication and role-based access
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Restore session from localStorage on first load or page refresh
  if (!authStore.isAuthenticated) {
    authStore.restoreSession()
  }

  const isAuthenticated = authStore.isAuthenticated
  const isEmployee = authStore.isEmployee
  const isOwner = authStore.isOwner
  const shiftActive = authStore.shiftActive
  const today = new Date().toISOString().split('T')[0]
  const shiftDateStored = authStore.shiftDate

  // Rule 1: If route requires auth and user is not authenticated → redirect to /login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  // Rule 2: If user is employee and hasn't logged shift today → redirect to /shift-login (except on those pages)
  if (isEmployee && isAuthenticated && !shiftActive && to.path !== '/shift-login' && to.path !== '/login') {
    return next('/shift-login')
  }

  // Rule 3: If employee tries to access owner-only routes → redirect to dashboard
  if (isEmployee && to.meta.ownerOnly) {
    return next('/dashboard')
  }

  // Rule 4: If owner visits /shift-login → redirect to dashboard
  if (isOwner && to.path === '/shift-login') {
    return next('/dashboard')
  }

  // Rule 5: If already authenticated and visiting login → redirect to dashboard
  if ((to.path === '/login') && isAuthenticated) {
    return next('/dashboard')
  }

  next()
})

export default router

