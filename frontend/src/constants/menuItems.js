/**
 * Sidebar navigation menu configuration for the Sonik retail management system.
 * Each item has: label, path, icon (Heroicons name), and section for grouping.
 */

export const MENU_ITEMS = [
  // MAIN section
  {
    label: 'Dashboard',
    path: '/dashboard',
    icon: 'chart-bar',
    section: 'MAIN',
  },

  // MANAGE section
  {
    label: 'Billing',
    path: '/billing',
    icon: 'receipt-percent',
    section: 'MANAGE',
  },
  {
    label: 'Inventory',
    path: '/inventory',
    icon: 'archive-box',
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
    icon: 'chart-line',
    section: 'REPORTS',
  },
  {
    label: 'Finance',
    path: '/finance',
    icon: 'banknotes',
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
    icon: 'exclamation-triangle',
    section: 'REPORTS',
  },

  // SETTINGS section
  {
    label: 'Settings',
    path: '/settings',
    icon: 'cog-6-tooth',
    section: 'SETTINGS',
  },
]
