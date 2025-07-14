<script setup lang="ts">
import { computed } from 'vue'
import type { Timer } from '@/types'
import ReactiveTimer from './ReactiveTimer.vue'
import { timerToMs } from '@/utils'

const props = defineProps<{
  timer: Timer
}>()

const displayColor = computed(() => {
  if (timerToMs(props.timer) < 0) {
    return 'var(--timer-negative)'
  }
  return props.timer.color || 'var(--color-light)' // Fallback color
})
</script>

<template>
  <div class="small-timer flex items-center justify-between rounded-md bg-light/5 p-2">
    <span class="name text-light/70">{{ timer.name }}</span>
    <span class="value font-mono text-lg" :style="{ color: displayColor }">
      <ReactiveTimer :timer="props.timer" />
    </span>
  </div>
</template>
