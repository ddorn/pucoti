<script lang="ts" setup>
import type { Timer } from '@/types'
import { useListenerFn } from '@/lib'
import { timerToMs, timerToString } from '@/utils'
import { onMounted, ref } from 'vue'

const props = defineProps<{
  timer: Timer
  color: string
  size?: string
}>()

const displayTime = ref('00:00')
const color = ref('')

function handleClockTick() {
  displayTime.value = timerToString(props.timer)
  color.value = timerToMs(props.timer) < 0 ? 'var(--timer-negative)' : props.color
}

onMounted(handleClockTick)
useListenerFn('clock-tick', handleClockTick)
</script>

<template>
  <span
    v-bind="$attrs"
    :style="{ color: color, fontSize: props.size ?? 'clamp(2em, 12vw, 100em)' }"
    class="font-display"
    >{{ displayTime }}</span
  >
</template>
