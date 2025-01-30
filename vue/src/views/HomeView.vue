<template>
  <div ref="home" style="overflow: hidden">
    <template ref="timer-template">
      <div class="timer-container scale-max-size">
        <span class="timer-value">000:00</span>
      </div>
    </template>

    <input type="text" ref="intention" placeholder="Intention?" class="scale-max-size" style="height: 20vh" @keydown="intentionKeydown"/>

    <Timer :timer="store.timers.main"/>

    <footer class="timer-row" :style="{ gridTemplateColumns: `repeat(${store.secondaryTimers.length}, 1fr)` }">
      <!-- TODO: CSS here -->
      <Timer v-for="timer in store.secondaryTimers" :timer="store.timers[timer]" :key="timer"/>

    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, useTemplateRef } from 'vue';
import { usePucotiStore } from '@/stores/counter';
import { MINUTE, scaleMaxSize, scaleMaxSizeAll } from '@/lib';
import router from '@/router';
import Timer from '@/components/Timer.vue';

const store = usePucotiStore();
const $intention = useTemplateRef<HTMLElement>("intention");

function redraw() {
  scaleMaxSizeAll();
}

const redrawHandle = setInterval(redraw, 1000);

onMounted(() => {
  redraw();
});



function handleKeybindings(e) {
  switch (e.key) {
    case "j":
      store.ringTime -= MINUTE;
      break;
    case "J":
      store.ringTime -= 5 * MINUTE;
      break;
    case "k":
      store.ringTime += MINUTE;
      break;
    case "K":
      store.ringTime += 5 * MINUTE;
      break;
    case "r":
      store.ringTime = new Date().getTime() + store.countdownDuration;
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
        store.ringTime = new Date().getTime() + digit * MINUTE;
        store.countdownDuration = digit * MINUTE;
      } else {
        return;
      }
  }

  e.preventDefault();
  store.updateTimers();
  redraw();
};

document.addEventListener("keydown", handleKeybindings);
onUnmounted(() => {
  document.removeEventListener("keydown", handleKeybindings);
  clearInterval(redrawHandle);
});

function intentionKeydown(e) {
  e.stopPropagation();
  if (e.key === "Enter") {
    store.setIntention(e.target.value);
    e.target.blur();
  }
  window.requestAnimationFrame(() => scaleMaxSize(e.target));
};
</script>
