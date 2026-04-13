let razorpayLoaderPromise

export function ensureRazorpayLoaded() {
  if (typeof window === 'undefined') {
    return Promise.reject(new Error('Razorpay checkout can only be loaded in the browser'))
  }

  if (window.Razorpay) {
    return Promise.resolve(window.Razorpay)
  }

  if (razorpayLoaderPromise) {
    return razorpayLoaderPromise
  }

  razorpayLoaderPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true

    script.onload = () => resolve(window.Razorpay)
    script.onerror = () => reject(new Error('Failed to load Razorpay checkout script'))

    document.body.appendChild(script)
  })

  return razorpayLoaderPromise
}
