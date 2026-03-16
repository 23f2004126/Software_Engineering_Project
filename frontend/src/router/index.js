import { createRouter, createWebHistory } from 'vue-router'

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
      meta: { requiresAuth: true },
    },
    {
      path: '/sales/:id',
      name: 'SaleDetails',
      component: () => import('../modules/billing/SaleDetailsPage.vue'),
      meta: { requiresAuth: true },
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
      meta: { requiresAuth: true },
    },
    {
      path: '/inventory/:id',
      name: 'EditProduct',
      component: () => import('../modules/inventory/AddEditProductPage.vue'),
      meta: { requiresAuth: true },
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
      meta: { requiresAuth: true },
    },
    {
      path: '/credit',
      name: 'CreditManagement',
      component: () => import('../modules/credit/CreditManagementPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/credit/:id',
      name: 'CustomerProfile',
      component: () => import('../modules/credit/CustomerProfilePage.vue'),
      meta: { requiresAuth: true },
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
      meta: { requiresAuth: true },
    },
    {
      path: '/purchase-orders',
      name: 'PurchaseOrders',
      component: () => import('../modules/suppliers/PurchaseOrderPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/employees',
      name: 'Employees',
      component: () => import('../modules/employees/EmployeesPage.vue'),
      meta: { requiresAuth: true },
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
  ],
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('sonik_auth') === 'true'

  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if not authenticated
    next('/login')
  } else if ((to.path === '/login' || to.path === '/shift-login') && isAuthenticated) {
    // Redirect to dashboard if already logged in and visiting login
    next('/dashboard')
  } else {
    next()
  }
})

export default router
