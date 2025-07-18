<script setup lang="ts">
import { ref, nextTick, useTemplateRef, computed } from 'vue'
import Button from '@/components/Button.vue'
import Timer from '@/components/Timer.vue'
import IntentionHistory from '@/components/IntentionHistory.vue'
import CreateRoomModal from '@/components/CreateRoomModal.vue'
import JoinRoomModal from '@/components/JoinRoomModal.vue'
import { usePucotiStore } from '@/stores/counter'
import router from '@/router'
import { humanTimeToMs, MINUTE, timerToMs } from '@/utils' // Replaced timerToString with timerToMs
import { useListenerFn } from '@/lib'
import TimersList from '@/components/TimersList.vue'
import ReactiveTimer from '@/components/ReactiveTimer.vue' // Added ReactiveTimer import

const store = usePucotiStore()

// Social modals
const showCreateRoomModal = ref(false)
const showJoinRoomModal = ref(false)

// --- Editing Time ---
const isEditingTime = ref<boolean>(false)
const newTimeValue = ref<string>('')
const timeInputRef = ref<HTMLInputElement | null>(null)
const startEditingTime = () => {
  isEditingTime.value = true
  nextTick(() => {
    if (timeInputRef.value) {
      timeInputRef.value.focus()
    }
  })
}
const updateTimer = (e: Event) => {
  const target = e.target as HTMLInputElement
  try {
    const newTime = humanTimeToMs(target.value)
    store.setRingIn(newTime)
  } catch (e) {
    console.error(e)
  }

  stopEditingTime()
}

const stopEditingTime = () => {
  isEditingTime.value = false
  newTimeValue.value = ''
}

// --- Editing Intention ---
const isEditingIntention = ref<boolean>(false)
const $intention = useTemplateRef<HTMLInputElement>('intention')

const startEditingIntention = () => {
  isEditingIntention.value = true
  nextTick(() => {
    if ($intention.value) {
      $intention.value.focus()
      $intention.value.select()
    }
  })
}

const stopEditingIntention = () => {
  if ($intention.value) {
    $intention.value.value = store.intention
    $intention.value.blur()
  }
  isEditingIntention.value = false
}

function onIntentionInput(e: KeyboardEvent) {
  e.stopPropagation()
  const target = e.target as HTMLInputElement
  if (e.key === 'Enter') {
    store.setIntention(target.value)
    stopEditingIntention()
  } else if (e.key === 'Escape') {
    stopEditingIntention()
  }
}

// --- Global Shortcuts ---
const handleKeydown = (e: KeyboardEvent) => {
  return
  if (isEditingIntention.value || isEditingTime.value) {
    return
  }

  switch (e.key) {
    case 'j':
      store.addTime(-MINUTE)
      break
    case 'J':
      store.addTime(-5 * MINUTE)
      break
    case 'k':
      store.addTime(MINUTE)
      break
    case 'K':
      store.addTime(5 * MINUTE)
      break
    case 'r':
      store.setRingIn(store.countdownDuration)
      break
    case 'h':
      router.push('/help')
      break
    case 's':
      router.push('/settings')
      break
    case 'p':
      router.push('/intentionhistory')
      break
    case 'c':
    case 'C':
      showCreateRoomModal.value = true
      break
    case 'e':
    case 'E':
      showJoinRoomModal.value = true
      break
    case 'Enter':
      startEditingIntention()
      break
    default:
      if (e.code.startsWith('Digit')) {
        let digit = parseInt(e.code[5])
        if (e.shiftKey) {
          digit *= 10
        }
        store.setRingIn(digit * MINUTE)
        store.countdownDuration = digit * MINUTE
      } else {
        return
      }
  }

  e.preventDefault()
}

useListenerFn('keydown', handleKeydown)

const onIntentionDisplayColor = computed(() => {
  return timerToMs(store.timers.onIntention) < 0 ? 'var(--timer-negative)' : 'var(--color-acid)'
})
</script>

<template>
  <div class="intention-container text-center border-4 border-red-400">
    <div
      v-if="!isEditingIntention"
      class="intention-display inline-block cursor-text bg-light/10 font-display text-acid"
      @click="startEditingIntention"
    >
      {{ store.intention || 'Intention?' }}
    </div>
    <input
      v-else
      id="intention"
      ref="intention"
      type="text"
      :value="store.intention"
      placeholder="Enter your intention"
      class="intention-input inline-block border-none bg-light/10 text-center font-display text-acid outline-none placeholder:text-acid/40"
      @keydown.stop="onIntentionInput"
      @blur="stopEditingIntention"
    />
  </div>
  <!--
  <div class="mobile-timer">
    <div class="text-center">
      <Timer
        class="leading-none"
        size="clamp(15vw, 15vw, 80vw)"
        :timer="store.timers.main"
        color="var(--color-light)"
      />
    </div>
    <div class="time-on-purpose text-center font-display">
      <span :style="{ color: onIntentionDisplayColor }">
        <ReactiveTimer :timer="store.timers.onIntention" />
      </span>
    </div>
  </div>
  -->

  <main class="grow p-[2vw_2vw_0_1vw]">
    <div class="main-layout grid gap-x-[1vw]">
      <div class="contents">
        <div class="action-item-list flex flex-col space-y-[1vw]">
          <Button label="-1 min" shortcut="j" @click="store.addTime(-MINUTE)" />
          <Button label="-5 min" shortcut="J" @click="store.addTime(-5 * MINUTE)" />
        </div>
        <div
          v-if="!isEditingTime"
          class="main-timer-container flex cursor-pointer items-center justify-center bg-light/10"
          @click="startEditingTime"
        >
          <Timer :timer="store.timers.main" color="var(--color-light)" />
        </div>
        <input
          v-else
          ref="timeInputRef"
          v-model="newTimeValue"
          placeholder="1h 10m"
          class="main-timer-container w-full bg-transparent text-center font-display text-[clamp(4em,12vw,100vw)] text-light outline-none placeholder:text-light/50"
          @keyup.escape="stopEditingTime"
          @keyup.enter="updateTimer"
          @blur="stopEditingTime"
        />
        <div class="action-item-list flex flex-col space-y-[1vw]">
          <Button label="+1 min" shortcut="k" @click="store.addTime(MINUTE)" />
          <Button label="+5 min" shortcut="K" @click="store.addTime(5 * MINUTE)" />
        </div>
      </div>
      <div
        class="footer-action-items mt-[clamp(1em,1.5vw,100vw)] flex space-x-[1vw] transition-opacity"
        :class="{ 'opacity-50': store.serverOffline }"
      >
        <Button
          label="Create room"
          shortcut="C"
          outline
          @click="showCreateRoomModal = true"
          :disabled="store.serverOffline"
        />
        <Button
          label="Enter room"
          shortcut="E"
          outline
          @click="showJoinRoomModal = true"
          :disabled="store.serverOffline"
        />
      </div>
      <div class="below">
        <TimersList />
        <IntentionHistory />
      </div>
    </div>
  </main>

  <!-- Social Modals -->
  <CreateRoomModal :show="showCreateRoomModal" @close="showCreateRoomModal = false" />
  <JoinRoomModal :show="showJoinRoomModal" @close="showJoinRoomModal = false" />
</template>

<style scoped>
/* Mobile-first styles (small screens) */
.intention-container {
  margin-top: 0;
}

.intention-display,
.intention-input {
  min-width: auto;
  padding: 0.1em 0.5em;
  font-size: 1.5em;
}

.mobile-timer {
  display: block;
}

.main-layout {
  display: none;
}

.action-item-list:first-of-type {
  grid-area: action-left;
}

.main-timer-container,
input.main-timer-container {
  grid-area: timer;
}

.below {
  grid-area: below;
}

.action-item-list:last-of-type {
  grid-area: action-right;
}

.footer-action-items {
  grid-area: footer;
}

/* Large screen styles (desktop) */
@media (min-width: 400px) and (min-height: 300px) {
  .intention-container {
    margin-top: clamp(1em, 1.5vw, 100vw);
  }

  .intention-display,
  .intention-input {
    min-width: 300px;
    padding: 0.1em 0.5em;
    font-size: 3em;
  }

  .mobile-timer {
    display: none;
  }

  .main-layout {
    display: grid;
    margin-top: clamp(1em, 1.5vw, 100vw);
    grid-template-areas:
      'action-left timer action-right'
      '.    timer    .'
      '.    footer   .'
      '.    below    .';
    grid-template-columns: auto 1fr auto;
  }
}
</style>
