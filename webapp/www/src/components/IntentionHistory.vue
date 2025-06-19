<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { usePucotiStore } from '@/stores/counter'
import { fmtSeconds } from '@/utils'
import Button from './Button.vue'
import type { IntentionHistoryItem } from '@/types'

const store = usePucotiStore()

// Reactive state for editing
const editingIndex = ref<number | null>(null)
const editingValue = ref<string>('')

// Computed property for completed intentions with duration
const completedIntentions = computed(() => {
  let history = store.intentionHistory.filter(
    (item) => item.intention != '' && item.end !== undefined,
  )
  return history
    .map((item: IntentionHistoryItem, index: number) => ({
      ...item,
      index,
      duration: item.end ? item.end - item.start : 0,
      isCompleted: !!item.end,
    }))
    .reverse() // Show most recent first
})

// Edit functionality
const startEditing = (index: number, currentText: string) => {
  editingIndex.value = index
  editingValue.value = currentText
  nextTick(() => {
    const input = document.querySelector(`input[data-edit-index="${index}"]`) as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}

const saveEdit = (originalIndex: number) => {
  if (editingValue.value.trim()) {
    store.updateHistoricalIntention(originalIndex, editingValue.value.trim())
  }
  cancelEdit()
}

const cancelEdit = () => {
  editingIndex.value = null
  editingValue.value = ''
}

const handleEditKeydown = (event: KeyboardEvent, originalIndex: number) => {
  event.stopPropagation()

  if (event.key === 'Enter') {
    event.preventDefault()
    saveEdit(originalIndex)
  } else if (event.key === 'Escape') {
    event.preventDefault()
    cancelEdit()
  }
}

// Continue functionality
const continueFromHistory = (intention: string) => {
  store.continueFromHistory(intention)
}

// Format duration helper
const formatDuration = (milliseconds: number) => {
  const parts = fmtSeconds(milliseconds)
  return parts.join(':')
}
</script>

<template>
  <div class="history-section">
    <h2 class="history-title">History</h2>

    <div v-if="completedIntentions.length === 0" class="empty-state">
      No intentions completed yet. Start working on something to see your history here.
    </div>

    <div v-else class="history-list">
      <div
        v-for="item in completedIntentions"
        :key="`${item.index}-${item.start}`"
        class="history-item"
      >
        <div class="history-item-content">
          <div class="intention-text">
            <input
              v-if="editingIndex === item.index"
              :data-edit-index="item.index"
              v-model="editingValue"
              class="intention-edit-input"
              @keydown="handleEditKeydown($event, item.index)"
              @blur="cancelEdit"
              @click.stop
            />
            <span v-else class="intention-display">{{ item.intention }}</span>
          </div>

          <div class="history-actions">
            <button
              v-if="editingIndex !== item.index"
              class="edit-button"
              title="Edit intention"
              @click="startEditing(item.index, item.intention)"
            >
              ✏️
            </button>

            <div class="duration">{{ formatDuration(item.duration) }}</div>

            <Button label="Continue" @click="continueFromHistory(item.intention)" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.history-section {
  margin-top: clamp(2em, 3vw, 100vw);
}

.history-title {
  color: var(--color-acid);
  font-family: var(--font-display);
  font-size: clamp(1.5em, 2.5vw, 100vw);
  margin-bottom: 0.5em;
}

.empty-state {
  color: color-mix(in oklab, var(--color-light) 80%, transparent);
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  background-color: color-mix(in oklab, var(--color-light) 5%, transparent);
  border: 1px solid color-mix(in oklab, var(--color-light) 15%, transparent);
  border-radius: 8px;
  margin-bottom: 0.5em;
  padding: 1em;
  transition: background-color 0.2s ease;
}

.history-item:hover {
  background-color: color-mix(in oklab, var(--color-light) 8%, transparent);
}

.history-item-content {
  display: flex;
  align-items: center;
  gap: 1em;
}

.intention-text {
  flex: 1;
  min-width: 0; /* Allow text to shrink */
}

.intention-display {
  color: var(--color-light);
  word-break: break-word;
  line-height: 1.4;
}

.intention-edit-input {
  width: 100%;
  background: color-mix(in oklab, var(--color-light) 10%, transparent);
  border: 1px solid var(--color-acid);
  border-radius: 4px;
  color: var(--color-light);
  padding: 0.25em 0.5em;
  font-size: inherit;
  outline: none;
}

.intention-edit-input:focus {
  border-color: var(--color-acid);
  box-shadow: 0 0 0 2px color-mix(in oklab, var(--color-acid) 20%, transparent);
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 0.75em;
  flex-shrink: 0;
}

.edit-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25em;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  font-size: 1em;
}

.edit-button:hover {
  background-color: color-mix(in oklab, var(--color-light) 15%, transparent);
}

.duration {
  color: var(--color-acid);
  font-family: var(--font-mono, monospace);
  font-size: 0.9em;
  min-width: 4em;
  text-align: right;
}

/* Scrollbar styling for webkit browsers */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: color-mix(in oklab, var(--color-light) 5%, transparent);
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb {
  background: color-mix(in oklab, var(--color-light) 20%, transparent);
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: color-mix(in oklab, var(--color-light) 30%, transparent);
}
</style>
