<script setup>
import { ref, computed } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Modal from '../../components/ui/Modal.vue'

const mockEmployees = [
  { id: 1, name: 'Ravi Kumar', role: 'Sales Staff', email: 'ravi@sonik.com', phone: '9876543210', joinDate: '2024-01-15', performance: 92, status: 'active' },
  { id: 2, name: 'Priya Singh', role: 'Supervisor', email: 'priya@sonik.com', phone: '9876543211', joinDate: '2023-08-10', performance: 88, status: 'active' },
  { id: 3, name: 'Amit Kumar', role: 'Sales Staff', email: 'amit@sonik.com', phone: '9876543212', joinDate: '2024-03-20', performance: 76, status: 'active' },
  { id: 4, name: 'Neha Verma', role: 'Inventory Manager', email: 'neha@sonik.com', phone: '9876543213', joinDate: '2023-12-01', performance: 85, status: 'active' },
  { id: 5, name: 'Vikram Desai', role: 'Store Manager', email: 'vikram@sonik.com', phone: '9876543214', joinDate: '2023-01-10', performance: 95, status: 'active' },
  { id: 6, name: 'Anjali Nair', role: 'Billing Staff', email: 'anjali@sonik.com', phone: '9876543215', joinDate: '2024-05-01', performance: 82, status: 'inactive' },
]

const showAddModal = ref(false)

const newEmployee = ref({
  name: '',
  role: 'Sales Staff',
  email: '',
  phone: '',
})

const roleColors = {
  'Sales Staff': { icon: '👤', color: 'bg-blue-100 text-blue-700' },
  'Supervisor': { icon: '👨‍💼', color: 'bg-purple-100 text-purple-700' },
  'Inventory Manager': { icon: '📦', color: 'bg-green-100 text-green-700' },
  'Store Manager': { icon: '🏢', color: 'bg-red-100 text-red-700' },
  'Billing Staff': { icon: '💳', color: 'bg-amber-100 text-amber-700' },
}

const performanceColor = (score) => {
  if (score >= 90) return 'text-emerald-600'
  if (score >= 80) return 'text-blue-600'
  if (score >= 70) return 'text-amber-600'
  return 'text-red-600'
}

const handleAddEmployee = () => {
  showAddModal.value = false
  newEmployee.value = {
    name: '',
    role: 'Sales Staff',
    email: '',
    phone: '',
  }
}

const activeCount = computed(() => mockEmployees.filter((e) => e.status === 'active').length)
const avgPerformance = computed(() => {
  const avg = mockEmployees.reduce((sum, e) => sum + e.performance, 0) / mockEmployees.length
  return Math.round(avg)
})
</script>

<template>
  <MainLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Employees</h1>
        <p class="text-sm text-slate-500 mt-1">Manage team members and performance</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-4 gap-4">
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Total Employees</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">{{ mockEmployees.length }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Active</p>
          <p class="font-mono text-3xl font-bold text-emerald-600 mt-2">{{ activeCount }}</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Avg Performance</p>
          <p class="font-mono text-3xl font-bold text-blue-600 mt-2">{{ avgPerformance }}%</p>
        </Card>
        <Card>
          <p class="text-xs font-semibold text-slate-400 uppercase">Roles</p>
          <p class="font-mono text-3xl font-bold text-slate-900 mt-2">5</p>
        </Card>
      </div>

      <!-- Employee Cards Grid -->
      <div class="grid grid-cols-3 gap-5">
        <Card v-for="employee in mockEmployees" :key="employee.id" hover>
          <template #header>
            <div class="flex items-start justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ employee.name }}</p>
                <span
                  class="inline-block text-xs px-2 py-0.5 rounded-full font-semibold mt-2"
                  :class="roleColors[employee.role].color"
                >
                  {{ roleColors[employee.role].icon }} {{ employee.role }}
                </span>
              </div>
              <span
                class="text-sm px-2 py-1 rounded-full font-semibold"
                :class="employee.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'"
              >
                {{ employee.status }}
              </span>
            </div>
          </template>

          <div class="space-y-3 mb-4">
            <div>
              <p class="text-xs text-slate-500 mb-1">Email</p>
              <p class="text-sm font-semibold text-slate-900">{{ employee.email }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Phone</p>
              <p class="text-sm font-mono">{{ employee.phone }}</p>
            </div>
            <div>
              <p class="text-xs text-slate-500 mb-1">Performance Score</p>
              <div class="flex items-center gap-2">
                <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div class="h-full bg-emerald-500" :style="{ width: `${employee.performance}%` }"></div>
                </div>
                <span class="font-semibold text-sm" :class="performanceColor(employee.performance)">
                  {{ employee.performance }}%
                </span>
              </div>
            </div>
          </div>

          <template #footer>
            <div class="flex gap-2">
              <Button variant="secondary" size="sm" fullWidth>
                View Details
              </Button>
              <Button variant="secondary" size="sm" fullWidth>
                Edit
              </Button>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Add Employee Modal -->
    <Modal v-model="showAddModal" title="Add New Employee" size="md">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Name</label>
          <input
            v-model="newEmployee.name"
            type="text"
            placeholder="e.g., Rajesh Kumar"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Role</label>
          <select
            v-model="newEmployee.role"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          >
            <option>Sales Staff</option>
            <option>Supervisor</option>
            <option>Inventory Manager</option>
            <option>Store Manager</option>
            <option>Billing Staff</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
          <input
            v-model="newEmployee.email"
            type="email"
            placeholder="name@sonik.com"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Phone</label>
          <input
            v-model="newEmployee.phone"
            type="tel"
            placeholder="10-digit number"
            class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
          />
        </div>
      </div>

      <template #footer>
        <Button variant="secondary" @click="showAddModal = false">
          Cancel
        </Button>
        <Button variant="primary" @click="handleAddEmployee">
          Add Employee
        </Button>
      </template>
    </Modal>
  </MainLayout>
</template>
