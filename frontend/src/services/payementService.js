import api from '../utils/api'

export const paymentService = {
  createOrder(payload) {
    return api.post('/api/create-order', payload)
  },

  verifyPayment(payload) {
    return api.post('/api/verify-payment', payload)
  },
}
