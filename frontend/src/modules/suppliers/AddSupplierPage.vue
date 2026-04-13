<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { supplierService } from '../../services/apiService'

const router = useRouter()

const supplier = ref({
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  city: '',
  address: '',
  rating: 4.5,
  payment_terms: 30,
  status: 'active'
})

const error = ref('')
const loading = ref(false)

// ✅ Validation helpers
const isValidEmail = (email) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

const isValidPhone = (phone) => {
  return /^[0-9]{10}$/.test(phone)
}

const validateForm = () => {
  if (
    !supplier.value.name ||
    !supplier.value.contact_person ||
    !supplier.value.phone ||
    !supplier.value.email ||
    !supplier.value.city ||
    !supplier.value.address
  ) {
    return 'Please fill all required fields'
  }

  if (!isValidPhone(supplier.value.phone)) {
    return 'Phone must be 10 digits'
  }

  if (!isValidEmail(supplier.value.email)) {
    return 'Invalid email format'
  }

  return null
}

// ✅ Submit handler
const handleSubmit = async () => {
  error.value = ''

  const validationError = validateForm()
  if (validationError) {
    error.value = validationError
    return
  }

  try {
    loading.value = true

    await supplierService.createSupplier(supplier.value)

    router.push('/suppliers')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-6">
    <div class="w-full max-w-2xl bg-white rounded-2xl shadow-lg p-6 space-y-6">

      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Add Supplier</h1>
        <p class="text-sm text-slate-500 mt-1">
          Fill in the details to create a new supplier
        </p>
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="bg-red-50 border border-red-200 text-red-600 px-4 py-2 rounded-lg"
      >
        {{ error }}
      </div>

      <!-- Form -->
      <div class="grid grid-cols-2 gap-4">

        <!-- Name -->
        <div>
          <label class="label">Supplier Name *</label>
          <input v-model="supplier.name" class="input" placeholder="Fresh Farms Dairy" />
        </div>

        <!-- Contact Person -->
        <div>
          <label class="label">Contact Person *</label>
          <input v-model="supplier.contact_person" class="input" placeholder="Rajesh Kumar" />
        </div>

        <!-- Phone -->
        <div>
          <label class="label">Phone *</label>
          <input v-model="supplier.phone" class="input" placeholder="9876543210" />
        </div>

        <!-- Email -->
        <div>
          <label class="label">Email *</label>
          <input v-model="supplier.email" type="email" class="input" placeholder="example@gmail.com" />
        </div>

        <!-- City -->
        <div>
          <label class="label">City *</label>
          <input v-model="supplier.city" class="input" placeholder="Chennai" />
        </div>

        <!-- Address -->
        <div>
          <label class="label">Address *</label>
          <input v-model="supplier.address" class="input" placeholder="Full address" />
        </div>

        <!-- Rating -->
        <div>
          <label class="label">Rating</label>
          <input
            v-model.number="supplier.rating"
            type="number"
            step="0.1"
            min="0"
            max="5"
            class="input"
          />
        </div>

        <!-- Payment Terms -->
        <div>
          <label class="label">Payment Terms (days)</label>
          <input
            v-model.number="supplier.payment_terms"
            type="number"
            class="input"
          />
        </div>

        <!-- Status -->
        <div class="col-span-2">
          <label class="label">Status</label>
          <select v-model="supplier.status" class="input">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

      </div>

      <!-- Buttons -->
      <div class="flex justify-end gap-3 pt-4 border-t">
        <button
          class="px-4 py-2 rounded-xl border border-slate-300 hover:bg-slate-100"
          @click="router.push('/suppliers')"
        >
          Cancel
        </button>

        <button
          class="px-5 py-2 rounded-xl bg-emerald-600 text-white font-semibold hover:bg-emerald-700 disabled:opacity-50"
          :disabled="loading"
          @click="handleSubmit"
        >
          {{ loading ? 'Saving...' : 'Save Supplier' }}
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.input {
  @apply w-full mt-1 px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400;
}

.label {
  @apply text-sm font-medium text-slate-600;
}
</style>