/**
 * Currency utility functions for Sonik retail management system.
 * All formatting uses Indian Rupee (₹) with Indian number formatting system.
 */

/**
 * Format a number as Indian Rupee currency.
 * @param {number} value - The value to format
 * @param {Object} options - Formatting options
 * @param {boolean} options.showSymbol - Whether to show ₹ symbol (default: true)
 * @param {number} options.decimals - Number of decimal places (default: 0)
 * @returns {string} Formatted currency string (e.g., "₹1,54,325")
 */
export function formatCurrency(value, options = {}) {
  const { showSymbol = true, decimals = 0 } = options
  const formatted = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)

  if (!showSymbol) {
    return formatted.replace(/₹\s?/, '')
  }

  return formatted
}

/**
 * Format a number to compact form with Indian number system suffixes.
 * @param {number} value - The value to format
 * @returns {string} Compact formatted string (e.g., "₹1.54L", "₹12Cr")
 */
export function formatCompact(value) {
  if (value >= 10000000) {
    // >= 1 Crore
    return `₹${(value / 10000000).toFixed(2)}Cr`
  } else if (value >= 100000) {
    // >= 1 Lakh
    return `₹${(value / 100000).toFixed(2)}L`
  }

  return `₹${value}`
}

/**
 * Parse a formatted currency string back to a number.
 * @param {string} str - The formatted string (e.g., "₹1,54,325")
 * @returns {number} The parsed number
 */
export function parseCurrency(str) {
  return parseFloat(str.replace(/₹\s?/g, '').replace(/,/g, ''))
}

/**
 * Calculate profit margin percentage.
 * @param {number} cost - The cost price
 * @param {number} selling - The selling price
 * @returns {number} Margin percentage (e.g., 25 for 25%)
 */
export function calcMargin(cost, selling) {
  if (cost <= 0) return 0
  return ((selling - cost) / cost) * 100
}

/**
 * Get Tailwind text color class based on margin percentage.
 * @param {number} marginPercent - The margin percentage
 * @returns {string} Tailwind color class
 */
export function marginColor(marginPercent) {
  if (marginPercent >= 30) {
    return 'text-emerald-600'
  } else if (marginPercent >= 15) {
    return 'text-blue-600'
  }
  return 'text-amber-600'
}
