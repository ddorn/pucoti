<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { usePucotiStore } from './stores/counter'
import { humanTimeToMs } from './utils'
import { tickClock, useIntervalFn } from './lib'
import { onMounted, onUnmounted } from 'vue'

const audio = new Audio('/bell.mp3')

const store = usePucotiStore()
store.setIntention('')

function checkTime() {
  const now = Date.now()
  const timeOnCountdown = store.timers.main.zeroAt - now
  if (timeOnCountdown <= 0) {
    if (now - store.lastRung > humanTimeToMs(store.ringEvery)) {
      store.lastRung = now
      audio.currentTime = 0
      audio.play()
    }
  } else {
    store.lastRung = 0
  }
}

useIntervalFn(tickClock, 1000)
useIntervalFn(checkTime, 500)
</script>

<template>
  <!--
  <header>
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </header>
  -->

  <RouterView />
</template>
