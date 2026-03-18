<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  rows: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
  emptyMessage: {
    type: String,
    default: 'No data found.',
  },
  striped: Boolean,
  hoverable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['row-click', 'sort'])

const skeletonRows = computed(() => Array(5).fill(null))

const handleRowClick = (row) => {
  emit('row-click', row)
}

const handleSort = (column) => {
  if (column.sortable) {
    // Simple toggle between asc and desc
    const direction = 'asc'
    emit('sort', { key: column.key, direction })
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
    <!-- Loading state -->
    <div v-if="loading" class="divide-y divide-slate-100">
      <div v-for="i in 5" :key="i" class="px-4 py-3.5 flex gap-4">
        <div class="h-4 bg-slate-100 rounded animate-pulse flex-1"></div>
        <div class="h-4 bg-slate-100 rounded animate-pulse w-24"></div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="rows.length === 0" class="text-center py-16">
      <svg class="w-12 h-12 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p class="text-sm text-slate-400">{{ emptyMessage }}</p>
    </div>

    <!-- Table -->
    <table v-else class="w-full text-sm">
      <thead class="bg-slate-50 border-b border-slate-200">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            class="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide"
            :style="{ width: column.width, textAlign: column.align || 'left' }"
          >
            <div class="flex items-center gap-2 cursor-pointer" @click="handleSort(column)">
              {{ column.label }}
              <svg v-if="column.sortable" class="w-3 h-3 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h5a1 1 0 000-2H3zM3 11a1 1 0 100 2h4a1 1 0 100-2H3zM15 8a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L15 13.586V8z" />
              </svg>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(row, rowIndex) in rows"
          :key="rowIndex"
          class="border-b border-slate-100 last:border-0 transition-colors"
          :class="{
            'hover:bg-slate-50': hoverable,
            'bg-slate-50/50': striped && rowIndex % 2 === 1,
            'cursor-pointer': true,
          }"
          @click="handleRowClick(row)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            class="px-4 py-3.5 text-slate-700"
            :style="{ textAlign: column.align || 'left' }"
          >
            <slot :name="column.key" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
