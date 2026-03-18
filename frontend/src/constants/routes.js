/**
 * Routes constants for the Sonik retail management system.
 * Use these constants for programmatic navigation to avoid hardcoding paths.
 */

export const ROUTES = {
  LOGIN: '/login',
  SHIFT_LOGIN: '/shift-login',
  DASHBOARD: '/dashboard',
  BILLING: '/billing',
  SALES_HISTORY: '/sales',
  SALE_DETAILS: (id) => `/sales/${id}`,
  INVENTORY: '/inventory',
  ADD_PRODUCT: '/inventory/add',
  EDIT_PRODUCT: (id) => `/inventory/${id}`,
  DAMAGE_LOSS: '/damage-loss',
  FINANCE: '/finance',
  CREDIT: '/credit',
  CUSTOMER_PROFILE: (id) => `/credit/${id}`,
  MILK: '/milk',
  MILK_ENTRY: (id) => `/milk/${id}`,
  SUPPLIERS: '/suppliers',
  PURCHASE_ORDERS: '/purchase-orders',
  EMPLOYEES: '/employees',
  SHIFT_REPORT: '/shift-report',
}
