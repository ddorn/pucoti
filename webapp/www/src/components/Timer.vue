<script lang="ts" setup>
import ReactiveTimer from './ReactiveTimer.vue'
import type { Timer } from '@/types'
import { useListenerFn } from '@/lib'
import { timerToMs } from '@/utils' // timerToString removed
import { onMounted, ref, watch } from 'vue' // watch added

const props = defineProps<{
  timer: Timer
  color: string
  size?: string
}>()

// This ref will hold the actual color to be applied,
// which could be props.color (for positive/zero time) or the negative-time color.
const colorForDisplay = ref(props.color)

function updateColorForDisplay() {
  // Use props.color as the default color for positive/zero time
  colorForDisplay.value = timerToMs(props.timer) < 0 ? 'var(--timer-negative)' : props.color
}

onMounted(updateColorForDisplay)
useListenerFn('clock-tick', updateColorForDisplay)

// Watch for changes in the base color prop or the timer itself to update the display color
watch(() => props.color, updateColorForDisplay)
watch(() => props.timer, updateColorForDisplay, { deep: true }) // deep watch on timer object
</script>

<template>
  <span
    v-bind="$attrs"
    :style="{ color: colorForDisplay, fontSize: props.size ?? 'clamp(2em, 12vw, 100em)' }"
    class="font-display"
  >
    <ReactiveTimer :timer="props.timer" />
  </span>
</template>
