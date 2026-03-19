import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const role = ref(null) // 'owner' or 'employee'
  const isAuthenticated = ref(false)
  const shiftActive = ref(false)
  const shiftDate = ref(null) // Today's date in format YYYY-MM-DD (for employee shift tracking)

  // Computed
  const isOwner = computed(() => role.value === 'owner')
  const isEmployee = computed(() => role.value === 'employee')

  // Actions
  const login = (userData, userRole) => {
    user.value = userData
    role.value = userRole // 'owner' or 'employee'
    isAuthenticated.value = true
    
    // Persist to localStorage
    localStorage.setItem('sonik_auth', JSON.stringify({
      user: userData,
      role: userRole,
      isAuthenticated: true,
    }))
  }

  const logout = () => {
    user.value = null
    role.value = null
    isAuthenticated.value = false
    shiftActive.value = false
    shiftDate.value = null
    localStorage.removeItem('sonik_auth')
    localStorage.removeItem('sonik_shift_date')
    localStorage.removeItem('sonik_shift_active')
  }

  const startShift = () => {
    const today = new Date().toISOString().split('T')[0]
    shiftActive.value = true
    shiftDate.value = today
    localStorage.setItem('sonik_shift_date', today)
    localStorage.setItem('sonik_shift_active', 'true')
  }

  const endShift = () => {
    shiftActive.value = false
    shiftDate.value = null
    localStorage.removeItem('sonik_shift_date')
    localStorage.removeItem('sonik_shift_active')
  }

  const restoreSession = () => {
    // Restore auth data from localStorage
    const authData = localStorage.getItem('sonik_auth')
    if (authData) {
      try {
        const { user: userData, role: userRole, isAuthenticated: isAuth } = JSON.parse(authData)
        user.value = userData
        role.value = userRole
        isAuthenticated.value = isAuth
      } catch (e) {
        console.error('Failed to restore auth session:', e)
      }
    }

    // Restore shift data from localStorage
    const shiftDateStored = localStorage.getItem('sonik_shift_date')
    const shiftActiveStored = localStorage.getItem('sonik_shift_active') === 'true'

    if (shiftDateStored && shiftActiveStored) {
      const today = new Date().toISOString().split('T')[0]
      // Only restore shift if it's still today
      if (shiftDateStored === today) {
        shiftDate.value = shiftDateStored
        shiftActive.value = true
      } else {
        // Shift is from a previous day, clear it
        localStorage.removeItem('sonik_shift_date')
        localStorage.removeItem('sonik_shift_active')
        shiftActive.value = false
        shiftDate.value = null
      }
    }
  }

  return {
    // State
    user,
    role,
    isAuthenticated,
    shiftActive,
    shiftDate,
    
    // Computed
    isOwner,
    isEmployee,
    
    // Actions
    login,
    logout,
    startShift,
    endShift,
    restoreSession,
  }
})
