<script setup lang="ts">
import { ref, nextTick, useTemplateRef, computed, onMounted, onUnmounted } from 'vue'
import Button from '@/components/Button.vue'
import Timer from '@/components/Timer.vue'
import IntentionHistory from '@/components/IntentionHistory.vue'
import { usePucotiStore } from '@/stores/counter'
import router from '@/router'
import { humanTimeToMs, MINUTE, timerToString } from '@/utils'
import { useListenerFn } from '@/lib'
import TimersList from '@/components/TimersList.vue'

const store = usePucotiStore()

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
    let newTime = humanTimeToMs(target.value)
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
useListenerFn('keydown', (e: KeyboardEvent) => {
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
})

const timeOnPurpose = computed(() => {
  return timerToString(store.timers.main)
})
</script>

<template>
  <div v-if="isMiniView" class="mini-view bg-dark">
    <div class="text-[1.8em] font-display text-acid" @click="startEditingIntention">
      {{ store.intention || 'Enter your intention' }}
    </div>
    <div class="main-timer-container flex-grow">
      <Timer :timer="store.timers.main" color="var(--color-light)" />
    </div>
    <div class="time-on-purpose text-center font-display text-acid text-[2em]">
      {{ timeOnPurpose }}
    </div>
  </div>

  <main v-else class="bg-dark grow p-[2vw_2vw_0_1vw]">
    <div class="mt-[clamp(1em,1.5vw,100vw)] text-center">
      <div
        v-if="!isEditingIntention"
        class="inline-block min-w-[300px] cursor-text bg-light/10 p-[0.1em_0.5em] text-[3em] font-display text-acid"
        @click="startEditingIntention"
      >
        {{ store.intention || 'Enter your intention' }}
      </div>
      <input
        v-else
        id="intention"
        ref="intention"
        type="text"
        :value="store.intention"
        placeholder="Enter your intention"
        class="inline-block min-w-[300px] border-none bg-light/10 p-[0.1em_0.5em] text-center text-[3em] font-display text-acid outline-none placeholder:text-acid/40"
        @keydown.stop="onIntentionInput"
        @blur="stopEditingIntention"
      />
    </div>
    <div class="main-layout mt-[clamp(1em,1.5vw,100vw)] grid gap-x-[1vw]">
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
      <div class="footer-action-items mt-[clamp(1em,1.5vw,100vw)] flex space-x-[1vw]">
        <Button label="Create room" shortcut="C" outline />
        <Button label="Enter room" shortcut="E" outline />
      </div>
      <div class="below">
        <TimersList />
        <IntentionHistory />
      </div>
    </div>
  </main>
</template>

<style scoped>
.mini-view {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 1em;
  text-align: center;
  gap: 1em;
}

.mini-view .main-timer-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 100px;
}

.main-layout {
  grid-template-areas:
    'action-left timer action-right'
    '.    timer    .'
    '.    footer   .'
    '.    below    .';
  grid-template-columns: auto 1fr auto;
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
</style>
