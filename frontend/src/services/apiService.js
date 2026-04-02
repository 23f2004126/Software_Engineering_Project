import { useAuthStore } from '../stores/authStore'
import api from '../utils/api'

/**
 * SALES API SERVICES
 * Handles all sales-related API calls
 */
export const salesService = {
  /**
   * Search products by query
   * @param {string} query - Search query
   * @returns {Promise<Array>} List of products
   */
  async searchProducts(query) {
    try {
      const response = await api.get(`/api/sales/products/search?q=${encodeURIComponent(query)}`)
      return response.data || []
    } catch (error) {
      console.error('Error searching products:', error)
      throw new Error(error.response?.data?.detail || 'Failed to search products')
    }
  },

  /**
   * Get product details by ID
   * @param {number} productId - Product ID
   * @returns {Promise<Object>} Product details
   */
  async getProduct(productId) {
    try {
      const response = await api.get(`/api/sales/products/${productId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch product')
    }
  },

  /**
   * Get daily sales summary
   * @param {string} date - ISO format date (YYYY-MM-DD)
   * @returns {Promise<Object>} Daily summary with totals by payment method
   */
  async getDailySummary(date) {
    try {
      const response = await api.get(`/api/sales/daily/summary?date=${date}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch daily summary')
    }
  },

  /**
   * Create a new sale
   * @param {Object} saleData - Sale creation data
   * @returns {Promise<Object>} Created sale with bill_id
   */
  async createSale(saleData) {
    try {
      const authStore = useAuthStore()
      const response = await api.post('/api/sales', saleData, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create sale')
    }
  },

  /**
   * Get sale details
   * @param {number} billId - Bill/Sale ID
   * @returns {Promise<Object>} Sale details with items and transactions
   */
  async getSaleDetails(billId) {
    try {
      const response = await api.get(`/api/sales/${billId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch sale details')
    }
  },

  /**
   * Get sales history with optional filters
   * @param {Object} filters - Filter parameters
   * @returns {Promise<Array>} List of sales
   */
  async getSalesHistory(filters = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.paymentMethod) params.append('payment_method', filters.paymentMethod)
      if (filters.status) params.append('status', filters.status)
      if (filters.customerId) params.append('customer_id', filters.customerId)
      if (filters.skip !== undefined) params.append('skip', filters.skip)
      if (filters.limit !== undefined) params.append('limit', filters.limit)

      const response = await api.get(`/api/sales?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch sales history')
    }
  },

  /**
   * Reverse a sale
   * @param {number} billId - Bill ID to reverse
   * @returns {Promise<Object>} Reversal response
   */
  async reverseSale(billId) {
    try {
      const authStore = useAuthStore()
      const response = await api.post(`/api/sales/${billId}/reverse`, {}, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to reverse sale')
    }
  }
}

/**
 * INVENTORY API SERVICES
 * Handles all inventory-related API calls
 */
export const inventoryService = {
  /**
   * Create a new product
   * @param {Object} productData - Product creation data
   * @returns {Promise<Object>} Created product
   */
  async createProduct(productData) {
    try {
      const authStore = useAuthStore()
      const response = await api.post('/api/inventory', productData, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create product')
    }
  },

  /**
   * Get all products with pagination and filters
   * @param {Object} options - Query options
   * @returns {Promise<Array>} List of products
   */
  async getProducts(options = {}) {
    try {
      const params = new URLSearchParams()
      
      if (options.skip !== undefined) params.append('skip', options.skip)
      if (options.limit !== undefined) params.append('limit', options.limit)
      if (options.category) params.append('category', options.category)
      if (options.status) params.append('status', options.status || 'active')
      if (options.search) params.append('search', options.search)

      const response = await api.get(`/api/inventory?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch products')
    }
  },

  /**
   * Get product by ID (alias for getProductDetail)
   * @param {number} productId - Product ID
   * @returns {Promise<Object>} Product details with stock history
   */
  async getProductById(productId) {
    return this.getProductDetail(productId)
  },

  /**
   * Get product details with stock history
   * @param {number} productId - Product ID
   * @returns {Promise<Object>} Product details with movements
   */
  async getProductDetail(productId) {
    try {
      const response = await api.get(`/api/inventory/${productId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch product details')
    }
  },

  /**
   * Update product
   * @param {number} productId - Product ID
   * @param {Object} productData - Updated product data
   * @returns {Promise<Object>} Updated product
   */
  async updateProduct(productId, productData) {
    try {
      const authStore = useAuthStore()
      const response = await api.put(`/api/inventory/${productId}`, productData, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update product')
    }
  },

  /**
   * Discontinue/delete a product
   * @param {number} productId - Product ID
   * @returns {Promise<Object>} Deletion response
   */
  async deleteProduct(productId) {
    try {
      const authStore = useAuthStore()
      const response = await api.delete(`/api/inventory/${productId}`, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete product')
    }
  },

  /**
   * Get product by barcode
   * @param {string} barcode - Product barcode
   * @returns {Promise<Object>} Product details
   */
  async getProductByBarcode(barcode) {
    try {
      const response = await api.get(`/api/sales/products/barcode/${barcode}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Product not found')
    }
  },

  /**
   * Adjust product stock
   * @param {number} productId - Product ID
   * @param {number} quantityChange - Quantity to add/subtract
   * @param {string} reason - Reason for adjustment
   * @returns {Promise<Object>} Adjustment response
   */
  async adjustStock(productId, quantityChange, reason) {
    try {
      const authStore = useAuthStore()
      const response = await api.post('/api/inventory/stock-adjustment', {
        product_id: productId,
        quantity_change: quantityChange,
        reason: reason
      }, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to adjust stock')
    }
  },

  /**
   * Get stock movement history for a product
   * @param {number} productId - Product ID
   * @param {Object} options - Pagination options
   * @returns {Promise<Array>} Stock movements
   */
  async getStockMovements(productId, options = {}) {
    try {
      const params = new URLSearchParams()
      
      if (options.skip !== undefined) params.append('skip', options.skip)
      if (options.limit !== undefined) params.append('limit', options.limit)

      const response = await api.get(`/api/inventory/${productId}/movements?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch stock movements')
    }
  },

  /**
   * Get low stock products
   * @returns {Promise<Array>} Products below reorder level
   */
  async getLowStockProducts() {
    try {
      const response = await api.get('/api/inventory/alerts/low-stock')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch low stock alerts')
    }
  },

  /**
   * Get expiring soon products
   * @param {number} days - Days until expiry (default 30)
   * @returns {Promise<Array>} Expiring products
   */
  async getExpiringProducts(days = 30) {
    try {
      const response = await api.get(`/api/inventory/alerts/expiring-soon?days=${days}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch expiring alerts')
    }
  },

  /**
   * Get total inventory value
   * @returns {Promise<Object>} Inventory value statistics
   */
  async getTotalInventoryValue() {
    try {
      const response = await api.get('/api/inventory/value/total')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch inventory value')
    }
  },

  /**
   * Log damage/loss event
   * @param {Object} damageData - Damage/loss details
   * @returns {Promise<Object>} Created record
   */
  async logDamageLoss(damageData) {
    try {
      const authStore = useAuthStore()
      const response = await api.post('/api/inventory/damage-loss', damageData, {
        headers: {
          'X-User-ID': authStore.user?.user_id || 1
        }
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to log damage/loss')
    }
  },

  /**
   * Get damage/loss report
   * @param {Object} filters - Report filters
   * @returns {Promise<Object>} Damage/loss report
   */
  async getDamageLossReport(filters = {}) {
    try {
      const params = new URLSearchParams()
      
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.reason) params.append('reason', filters.reason)

      const response = await api.get(`/api/inventory/damage-loss/report?${params.toString()}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch damage/loss report')
    }
  },

  /**
   * Get inventory statistics/overview
   * @returns {Promise<Object>} Inventory statistics
   */
  async getInventoryStats() {
    try {
      const response = await api.get('/api/inventory/stats/overview')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch inventory stats')
    }
  }
}

export default {
  sales: salesService,
  inventory: inventoryService
}
