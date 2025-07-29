<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import type { Timer } from '@/types'
import { useListenerFn } from '@/lib'
import { timerToString } from '@/utils'

const props = defineProps<{
  timer: Timer
}>()

const displayedTime = ref('00:00')

function updateDisplay() {
  if (props.timer) {
    displayedTime.value = timerToString(props.timer)
  }
}

// Initial update
onMounted(updateDisplay)

// Update when the timer object itself changes or its properties that timerToString depends on might change
// (e.g. if the timer instance is replaced)
watch(() => props.timer, updateDisplay, { deep: true })

// Update on every clock tick for continuous time change
useListenerFn('clock-tick', updateDisplay)
</script>

<template>
  <span>{{ displayedTime }}</span>
</template>
