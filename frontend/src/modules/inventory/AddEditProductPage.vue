<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import MainLayout from '../../layouts/MainLayout.vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import { calcMargin, marginColor } from '../../utils/currency.js'

const router = useRouter()
const route = useRoute()

const isEditMode = computed(() => !!route.params.id)

const form = ref({
  name: '',
  category: 'Dairy',
  unit: 'Piece',
  costPrice: 0,
  sellingPrice: 0,
  stock: 0,
  reorderLevel: 20,
  expiryDate: '',
  hsnCode: '',
  description: '',
})

const errors = ref({})
const isSaving = ref(false)

const margin = computed(() => {
  return calcMargin(parseFloat(form.value.costPrice) || 0, parseFloat(form.value.sellingPrice) || 0)
})

const marginLabel = computed(() => {
  const color = marginColor(margin.value)
  return `<span class="${color}">${margin.value.toFixed(1)}%</span>`
})

const profit = computed(() => {
  return (parseFloat(form.value.sellingPrice) || 0) - (parseFloat(form.value.costPrice) || 0)
})

const isFormValid = computed(() => {
  return (
    form.value.name &&
    form.value.costPrice &&
    form.value.sellingPrice > form.value.costPrice &&
    form.value.stock >= 0
  )
})

const handleSave = () => {
  errors.value = {}

  if (!form.value.name) {
    errors.value.name = 'Product name is required'
  }
  if (!form.value.costPrice) {
    errors.value.costPrice = 'Cost price is required'
  }
  if (form.value.sellingPrice <= form.value.costPrice) {
    errors.value.sellingPrice = 'Selling price must be greater than cost price'
  }

  if (Object.keys(errors.value).length > 0) return

  isSaving.value = true
  setTimeout(() => {
    isSaving.value = false
    router.push('/inventory')
  }, 1200)
}
</script>

<template>
  <MainLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <!-- Breadcrumb -->
      <div class="text-sm text-slate-500">
        <a href="/inventory" class="text-emerald-600 hover:underline">Inventory</a>
        <span class="mx-2">→</span>
        {{ isEditMode ? 'Edit Product' : 'Add Product' }}
      </div>

      <!-- Form Card -->
      <Card padding="lg">
        <form class="space-y-6" @submit.prevent="handleSave">
          <!-- Product Name -->
          <div class="col-span-2">
            <Input
              v-model="form.name"
              label="Product Name"
              placeholder="e.g., Amul Butter 100g"
              required
              :error="errors.name"
            />
          </div>

          <!-- Category & Unit -->
          <div class="grid grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Category</label>
              <select
                v-model="form.category"
                class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option>Dairy</option>
                <option>Grains</option>
                <option>Bakery</option>
                <option>Snacks</option>
                <option>Grocery</option>
                <option>Personal</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Unit</label>
              <select
                v-model="form.unit"
                class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option>Piece</option>
                <option>Kg</option>
                <option>g</option>
                <option>L</option>
                <option>ml</option>
                <option>Pack</option>
                <option>Dozen</option>
              </select>
            </div>
          </div>

          <!-- Cost & Selling Price -->
          <div class="grid grid-cols-2 gap-6">
            <div>
              <Input
                v-model.number="form.costPrice"
                label="Cost Price"
                type="number"
                prefix="₹"
                :error="errors.costPrice"
              />
            </div>
            <div>
              <Input
                v-model.number="form.sellingPrice"
                label="Selling Price"
                type="number"
                prefix="₹"
                :error="errors.sellingPrice"
              />
              <p v-if="!errors.sellingPrice" class="text-xs text-slate-500 mt-1">
                Margin: <span :class="marginColor(margin)">{{ margin.toFixed(1) }}%</span>
              </p>
            </div>
          </div>

          <!-- Stock -->
          <div class="grid grid-cols-2 gap-6">
            <Input
              v-model.number="form.stock"
              label="Initial Stock"
              type="number"
            />
            <Input
              v-model.number="form.reorderLevel"
              label="Reorder Level"
              type="number"
            />
          </div>

          <!-- Expiry & HSN -->
          <div class="grid grid-cols-2 gap-6">
            <Input
              v-model="form.expiryDate"
              label="Expiry Date"
              type="date"
            />
            <Input
              v-model="form.hsnCode"
              label="HSN Code"
              hint="Optional - required for GST invoicing"
            />
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 resize-none"
              placeholder="Product details, benefits, etc."
            ></textarea>
          </div>

          <!-- Margin Preview -->
          <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-4 flex items-center justify-between">
            <p class="text-sm text-slate-700">
              Cost <span class="font-semibold">₹{{ form.costPrice }}</span> → Sell
              <span class="font-semibold">₹{{ form.sellingPrice }}</span> → Profit
              <span class="font-semibold text-emerald-700">₹{{ profit }}</span>
            </p>
            <div class="w-32 h-2 bg-slate-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-emerald-500 transition-all duration-300"
                :style="{ width: `${Math.min(margin, 100)}%` }"
              ></div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end gap-3 border-t border-slate-100 -mx-8 -mb-8 px-8 py-6">
            <Button variant="secondary" @click="router.back()">
              Cancel
            </Button>
            <Button
              variant="primary"
              :loading="isSaving"
              :disabled="!isFormValid"
              @click="handleSave"
            >
              {{ isEditMode ? 'Update Product' : 'Save Product' }}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  </MainLayout>
</template>
