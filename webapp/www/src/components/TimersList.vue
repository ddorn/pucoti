<script setup lang="ts">
import { computed } from 'vue'
import { usePucotiStore } from '@/stores/counter'
import SmallTimer from './SmallTimer.vue'
import Button from './Button.vue'

const store = usePucotiStore()

const friendsWithTimers = computed(() => {
  if (store.friendActivity.length <= 1) {
    return []
  }
  
  return store.friendActivity.map(friend => {
    const now = Date.now()
    const remaining = friend.timer_end - now
    const totalTime = now - friend.start
    const purposeTime = friend.purpose_start ? now - friend.purpose_start : 0
    
    return {
      ...friend,
      remaining,
      totalTime,
      purposeTime,
      isTimerUp: remaining <= 0,
      timer: {
        zeroAt: friend.timer_end,
        increasing: false,
        name: `${friend.username}${friend.username === store.social.username ? ' (you)' : ''}`,
        color: remaining <= 0 ? 'var(--color-red)' : 'var(--color-light)'
      }
    }
  })
})

const formatDuration = (ms: number): string => {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}

const leaveRoom = () => {
  store.leaveRoom()
}
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

    <!-- Social Room Section -->
    <div
      v-if="store.social.room && store.social.username"
      class="social-section mt-6 pt-4 border-t border-light/10 transition-opacity"
      :class="{ 'opacity-50': store.serverOffline }"
    >
      <div class="room-header flex items-center justify-between mb-3">
        <div>
          <h3 class="text-light font-display text-lg">
            Room: <span class="text-acid">{{ store.social.room }}</span>
          </h3>
          <div class="text-xs text-light/60">
            {{ store.friendActivity.length }} {{ store.friendActivity.length === 1 ? 'person' : 'people' }} online
          </div>
        </div>
        <Button
          label="Leave"
          @click="leaveRoom"
          outline
          class="text-xs px-2 py-1"
          :disabled="store.serverOffline"
        />
      </div>

      <!-- Server Offline Notice -->
      <div v-if="store.serverOffline" class="server-offline-notice bg-red-900/50 border border-red-500/60 text-red-300 text-sm rounded-md p-3 mb-3 text-center">
        Connection to server failed. Trying to reconnect...
      </div>
      
      <div v-if="friendsWithTimers.length === 0" class="text-light/60 text-sm text-center py-4">
        <div v-if="store.friendActivity.length === 0">
          Connecting to room...
        </div>
        <div v-else>
          You're alone. Share <strong class="text-acid">{{ store.social.room }}</strong> with friends!
        </div>
      </div>
      
      <div v-else class="friends-timers space-y-3">
        <div 
          v-for="friend in friendsWithTimers" 
          :key="friend.username"
          class="friend-item bg-light/5 rounded-lg p-3"
        >
          <div class="friend-header flex items-center justify-between mb-2">
            <div class="friend-name text-light font-medium text-sm">
              {{ friend.username }}
              <span v-if="friend.username === store.social.username" class="text-acid text-xs">
                (you)
              </span>
            </div>
            <div class="friend-status text-xs" :class="friend.isTimerUp ? 'text-red-400' : 'text-green-400'">
              {{ friend.isTimerUp ? '⏰ Time up!' : '✓ Active' }}
            </div>
          </div>

          <div v-if="friend.purpose" class="friend-purpose text-acid text-sm mb-2">
            {{ friend.purpose }}
          </div>

          <div class="friend-timers">
            <SmallTimer :timer="friend.timer" />
            <div v-if="friend.purpose && friend.purpose_start" class="purpose-time text-xs text-acid mt-1">
              On purpose: {{ formatDuration(friend.purposeTime) }}
            </div>
          </div>
        </div>
      </div>
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

.friend-item {
  transition: background-color 0.2s ease;
}

.friend-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.social-section {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
