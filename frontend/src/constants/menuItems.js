/**
 * Sidebar navigation menu configuration for the Sonik retail management system.
 * Each item has: label, path, icon (Heroicons name), and section for grouping.
 */

export const MENU_ITEMS = [
  // MAIN section
  {
    label: 'Dashboard',
    path: '/dashboard',
    icon: 'home',
    section: 'MAIN',
  },

  // MANAGE section
  {
    label: 'Billing',
    path: '/billing',
    icon: 'receipt',
    section: 'MANAGE',
  },
  {
    label: 'Inventory',
    path: '/inventory',
    icon: 'cube',
    section: 'MANAGE',
  },
  {
    label: 'Credit',
    path: '/credit',
    icon: 'credit-card',
    section: 'MANAGE',
  },
  {
    label: 'Milk',
    path: '/milk',
    icon: 'beaker',
    section: 'MANAGE',
  },
  {
    label: 'Suppliers',
    path: '/suppliers',
    icon: 'truck',
    section: 'MANAGE',
  },
  {
    label: 'Employees',
    path: '/employees',
    icon: 'users',
    section: 'MANAGE',
  },

  // REPORTS section
  {
    label: 'Sales History',
    path: '/sales',
    icon: 'chart-bar',
    section: 'REPORTS',
  },
  {
    label: 'Finance',
    path: '/finance',
    icon: 'currency-rupee',
    section: 'REPORTS',
  },
  {
    label: 'Shift Reports',
    path: '/shift-report',
    icon: 'clock',
    section: 'REPORTS',
  },
  {
    label: 'Damage & Loss',
    path: '/damage-loss',
    icon: 'trash',
    section: 'REPORTS',
  },

  // SETTINGS section
  {
    label: 'Settings',
    path: '/settings',
    icon: 'cog',
    section: 'SETTINGS',
  },
]
