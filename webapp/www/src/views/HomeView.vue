<script setup lang="ts">
import { ref, nextTick, useTemplateRef } from 'vue'
import Button from '@/components/Button.vue'
import AppLogo from '@/components/AppLogo.vue'
import Timer from '@/components/Timer.vue'
import IntentionHistory from '@/components/IntentionHistory.vue'
import { usePucotiStore } from '@/stores/counter'
import { RouterLink } from 'vue-router'
import router from '@/router'
import { humanTimeToMs, MINUTE } from '@/utils'
import { useListenerFn } from '@/lib'

const store = usePucotiStore()

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
const updateTimer = (e) => {
  try {
    let newTime = humanTimeToMs(e.target.value)
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
  $intention.value = store.intention // Revert to the current store value
  $intention.value.blur() // blur to take focus away from the input
  isEditingIntention.value = false
}

function onIntentionInput(e: KeyboardEvent) {
  e.stopPropagation()

  const target = e.target as HTMLInputElement

  if (e.key === 'Enter') {
    store.setIntention(target.value)
    stopEditingIntention()
  } else if (e.key === 'Escape') {
    target.value = store.intention
    stopEditingIntention()
  }
}

useListenerFn('keydown', (e: KeyboardEvent) => {
  // If we are editing either intention or time, global shortcuts are disabled
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
      // Key corresponding to 0-9 -> set to that minute
      // + if shift is pressed, set to 10*key
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
</script>

<template>
  <main class="bg-dark grow p-[2vw_2vw_0_1vw]">
    <div class="intention-area">
      <div v-if="!isEditingIntention" class="intention-placeholder" @click="startEditingIntention">
        {{ store.intention || 'Enter your intention' }}
      </div>
      <input
        v-else
        id="intention"
        type="text"
        ref="intention"
        :value="store.intention"
        placeholder="Enter your intention"
        @keydown.stop="onIntentionInput"
        @blur="stopEditingIntention"
      />
    </div>
    <div class="main-layout">
      <div class="timer-layout">
        <div class="action-item-list">
          <Button label="-1 min" shortcut="j" @click="store.addTime(-MINUTE)" />
          <Button label="-5 min" shortcut="J" @click="store.addTime(-5 * MINUTE)" />
        </div>
        <div v-if="!isEditingTime" class="main-timer-container" @click="startEditingTime">
          <Timer :timer="store.timers.main" color="var(--color-light)" />
        </div>
        <input
          v-else
          ref="timeInputRef"
          v-model="newTimeValue"
          placeholder="1h 10m"
          class="timer-input"
          @keyup.escape="stopEditingTime"
          @keyup.enter="updateTimer"
          @blur="stopEditingTime"
        />
        <div class="action-item-list">
          <Button label="+1 min" shortcut="k" @click="store.addTime(MINUTE)" />
          <Button label="+5 min" shortcut="K" @click="store.addTime(5 * MINUTE)" />
        </div>
      </div>
      <div class="footer-action-items">
        <Button label="Create room" shortcut="C" outline />
        <Button label="Enter room" shortcut="E" outline />
      </div>
      <div class="below">
        <IntentionHistory />
      </div>
    </div>
  </main>
</template>

<style scoped>
.purpose {
  margin-top: clamp(1em, 1.5vw, 100vw);
  color: var(--color-acid);
  font-family: var(--font-display);
  font-size: clamp(1em, 2vw, 100vw);
  display: block;
  text-align: center;
}

.main-timer-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: color-mix(in oklab, var(--color-light) 10%, transparent);
  cursor: pointer;
}

.main-layout {
  margin-top: clamp(1em, 1.5vw, 100vw);
  display: grid;
  grid-template-areas:
    'action-left timer action-right'
    '.    timer    .'
    '.    footer   .'
    '.    below    .';
  grid-template-columns: auto 1fr auto;
  column-gap: 1vw;
}

.timer-layout {
  display: contents;
}

.action-item-list:first-of-type {
  grid-area: action-left;
}

.main-timer-container {
  grid-area: timer;
}

.below {
  grid-area: below;
}

.action-item-list:last-of-type {
  grid-area: action-right;
}

.action-item-list {
  display: flex;
  flex-direction: column;
}

.action-item-list > * + * {
  margin-top: 1vw;
}

.footer-action-items {
  grid-area: footer;
  display: flex;
  margin-top: clamp(1em, 1.5vw, 100vw);
}

.footer-action-items > * + * {
  margin-left: 1vw;
}

.timer-input {
  font-family: var(--font-display);
  font-size: clamp(4em, 12vw, 100vw);
  color: var(--color-light);
  text-align: center;
  width: 100%;
  outline: none;
}

.timer-input::placeholder {
  color: color-mix(in srgb, var(--color-light) 50%, transparent);
}

.intention-area {
  margin-top: clamp(1em, 1.5vw, 100vw);
  text-align: center;
  /* Center the content within the div */
}

.intention-placeholder {
  display: inline-block;
  /* Allows padding and margin */
  color: var(--color-acid);
  background-color: color-mix(in oklab, var(--color-light) 10%, transparent);
  font-family: var(--font-display);
  font-size: 3em;
  /* Match input font size */
  padding: 0.1em 0.5em;
  /* Add some padding to make it look like an input */
  cursor: text;
  /* Indicate it's clickable/editable */
  min-width: 300px;
  /* Ensure a minimum width */
}

#intention {
  display: inline-block;
  /* Use inline-block for consistent centering */
  color: var(--color-acid);
  background-color: color-mix(in oklab, var(--color-light) 10%, transparent);
  font-family: var(--font-display);
  font-size: 3em;
  text-align: center;
  border: none;
  /* Remove default input border */
  outline: none;
  /* Remove default input outline */
  padding: 0.1em 0.5em;
  /* Match placeholder padding */
  min-width: 300px;
  /* Match placeholder width */
}

#intention::placeholder {
  color: color-mix(in oklab, var(--color-acid) 40%, transparent);
}
</style>
