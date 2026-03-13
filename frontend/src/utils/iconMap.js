/**
 * Icon map for Lucide Vue icons
 * Maps friendly icon names to Lucide Vue icon components
 */
import {
  ChartBar,
  ReceiptPercent,
  ArchiveBox,
  CreditCard,
  Beaker,
  Truck,
  Users,
  ChartLine,
  Banknotes,
  Clock,
  ExclamationTriangle,
  Cog6Tooth,
  ShoppingCart,
  ArrowTrendingUp,
  CurrencyRupee,
  DocumentText,
  CubeTransparent,
  Hourglass,
  ExclamationCircle,
  Sparkles,
  ClockAlert,
  Bell,
  CheckCircle,
} from 'lucide-vue-next'

export const ICON_MAP = {
  // Main Navigation
  'chart-bar': ChartBar,
  'receipt-percent': ReceiptPercent,
  'archive-box': ArchiveBox,
  'credit-card': CreditCard,
  'beaker': Beaker,
  'truck': Truck,
  'users': Users,
  'chart-line': ChartLine,
  'banknotes': Banknotes,
  'clock': Clock,
  'exclamation-triangle': ExclamationTriangle,
  'cog-6-tooth': Cog6Tooth,

  // Dashboard Widgets
  'shopping-cart': ShoppingCart,
  'arrow-trending-up': ArrowTrendingUp,
  'currency-rupee': CurrencyRupee,
  'document-text': DocumentText,
  'cube-transparent': CubeTransparent,
  'hourglass': Hourglass,

  // AI Insights
  'exclamation-circle': ExclamationCircle,
  'sparkles': Sparkles,
  'clock-alert': ClockAlert,

  // Notifications
  'bell': Bell,
  'check-circle': CheckCircle,
}

/**
 * Get icon component by name
 * @param {string} iconName - The name of the icon
 * @returns {Component | null} - The icon component or null if not found
 */
export const getIcon = (iconName) => {
  return ICON_MAP[iconName] || null
}
