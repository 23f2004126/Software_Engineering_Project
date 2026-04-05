<script setup>
import { ref, computed, onMounted } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { customerService } from '../../services/apiService.js'

const searchQuery = ref('')
const selectedCity = ref('')
const selectedStatus = ref('all')
const customers = ref([])
const loading = ref(false)
const error = ref(null)

const cities = computed(() => {
  return [...new Set(customers.value.map(c => c.city))]
})

const filteredCustomers = computed(() => {
  let filtered = customers.value

  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(c => c.status === selectedStatus.value)
  }

  if (selectedCity.value) {
    filtered = filtered.filter(c => c.city === selectedCity.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c =>
      c.name.toLowerCase().includes(query) ||
      c.email.toLowerCase().includes(query) ||
      c.phone.includes(query)
    )
  }

  return filtered
})

const creditUtilization = (customer) => {
  if (customer.credit_limit <= 0) return 0
  return Math.round((customer.credit_balance / customer.credit_limit) * 100)
}

const getCreditColor = (utilization) => {
  if (utilization > 90) return 'text-red-600'
  if (utilization > 70) return 'text-amber-600'
  return 'text-emerald-600'
}

const getCreditBg = (utilization) => {
  if (utilization > 90) return 'bg-red-100'
  if (utilization > 70) return 'bg-amber-100'
  return 'bg-emerald-100'
}

const showAddModal = ref(false)
const newCustomer = ref({
  name: '',
  email: '',
  phone: '',
  city: '',
  address: '',
  credit_limit: 25000,
})

// Load customers on mount
onMounted(async () => {
  await loadCustomers()
})

const loadCustomers = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await customerService.getCustomers()
    customers.value = data
  } catch (err) {
    error.value = err.message
    console.error('Failed to load customers:', err)
  } finally {
    loading.value = false
  }
}

const handleAddCustomer = async () => {
  try {
    await customerService.createCustomer({
      name: newCustomer.value.name,
      email: newCustomer.value.email,
      phone: newCustomer.value.phone,
      city: newCustomer.value.city,
      address: newCustomer.value.address,
      credit_limit: newCustomer.value.credit_limit,
    })
    await loadCustomers()
    showAddModal.value = false
    newCustomer.value = {
      name: '',
      email: '',
      phone: '',
      city: '',
      address: '',
      credit_limit: 25000,
    }
  } catch (err) {
    error.value = err.message
    console.error('Failed to create customer:', err)
  }
}
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">Customers</h1>
          <p class="text-sm text-slate-500 mt-1">
            Manage all customers and their credit profiles
          </p>
        </div>
        <Button variant="primary" @click="showAddModal = true">
          + Add Customer
        </Button>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card padding="lg" class="text-center">
          <div class="text-3xl font-bold text-slate-900">{{ customers.length }}</div>
          <p class="text-sm text-slate-600 mt-2">Total Customers</p>
        </Card>
        <Card padding="lg" class="text-center">
          <div class="text-3xl font-bold text-emerald-600">{{ customers.filter(c => c.status === 'active').length }}</div>
          <p class="text-sm text-slate-600 mt-2">Active</p>
        </Card>
        <Card padding="lg" class="text-center">
          <div class="text-3xl font-bold text-amber-600">
            ₹{{ (customers.reduce((sum, c) => sum + (c.credit_balance || 0), 0) / 100000).toFixed(1) }}L
          </div>
          <p class="text-sm text-slate-600 mt-2">Total Credit Used</p>
        </Card>
        <Card padding="lg" class="text-center">
          <div class="text-3xl font-bold text-blue-600">
            ₹{{ (customers.reduce((sum, c) => sum + c.credit_limit, 0) / 100000).toFixed(1) }}L
          </div>
          <p class="text-sm text-slate-600 mt-2">Total Credit Limit</p>
        </Card>
      </div>

      <!-- Filters -->
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <!-- Search -->
        <div class="lg:col-span-2">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by name, email or phone..."
              class="w-full bg-white border border-slate-200 rounded-lg px-4 py-2 pl-9 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>

        <!-- City Filter -->
        <select
          v-model="selectedCity"
          class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <option value="">All Cities</option>
          <option v-for="city in cities" :key="city" :value="city">
            {{ city }}
          </option>
        </select>

        <!-- Status Filter -->
        <select
          v-model="selectedStatus"
          class="px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <!-- Customers Table -->
      <Card padding="none">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50">
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Name</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Contact</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">City</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Credit Limit</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Credit Used</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Utilization</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Last Purchase</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-900">Status</th>
                <th class="px-6 py-3 text-right font-semibold text-slate-900">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="customer in filteredCustomers" 
                :key="customer.id"
                class="border-b border-slate-100 hover:bg-slate-50 transition-colors"
              >
                <td class="px-6 py-4 font-semibold text-slate-900">{{ customer.name }}</td>
                <td class="px-6 py-4">
                  <div class="text-xs text-slate-600">{{ customer.email }}</div>
                  <div class="text-xs text-slate-400">{{ customer.phone }}</div>
                </td>
                <td class="px-6 py-4 text-slate-600">{{ customer.city }}</td>
                <td class="px-6 py-4 font-semibold text-slate-900">₹{{ customer.credit_limit.toLocaleString() }}</td>
                <td class="px-6 py-4">
                  <span class="font-semibold text-amber-600">₹{{ (customer.credit_balance || 0).toLocaleString() }}</span>
                </td>
                <td class="px-6 py-4">
                  <div :class="['inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold', getCreditBg(creditUtilization(customer))]">
                    <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center" :class="getCreditColor(creditUtilization(customer))">
                      {{ creditUtilization(customer) }}%
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-slate-600">{{ customer.created_at ? new Date(customer.created_at).toLocaleDateString() : 'N/A' }}</td>
                <td class="px-6 py-4">
                  <span :class="['text-xs px-2.5 py-1 rounded-full font-semibold', customer.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700']">
                    {{ customer.status || 'active' }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="flex justify-end gap-2">
                    <router-link :to="`/credit/${customer.id}`" class="text-sm text-emerald-600 hover:text-emerald-700 font-semibold">
                      View
                    </router-link>
                    <button class="text-sm text-slate-600 hover:text-slate-900 font-semibold">Edit</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="filteredCustomers.length === 0" class="flex items-center justify-center py-12">
          <div class="text-center">
            <div class="text-4xl mb-2">👥</div>
            <p class="text-slate-500 font-medium">No customers found</p>
            <p class="text-slate-400 text-sm mt-1">Try adjusting your filters</p>
          </div>
        </div>
      </Card>

      <!-- Add Customer Modal -->
      <Modal v-model="showAddModal" title="Add New Customer" size="md">
        <div class="space-y-4">
          <Input v-model="newCustomer.name" label="Customer Name" placeholder="e.g., Fresh Mart" />
          <Input v-model="newCustomer.email" label="Email" type="email" placeholder="customer@example.com" />
          <Input v-model="newCustomer.phone" label="Phone Number" placeholder="10-digit mobile number" />
          <Input v-model="newCustomer.city" label="City" placeholder="e.g., Mumbai" />
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Credit Limit (₹)</label>
            <input
              v-model.number="newCustomer.credit_limit"
              type="number"
              placeholder="25000"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
            />
          </div>
        </div>

        <template #footer>
          <Button variant="secondary" @click="showAddModal = false">
            Cancel
          </Button>
          <Button variant="primary" @click="handleAddCustomer">
            Add Customer
          </Button>
        </template>
      </Modal>
    </div>
  </MainLayout>
</template>

<style scoped>
</style>
