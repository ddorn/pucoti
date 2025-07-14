<script setup lang="ts">
import { RouterView } from 'vue-router'
import { usePucotiStore } from './stores/counter'
import { humanTimeToMs } from './utils'
import { tickClock, useIntervalFn } from './lib'
import { onMounted } from 'vue'

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

  // Check and execute commands
  store.checkCommands()
}

useIntervalFn(tickClock, 1000)
useIntervalFn(checkTime, 500)

// Social features - periodic server updates
function updateSocialServer() {
  store.updateServer()
}

useIntervalFn(updateSocialServer, 5000) // Every 5 seconds, same as legacy app

onMounted(() => {
  store.initializeSocial()
})
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
