/**
 * Date formatting utility functions for Sonik retail management system.
 * Uses Indian date formats and IST timezone.
 */

/**
 * Format a date according to the specified format.
 * @param {Date|string} date - The date to format (Date object or ISO string)
 * @param {string} format - Format type: 'display', 'short', 'full', 'time', 'datetime'
 * @returns {string} Formatted date string
 *   - 'display':  "07 Jun 2025"
 *   - 'short':    "7/6/25"
 *   - 'full':     "Saturday, 7 June 2025"
 *   - 'time':     "10:45 AM"
 *   - 'datetime': "07 Jun 2025, 10:45 AM"
 */
export function formatDate(date, format = 'display') {
  const d = typeof date === 'string' ? new Date(date) : date

  const options = {
    display: { day: '2-digit', month: 'short', year: 'numeric' },
    short: { day: 'numeric', month: 'numeric', year: '2-digit' },
    full: { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' },
    time: { hour: '2-digit', minute: '2-digit', hour12: true },
    datetime: {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    },
  }

  return new Intl.DateTimeFormat('en-IN', options[format] || options.display).format(d)
}

/**
 * Format a date as human-friendly relative time.
 * @param {Date|string} date - The date to format
 * @returns {string} Relative time (e.g., "2 hours ago", "Yesterday", "Just now")
 */
export function formatRelative(date) {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) {
    return 'Just now'
  } else if (diffMinutes < 60) {
    return `${diffMinutes} min${diffMinutes > 1 ? 's' : ''} ago`
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  } else if (diffDays === 1) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays} days ago`
  }

  return formatDate(d, 'display')
}

/**
 * Format seconds to "Xh Ym Zs" duration format.
 * @param {number} seconds - The duration in seconds
 * @returns {string} Duration string (e.g., "2h 15m 0s")
 */
export function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  return `${hours}h ${minutes}m ${secs}s`
}

/**
 * Format seconds to "Xh Ym" duration format (without seconds).
 * @param {number} seconds - The duration in seconds
 * @returns {string} Duration string (e.g., "2h 15m")
 */
export function formatDurationHM(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  return `${hours}h ${minutes}m`
}

/**
 * Get the current month name and year.
 * @returns {string} Month and year (e.g., "June 2025")
 */
export function getCurrentMonthName() {
  const now = new Date()
  return new Intl.DateTimeFormat('en-IN', { month: 'long', year: 'numeric' }).format(now)
}

/**
 * Get the number of days in a given month.
 * @param {number} year - The year
 * @param {number} month - The month (1-indexed, 1-12)
 * @returns {number} Number of days in the month
 */
export function getDaysInMonth(year, month) {
  return new Date(year, month, 0).getDate()
}

/**
 * Check if a date is expiring within the specified threshold.
 * @param {string} dateStr - The date string to check
 * @param {number} daysThreshold - Days threshold (default: 7)
 * @returns {boolean} True if date is within threshold days from today
 */
export function isExpiringSoon(dateStr, daysThreshold = 7) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = date.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  return diffDays > 0 && diffDays <= daysThreshold
}

/**
 * Check if a date has expired.
 * @param {string} dateStr - The date string to check
 * @returns {boolean} True if date is in the past
 */
export function isExpired(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()

  return date.getTime() < now.getTime()
}
