<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import type { Timer } from '@/types'

const props = defineProps<{
  timer: Timer
}>()

const now = ref(Date.now())

let intervalId: number | undefined

onMounted(() => {
  intervalId = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (intervalId) {
    window.clearInterval(intervalId)
  }
})

const elapsedTime = computed(() => {
  if (props.timer.increasing) {
    return now.value - props.timer.zeroAt
  } else {
    const remaining = props.timer.zeroAt - now.value
    return remaining > 0 ? remaining : 0
  }
})

const formattedTime = computed(() => {
  const totalSeconds = Math.floor(elapsedTime.value / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  const pad = (num: number) => num.toString().padStart(2, '0')

  if (hours > 0) {
    return `${hours}:${pad(minutes)}:${pad(seconds)}`
  }
  return `${pad(minutes)}:${pad(seconds)}`
})
</script>

<template>
  <div class="small-timer flex items-center justify-between rounded-md bg-light/5 p-2">
    <span class="name text-light/70">{{ timer.name }}</span>
    <span class="value font-mono text-lg" :style="{ color: timer.color }">{{ formattedTime }}</span>
  </div>
</template>