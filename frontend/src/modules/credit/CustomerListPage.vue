<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'

const searchQuery = ref('')
const selectedCity = ref('')
const selectedStatus = ref('all')

const customers = ref([
  {
    id: 1,
    name: 'Prakash Mart',
    email: 'prakash@mart.com',
    phone: '9876543210',
    city: 'Mumbai',
    address: '123 Market Street, Mumbai',
    totalCredit: 45000,
    usedCredit: 38000,
    status: 'active',
    joinDate: '2024-01-15',
    lastPurchase: '2025-06-05',
  },
  {
    id: 2,
    name: 'Super Market Chain',
    email: 'info@supermarket.com',
    phone: '9765432109',
    city: 'Bangalore',
    address: '456 Commercial Area, Bangalore',
    totalCredit: 100000,
    usedCredit: 92000,
    status: 'active',
    joinDate: '2023-05-10',
    lastPurchase: '2025-06-04',
  },
  {
    id: 3,
    name: 'Local Store',
    email: 'local@store.com',
    phone: '9654321098',
    city: 'Delhi',
    address: '789 Retail Zone, Delhi',
    totalCredit: 25000,
    usedCredit: 5000,
    status: 'active',
    joinDate: '2024-03-22',
    lastPurchase: '2025-06-05',
  },
  {
    id: 4,
    name: 'Premium Retailers',
    email: 'premium@retailers.com',
    phone: '9543210987',
    city: 'Mumbai',
    address: '321 Premium Zone, Mumbai',
    totalCredit: 75000,
    usedCredit: 0,
    status: 'inactive',
    joinDate: '2023-11-08',
    lastPurchase: '2025-04-15',
  },
  {
    id: 5,
    name: 'City Convenience',
    email: 'city@conv.com',
    phone: '9432109876',
    city: 'Hyderabad',
    address: '654 City Center, Hyderabad',
    totalCredit: 50000,
    usedCredit: 22000,
    status: 'active',
    joinDate: '2024-02-18',
    lastPurchase: '2025-06-03',
  },
])

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
  return Math.round((customer.usedCredit / customer.totalCredit) * 100)
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
  totalCredit: 25000,
})

const handleAddCustomer = () => {
  customers.value.push({
    id: customers.value.length + 1,
    ...newCustomer.value,
    address: '',
    usedCredit: 0,
    status: 'active',
    joinDate: new Date().toISOString().split('T')[0],
    lastPurchase: new Date().toISOString().split('T')[0],
  })
  showAddModal.value = false
  newCustomer.value = {
    name: '',
    email: '',
    phone: '',
    city: '',
    totalCredit: 25000,
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
            ₹{{ (customers.reduce((sum, c) => sum + c.usedCredit, 0) / 100000).toFixed(1) }}L
          </div>
          <p class="text-sm text-slate-600 mt-2">Total Credit Used</p>
        </Card>
        <Card padding="lg" class="text-center">
          <div class="text-3xl font-bold text-blue-600">
            ₹{{ (customers.reduce((sum, c) => sum + c.totalCredit, 0) / 100000).toFixed(1) }}L
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
                <td class="px-6 py-4 font-semibold text-slate-900">₹{{ customer.totalCredit.toLocaleString() }}</td>
                <td class="px-6 py-4">
                  <span class="font-semibold text-amber-600">₹{{ customer.usedCredit.toLocaleString() }}</span>
                </td>
                <td class="px-6 py-4">
                  <div :class="['inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold', getCreditBg(creditUtilization(customer))]">
                    <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center" :class="getCreditColor(creditUtilization(customer))">
                      {{ creditUtilization(customer) }}%
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 text-slate-600">{{ customer.lastPurchase }}</td>
                <td class="px-6 py-4">
                  <span :class="['text-xs px-2.5 py-1 rounded-full font-semibold', customer.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700']">
                    {{ customer.status }}
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
              v-model.number="newCustomer.totalCredit"
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
