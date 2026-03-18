/**
 * Icon map for Lucide Vue icons
 * Maps friendly icon names to Lucide Vue icon components
 */
import {
  BarChart3,
  Receipt,
  Package,
  CreditCard,
  Beaker,
  Truck,
  Users,
  TrendingUp,
  Banknote,
  Clock,
  AlertTriangle,
  Settings,
  ShoppingCart,
  ArrowUpRight,
  DollarSign,
  FileText,
  Box,
  Hourglass,
  AlertCircle,
  Sparkles,
  ClockAlert,
  Bell,
  CheckCircle,
} from 'lucide-vue-next'

export const ICON_MAP = {
  // Main Navigation
  'chart-bar': BarChart3,
  'receipt-percent': Receipt,
  'archive-box': Package,
  'credit-card': CreditCard,
  'beaker': Beaker,
  'truck': Truck,
  'users': Users,
  'chart-line': TrendingUp,
  'banknotes': Banknote,
  'clock': Clock,
  'exclamation-triangle': AlertTriangle,
  'cog-6-tooth': Settings,

  // Dashboard Widgets
  'shopping-cart': ShoppingCart,
  'arrow-trending-up': ArrowUpRight,
  'currency-rupee': DollarSign,
  'document-text': FileText,
  'cube-transparent': Box,
  'hourglass': Hourglass,

  // AI Insights
  'exclamation-circle': AlertCircle,
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
