<script setup lang="ts">
import { usePucotiStore } from '@/stores/counter'
import SmallTimer from './SmallTimer.vue'

const store = usePucotiStore()
</script>

<template>
  <div class="timers-list-container">
    <h2 class="text-acid font-display text-[clamp(2em,3vw,100vw)]">Timers</h2>
    <div class="timers-list space-y-2">
      <SmallTimer
        v-for="timerKey in store.secondaryTimers"
        :key="timerKey"
        :timer="store.timers[timerKey]"
      />
    </div>
  </div>
</template>
<style scoped>
.timers-list-container {
  margin-top: clamp(2em, 3vw, 100vw);
}

.history-title {
  color: var(--color-acid);
  font-family: var(--font-display);
  font-size: clamp(1.5em, 2.5vw, 100vw);
  margin-bottom: 0.5em;
}
</style>
