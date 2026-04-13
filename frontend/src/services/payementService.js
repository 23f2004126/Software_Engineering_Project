import axios from 'axios'

export const paymentService = {
  createOrder(amount) {
    return axios.post('/api/create-order', {
      amount
    })
  },

  verifyPayment(payload) {
    return axios.post('/api/verify-payment', payload)
  }
}