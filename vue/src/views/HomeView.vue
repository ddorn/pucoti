<template>
  <div ref="home" style="overflow: hidden">

    <input id="intention" type="text" ref="intention" placeholder="Intention?" class="scale-max-size" style="height: 20vh" @keydown="intentionKeydown"/>

    <Timer id="main-timer" :timer="store.timers.main"/>

    <footer class="timer-row" :style="{ gridTemplateColumns: `repeat(${store.secondaryTimers.length}, 1fr)` }">
      <Timer v-for="timer in store.secondaryTimers" :timer="store.timers[timer]" :key="timer"/>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, useTemplateRef } from 'vue';
import { usePucotiStore } from '@/stores/pucotiStore';
import { scaleMaxSize, scaleMaxSizeAll } from '@/lib';
import router from '@/router/router';
import Timer from '@/components/Timer.vue';
import { MINUTE } from '@/timeUtils';

const store = usePucotiStore();
const $intention = useTemplateRef<HTMLElement>("intention");

function redraw() {
  scaleMaxSizeAll();
}

const redrawHandle = setInterval(redraw, 1000);

onMounted(() => {
  redraw();
});



function handleKeybindings(e: KeyboardEvent) {
  switch (e.key) {
    case "j":
      store.addTime(-MINUTE)
      break;
    case "J":
      store.addTime(-5 * MINUTE)
      break;
    case "k":
      store.addTime(MINUTE)
      break;
    case "K":
      store.addTime(5 * MINUTE)
      break;
    case "r":
      store.setRingIn(store.countdownDuration);
      break;
    case "h":
      router.push("/help");
      break;
    case "s":
      router.push("/settings");
      break;
    case "p":
      router.push("/intentionhistory");
      break;
    case "Enter":
      $intention.value!.focus();
      break;
    default:
      // Key corresponding to 0-9 -> set to that minute
      // + if shift is pressed, set to 10*key
      if (e.code.startsWith("Digit")) {
        let digit = parseInt(e.code[5]);
        if (e.shiftKey) {
          digit *= 10;
        }
        store.setRingIn(digit * MINUTE);
        store.countdownDuration = digit * MINUTE;
      } else {
        return;
      }
  }

  e.preventDefault();
  redraw();
};

document.addEventListener("keydown", handleKeybindings);
onUnmounted(() => {
  document.removeEventListener("keydown", handleKeybindings);
  clearInterval(redrawHandle);
});

function intentionKeydown(e: KeyboardEvent) {
  e.stopPropagation();
  if (e.key === "Enter") {
    store.setIntention(e.target.value);
    e.target.blur();
  }
  window.requestAnimationFrame(() => scaleMaxSize(e.target));
};
</script>
