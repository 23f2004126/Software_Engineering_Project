<script setup>
import { ref } from 'vue'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'

const selectedSection = ref('store')
const hasUnsavedChanges = ref(false)
const isSaving = ref(false)

// Store Profile
const storeProfile = ref({
  storeName: 'Sonik Smart Retail',
  ownerName: 'Rajesh Patel',
  phone: '9876543210',
  email: 'owner@sonik.com',
  address: '123 Market Street, Mumbai, 400001',
  city: 'Mumbai',
  state: 'Maharashtra',
  pincode: '400001',
})

// Tax Settings
const taxSettings = ref({
  gstRate: 5,
  gstNo: '27ABCDE1234F1Z5',
  panNo: 'AAAAA1111A',
  businessType: 'retail',
  invoicePrefix: 'BL-',
})

// Alert Settings
const alertSettings = ref({
  lowStockAlert: true,
  lowStockThreshold: 20,
  expiryAlert: true,
  expiryDays: 7,
  creditLimitAlert: true,
  dailyReportEmail: true,
})

// User Management
const mockUsers = [
  { id: 1, name: 'Rajesh Patel', email, role: 'Owner', status: 'active', lastLogin: '2025-06-05 14:30' },
  { id: 2, name: 'Priya Singh', email: 'priya@sonik.com', role: 'Manager', status: 'active', lastLogin: '2025-06-05 10:15' },
  { id: 3, name: 'Amit Kumar', email: 'amit@sonik.com', role: 'Staff', status: 'inactive', lastLogin: '2025-06-03 16:45' },
]

const sections = [
  { id: 'store', label: '🏢 Store Profile' },
  { id: 'tax', label: '🧾 Tax Settings' },
  { id: 'alerts', label: '🔔 Alerts' },
  { id: 'users', label: '👥 Users' },
]

const handleSave = () => {
  isSaving.value = true
  setTimeout(() => {
    isSaving.value = false
    hasUnsavedChanges.value = false
  }, 1200)
}

// Watch for changes
const markAsChanged = () => {
  hasUnsavedChanges.value = true
}
</script>

<template>
  <MainLayout>
    <!-- Unsaved Changes Bar -->
    <Transition name="slide-down">
      <div v-if="hasUnsavedChanges" class="fixed top-16 left-0 right-0 bg-amber-50 border-b border-amber-200 px-8 py-3 flex items-center justify-between z-40">
        <div class="flex items-center gap-2">
          <span class="text-xl">⚠️</span>
          <p class="text-sm text-amber-900">You have unsaved changes</p>
        </div>
        <div class="flex gap-2">
          <button class="text-sm text-amber-700 hover:text-amber-800 font-semibold">Discard</button>
          <button class="text-sm font-semibold px-4 py-2 rounded-lg bg-amber-600 text-white hover:bg-amber-700" @click="handleSave">
            Save Changes
          </button>
        </div>
      </div>
    </Transition>

    <div class="grid grid-cols-5 gap-6" :style="{ marginTop: hasUnsavedChanges ? '60px' : '0' }">
      <!-- LEFT: Navigation Menu -->
      <div class="col-span-1">
        <Card padding="none" class="sticky top-20 overflow-hidden">
          <nav class="divide-y divide-slate-200">
            <button
              v-for="section in sections"
              :key="section.id"
              class="w-full text-left px-6 py-4 text-sm font-medium transition-colors"
              :class="
                selectedSection === section.id
                  ? 'bg-emerald-50 border-l-4 border-emerald-500 text-emerald-700'
                  : 'border-l-4 border-transparent text-slate-700 hover:bg-slate-50'
              "
              @click="selectedSection = section.id"
            >
              {{ section.label }}
            </button>
          </nav>
        </Card>
      </div>

      <!-- RIGHT: Content -->
      <div class="col-span-4 space-y-6">
        <!-- Store Profile Section -->
        <div v-show="selectedSection === 'store'" class="space-y-6">
          <Card padding="lg">
            <h2 class="text-lg font-semibold text-slate-900 mb-6 pb-4 border-b border-slate-200">Store Information</h2>

            <div class="grid grid-cols-2 gap-6">
              <Input
                v-model="storeProfile.storeName"
                label="Store Name"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.ownerName"
                label="Owner Name"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.email"
                label="Email"
                type="email"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.phone"
                label="Phone"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.address"
                label="Address"
                class="col-span-2"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.city"
                label="City"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.state"
                label="State"
                @input="markAsChanged"
              />
              <Input
                v-model="storeProfile.pincode"
                label="Pincode"
                @input="markAsChanged"
              />
            </div>

            <div class="flex justify-end gap-3 mt-8 pt-6 border-t border-slate-200">
              <Button variant="secondary">Reset</Button>
              <Button variant="primary" :loading="isSaving" @click="handleSave">
                Save Profile
              </Button>
            </div>
          </Card>
        </div>

        <!-- Tax Settings Section -->
        <div v-show="selectedSection === 'tax'" class="space-y-6">
          <Card padding="lg">
            <h2 class="text-lg font-semibold text-slate-900 mb-6 pb-4 border-b border-slate-200">Tax Configuration</h2>

            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">GST Rate (%)</label>
                <input
                  v-model.number="taxSettings.gstRate"
                  type="number"
                  class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  @input="markAsChanged"
                />
              </div>
              <Input
                v-model="taxSettings.gstNo"
                label="GST Registration No"
                @input="markAsChanged"
              />
              <Input
                v-model="taxSettings.panNo"
                label="PAN Number"
                @input="markAsChanged"
              />
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Business Type</label>
                <select
                  v-model="taxSettings.businessType"
                  class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  @input="markAsChanged"
                >
                  <option value="retail">Retail</option>
                  <option value="wholesale">Wholesale</option>
                  <option value="ecommerce">E-Commerce</option>
                  <option value="service">Service</option>
                </select>
              </div>
              <Input
                v-model="taxSettings.invoicePrefix"
                label="Invoice Prefix"
                @input="markAsChanged"
              />
            </div>

            <div class="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <p class="text-sm text-blue-800">
                <span class="font-semibold">Note:</span> Tax settings will be applied to all new invoices. Past invoices will maintain their original tax configuration.
              </p>
            </div>

            <div class="flex justify-end gap-3 mt-8 pt-6 border-t border-slate-200">
              <Button variant="secondary">Reset</Button>
              <Button variant="primary" :loading="isSaving" @click="handleSave">
                Update Tax Settings
              </Button>
            </div>
          </Card>
        </div>

        <!-- Alert Settings Section -->
        <div v-show="selectedSection === 'alerts'" class="space-y-6">
          <Card padding="lg">
            <h2 class="text-lg font-semibold text-slate-900 mb-6 pb-4 border-b border-slate-200">Alert Configuration</h2>

            <div class="space-y-4">
              <!-- Low Stock Alert -->
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium text-slate-900">Low Stock Alert</p>
                  <p class="text-sm text-slate-500 mt-0.5">Get notified when stock falls below threshold</p>
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="alertSettings.lowStockAlert"
                    type="checkbox"
                    class="w-5 h-5 rounded accent-emerald-500"
                    @input="markAsChanged"
                  />
                </label>
              </div>

              <!-- Low Stock Threshold -->
              <div v-if="alertSettings.lowStockAlert" class="ml-4 p-4 rounded-lg bg-slate-50 border border-slate-200">
                <label class="block text-sm font-medium text-slate-700 mb-2">Alert Threshold (units)</label>
                <input
                  v-model.number="alertSettings.lowStockThreshold"
                  type="number"
                  class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  @input="markAsChanged"
                />
              </div>

              <!-- Expiry Alert -->
              <div class="border-t border-slate-200 pt-4 mt-4 flex items-center justify-between">
                <div>
                  <p class="font-medium text-slate-900">Expiry Alert</p>
                  <p class="text-sm text-slate-500 mt-0.5">Alert before products expire</p>
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="alertSettings.expiryAlert"
                    type="checkbox"
                    class="w-5 h-5 rounded accent-emerald-500"
                    @input="markAsChanged"
                  />
                </label>
              </div>

              <!-- Expiry Days -->
              <div v-if="alertSettings.expiryAlert" class="ml-4 p-4 rounded-lg bg-slate-50 border border-slate-200">
                <label class="block text-sm font-medium text-slate-700 mb-2">Alert Days Before Expiry</label>
                <input
                  v-model.number="alertSettings.expiryDays"
                  type="number"
                  class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  @input="markAsChanged"
                />
              </div>

              <!-- Credit Limit Alert -->
              <div class="border-t border-slate-200 pt-4 mt-4 flex items-center justify-between">
                <div>
                  <p class="font-medium text-slate-900">Credit Limit Alert</p>
                  <p class="text-sm text-slate-500 mt-0.5">Alert when customer approaches credit limit</p>
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="alertSettings.creditLimitAlert"
                    type="checkbox"
                    class="w-5 h-5 rounded accent-emerald-500"
                    @input="markAsChanged"
                  />
                </label>
              </div>

              <!-- Daily Report Email -->
              <div class="border-t border-slate-200 pt-4 mt-4 flex items-center justify-between">
                <div>
                  <p class="font-medium text-slate-900">Daily Report Email</p>
                  <p class="text-sm text-slate-500 mt-0.5">Receive summarized daily report by email</p>
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="alertSettings.dailyReportEmail"
                    type="checkbox"
                    class="w-5 h-5 rounded accent-emerald-500"
                    @input="markAsChanged"
                  />
                </label>
              </div>
            </div>

            <div class="flex justify-end gap-3 mt-8 pt-6 border-t border-slate-200">
              <Button variant="secondary">Reset to Default</Button>
              <Button variant="primary" :loading="isSaving" @click="handleSave">
                Save Alert Settings
              </Button>
            </div>
          </Card>
        </div>

        <!-- User Management Section -->
        <div v-show="selectedSection === 'users'" class="space-y-6">
          <Card>
            <template #header>
              <div class="flex items-center justify-between">
                <p class="font-semibold text-slate-900">Manage Users</p>
                <Button variant="primary" size="sm">
                  + Invite User
                </Button>
              </div>
            </template>

            <table class="w-full text-sm">
              <thead>
                <tr class="border-b border-slate-200">
                  <th class="px-6 py-3 text-left font-semibold text-slate-900">Name</th>
                  <th class="px-6 py-3 text-left font-semibold text-slate-900">Email</th>
                  <th class="px-6 py-3 text-left font-semibold text-slate-900">Role</th>
                  <th class="px-6 py-3 text-left font-semibold text-slate-900">Last Login</th>
                  <th class="px-6 py-3 text-left font-semibold text-slate-900">Status</th>
                  <th class="px-6 py-3 text-right font-semibold text-slate-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in mockUsers" :key="user.id" class="border-b border-slate-100 hover:bg-slate-50">
                  <td class="px-6 py-3 font-semibold text-slate-900">{{ user.name }}</td>
                  <td class="px-6 py-3 text-slate-600">{{ user.email }}</td>
                  <td class="px-6 py-3">
                    <span class="text-xs px-2.5 py-1 rounded-full bg-blue-100 text-blue-700 font-semibold">{{ user.role }}</span>
                  </td>
                  <td class="px-6 py-3 text-slate-600">{{ user.lastLogin }}</td>
                  <td class="px-6 py-3">
                    <span
                      class="text-xs px-2.5 py-1 rounded-full font-semibold"
                      :class="user.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700'"
                    >
                      {{ user.status }}
                    </span>
                  </td>
                  <td class="px-6 py-3 text-right">
                    <div class="flex justify-end gap-2">
                      <button class="text-sm text-slate-600 hover:text-slate-900 font-semibold">Edit</button>
                      <button class="text-sm text-red-600 hover:text-red-700 font-semibold">Remove</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </Card>

          <!-- Invite Section -->
          <Card padding="lg">
            <h3 class="font-semibold text-slate-900 mb-4">Invite New User</h3>
            <div class="space-y-4">
              <Input label="Email Address" placeholder="user@example.com" />
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <select class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400">
                  <option>Manager</option>
                  <option>Staff</option>
                  <option>Accountant</option>
                </select>
              </div>
              <Button variant="primary" fullWidth>
                Send Invite
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 300ms ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
