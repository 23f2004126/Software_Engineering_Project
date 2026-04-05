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
      const response = await api.post('/api/sales', saleData)
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
      const response = await api.post(`/api/sales/${billId}/reverse`, {})
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
      const response = await api.post('/api/inventory', productData)
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
      const response = await api.put(`/api/inventory/${productId}`, productData)
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
      const response = await api.delete(`/api/inventory/${productId}`)
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
      const response = await api.post('/api/inventory/stock-adjustment', {
        product_id: productId,
        quantity_change: quantityChange,
        reason: reason
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
      const response = await api.post('/api/inventory/damage-loss', damageData)
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

/**
 * CUSTOMER API SERVICES
 * Handles all customer-related API calls
 */
export const customerService = {
  /**
   * Create a new customer
   * @param {Object} customerData - Customer details
   * @returns {Promise<Object>} Created customer
   */
  async createCustomer(customerData) {
    try {
      const response = await api.post('/api/customers', customerData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create customer')
    }
  },

  /**
   * Get all customers with optional filters
   * @param {Object} options - Query options
   * @returns {Promise<Array>} List of customers
   */
  async getCustomers(options = {}) {
    try {
      const params = new URLSearchParams()
      
      if (options.status) params.append('status', options.status)
      if (options.skip !== undefined) params.append('skip', options.skip)
      if (options.limit !== undefined) params.append('limit', options.limit)
      if (options.search) params.append('search', options.search)

      const response = await api.get(`/api/customers?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch customers')
    }
  },

  /**
   * Get customer details
   * @param {number} customerId - Customer ID
   * @returns {Promise<Object>} Customer details
   */
  async getCustomer(customerId) {
    try {
      const response = await api.get(`/api/customers/${customerId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch customer')
    }
  },

  /**
   * Get risk assessment for all customers
   * @returns {Promise<Array>} List of customers with risk levels
   */
  async getRiskAssessment() {
    try {
      const response = await api.get('/api/customers/risk-assessment')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch risk assessment')
    }
  },

  /**
   * Update customer information
   * @param {number} customerId - Customer ID
   * @param {Object} customerData - Updated customer data
   * @returns {Promise<Object>} Updated customer
   */
  async updateCustomer(customerId, customerData) {
    try {
      const response = await api.put(`/api/customers/${customerId}`, customerData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update customer')
    }
  },

  /**
   * Update customer credit limit
   * @param {number} customerId - Customer ID
   * @param {Decimal} creditLimit - New credit limit
   * @param {string} reason - Reason for change
   * @returns {Promise<Object>} Updated customer
   */
  async updateCreditLimit(customerId, creditLimit, reason) {
    try {
      const response = await api.put(`/api/customers/${customerId}/credit-limit`, {
        credit_limit: creditLimit,
        reason: reason
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update credit limit')
    }
  },

  /**
   * Record a customer payment
   * @param {number} customerId - Customer ID
   * @param {Object} paymentData - Payment details (amount, mode, reference)
   * @returns {Promise<Object>} Payment confirmation
   */
  async recordPayment(customerId, paymentData) {
    try {
      const response = await api.post(`/api/customers/${customerId}/payment`, paymentData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to record payment')
    }
  },

  /**
   * Freeze customer credit
   * @param {number} customerId - Customer ID
   * @param {string} reason - Reason for freeze
   * @param {number} durationDays - Duration in days
   * @returns {Promise<Object>} Freeze confirmation
   */
  async freezeCredit(customerId, reason, durationDays) {
    try {
      const response = await api.post(`/api/customers/${customerId}/credit-freeze`, {
        reason: reason,
        duration_days: durationDays
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to freeze credit')
    }
  },

  /**
   * Delete/inactivate a customer
   * @param {number} customerId - Customer ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteCustomer(customerId) {
    try {
      const response = await api.delete(`/api/customers/${customerId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete customer')
    }
  }
}

/**
 * SUPPLIER API SERVICES
 * Handles all supplier-related API calls
 */
export const supplierService = {
  /**
   * Create a new supplier
   * @param {Object} supplierData - Supplier details
   * @returns {Promise<Object>} Created supplier
   */
  async createSupplier(supplierData) {
    try {
      const response = await api.post('/api/suppliers', supplierData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create supplier')
    }
  },

  /**
   * Get all suppliers with optional filters
   * @param {Object} options - Query options
   * @returns {Promise<Array>} List of suppliers
   */
  async getSuppliers(options = {}) {
    try {
      const params = new URLSearchParams()
      
      if (options.status) params.append('status', options.status)
      if (options.skip !== undefined) params.append('skip', options.skip)
      if (options.limit !== undefined) params.append('limit', options.limit)

      const response = await api.get(`/api/suppliers?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch suppliers')
    }
  },

  /**
   * Get supplier details
   * @param {number} supplierId - Supplier ID
   * @returns {Promise<Object>} Supplier details
   */
  async getSupplier(supplierId) {
    try {
      const response = await api.get(`/api/suppliers/${supplierId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch supplier')
    }
  },

  /**
   * Update supplier information
   * @param {number} supplierId - Supplier ID
   * @param {Object} supplierData - Updated supplier data
   * @returns {Promise<Object>} Updated supplier
   */
  async updateSupplier(supplierId, supplierData) {
    try {
      const response = await api.put(`/api/suppliers/${supplierId}`, supplierData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update supplier')
    }
  },

  /**
   * Get pending payments for a supplier
   * @param {number} supplierId - Supplier ID
   * @returns {Promise<Array>} List of pending payments
   */
  async getPendingPayments(supplierId) {
    try {
      const response = await api.get(`/api/suppliers/${supplierId}/pending-payments`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch pending payments')
    }
  },

  /**
   * Record a supplier payment
   * @param {number} supplierId - Supplier ID
   * @param {Object} paymentData - Payment details
   * @returns {Promise<Object>} Payment confirmation
   */
  async recordPayment(supplierId, paymentData) {
    try {
      const response = await api.post(`/api/suppliers/${supplierId}/payment`, paymentData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to record payment')
    }
  },

  /**
   * Get payment history for all suppliers
   * @returns {Promise<Array>} Payment history
   */
  async getPaymentHistory() {
    try {
      const response = await api.get('/api/suppliers/payment-history/all')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch payment history')
    }
  },

  /**
   * Delete/inactivate a supplier
   * @param {number} supplierId - Supplier ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteSupplier(supplierId) {
    try {
      const response = await api.delete(`/api/suppliers/${supplierId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete supplier')
    }
  }
}

/**
 * EXPENSE API SERVICES
 * Handles all expense-related API calls
 */
export const expenseService = {
  /**
   * Add a new expense
   * @param {Object} expenseData - Expense details
   * @returns {Promise<Object>} Created expense
   */
  async addExpense(expenseData) {
    try {
      const response = await api.post('/api/expenses', expenseData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to add expense')
    }
  },

  /**
   * Get all expenses with optional filters
   * @param {Object} options - Query options
   * @returns {Promise<Array>} List of expenses
   */
  async getExpenses(options = {}) {
    try {
      const params = new URLSearchParams()
      
      if (options.category) params.append('category', options.category)
      if (options.startDate) params.append('start_date', options.startDate)
      if (options.endDate) params.append('end_date', options.endDate)
      if (options.skip !== undefined) params.append('skip', options.skip)
      if (options.limit !== undefined) params.append('limit', options.limit)

      const response = await api.get(`/api/expenses?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch expenses')
    }
  },

  /**
   * Get expense summary for a month
   * @param {number} month - Month (1-12)
   * @param {number} year - Year
   * @returns {Promise<Object>} Expense summary
   */
  async getSummary(month, year) {
    try {
      const response = await api.get(`/api/expenses/summary?month=${month}&year=${year}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch summary')
    }
  },

  /**
   * Get financial report for date range
   * @param {string} fromDate - Start date (ISO format)
   * @param {string} toDate - End date (ISO format)
   * @returns {Promise<Object>} Financial report
   */
  async getFinancialReport(fromDate, toDate) {
    try {
      const params = new URLSearchParams()
      params.append('from_date', fromDate)
      params.append('to_date', toDate)

      const response = await api.get(`/api/expenses/financial-report?${params.toString()}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch financial report')
    }
  },

  /**
   * Delete an expense
   * @param {number} expenseId - Expense ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteExpense(expenseId) {
    try {
      const response = await api.delete(`/api/expenses/${expenseId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete expense')
    }
  }
}

/**
 * TRANSACTION API SERVICES
 * Handles all transaction/credit-related API calls
 */
export const transactionService = {
  /**
   * Add a transaction (debit or credit)
   * @param {Object} transactionData - Transaction details
   * @returns {Promise<Object>} Created transaction
   */
  async addTransaction(transactionData) {
    try {
      const response = await api.post('/api/transactions', transactionData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to add transaction')
    }
  },

  /**
   * Get transactions for a customer
   * @param {number} customerId - Customer ID
   * @param {Object} options - Filter options
   * @returns {Promise<Array>} List of transactions
   */
  async getTransactions(customerId, options = {}) {
    try {
      const params = new URLSearchParams()
      
      if (options.type) params.append('type', options.type)
      if (options.status) params.append('status', options.status)

      const response = await api.get(`/api/transactions/${customerId}?${params.toString()}`)
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch transactions')
    }
  },

  /**
   * Get credit aging report
   * @returns {Promise<Array>} Credit report items
   */
  async getCreditReport() {
    try {
      const response = await api.get('/api/transactions/report/credit-aging')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch credit report')
    }
  },

  /**
   * Waive a transaction (mark as waived)
   * @param {number} transactionId - Transaction ID
   * @returns {Promise<Object>} Updated transaction
   */
  async waiveTransaction(transactionId) {
    try {
      const response = await api.patch(`/api/transactions/${transactionId}/waive`, {})
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to waive transaction')
    }
  }
}

/**
 * DASHBOARD API SERVICES
 * Handles all dashboard data API calls
 */
export const dashboardService = {
  /**
   * Get dashboard KPIs
   * @returns {Promise<Object>} KPI data
   */
  async getKPIs() {
    try {
      const response = await api.get('/api/dashboard/kpis')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch KPIs')
    }
  },

  /**
   * Get dashboard alerts
   * @returns {Promise<Array>} List of alerts
   */
  async getAlerts() {
    try {
      const response = await api.get('/api/dashboard/alerts')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch alerts')
    }
  },

  /**
   * Get quick statistics
   * @returns {Promise<Object>} Quick stats
   */
  async getQuickStats() {
    try {
      const response = await api.get('/api/dashboard/quick-stats')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch quick stats')
    }
  },

  /**
   * Get dashboard summary
   * @returns {Promise<Object>} Dashboard summary
   */
  async getSummary() {
    try {
      const response = await api.get('/api/dashboard/summary')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch summary')
    }
  },

  /**
   * Get top selling products
   * @returns {Promise<Array>} Top products list
   */
  async getTopProducts() {
    try {
      const response = await api.get('/api/dashboard/top-products')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch top products')
    }
  },

  /**
   * Get sales overview
   * @returns {Promise<Object>} Sales overview data
   */
  async getSalesOverview() {
    try {
      const response = await api.get('/api/dashboard/sales-overview')
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch sales overview')
    }
  }
}

/**
 * CATEGORY API SERVICES
 * Handles all category-related API calls
 */
export const categoryService = {
  /**
   * Create a new category
   * @param {Object} categoryData - Category details
   * @returns {Promise<Object>} Created category
   */
  async createCategory(categoryData) {
    try {
      const response = await api.post('/api/categories', categoryData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create category')
    }
  },

  /**
   * Get all categories
   * @returns {Promise<Array>} List of categories
   */
  async getCategories() {
    try {
      const response = await api.get('/api/categories')
      return response.data || []
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch categories')
    }
  },

  /**
   * Get category by ID
   * @param {number} categoryId - Category ID
   * @returns {Promise<Object>} Category details
   */
  async getCategory(categoryId) {
    try {
      const response = await api.get(`/api/categories/${categoryId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch category')
    }
  },

  /**
   * Update category
   * @param {number} categoryId - Category ID
   * @param {Object} categoryData - Updated category data
   * @returns {Promise<Object>} Updated category
   */
  async updateCategory(categoryId, categoryData) {
    try {
      const response = await api.put(`/api/categories/${categoryId}`, categoryData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update category')
    }
  },

  /**
   * Delete category
   * @param {number} categoryId - Category ID
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteCategory(categoryId) {
    try {
      const response = await api.delete(`/api/categories/${categoryId}`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete category')
    }
  }
}

export default {
  sales: salesService,
  inventory: inventoryService,
  customer: customerService,
  supplier: supplierService,
  expense: expenseService,
  transaction: transactionService,
  dashboard: dashboardService,
  category: categoryService
}
