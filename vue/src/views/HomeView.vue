<template>
  <div ref="home" style="overflow: hidden">

    <input id="intention" type="text" ref="intention" placeholder="Intention?" class="scale-max-size" style="height: 20vh" @keydown="intentionKeydown"/>

    <CenteredChild id="main-timer" class="scale-max-size">
      <Timer :timer="store.timers.main"/>
    </CenteredChild>

    <footer class="timer-row" :style="{ gridTemplateColumns: `repeat(${store.secondaryTimers.length}, 1fr)` }">
      <CenteredChild v-for="timer in store.secondaryTimers" :key="timer" class="scale-max-size">
        <Timer :timer="store.timers[timer]" />
      </CenteredChild>
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
import CenteredChild from '@/components/CenteredChild.vue';

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


<style>

#main-timer {
    width: 100%;
    color: var(--timer);
    font-weight: 900;
    height: 60vh;
    padding: 1rem;
}

#intention {
    background: transparent;
    border: none;
    color: var(--purpose);
    padding: 0.5rem 1rem;
    width: 100%;
    text-align: center;
    overflow: hidden;
}

#intention::placeholder {
    color: var(--purpose);
    opacity: 0.4;
    padding: 1rem;
}

@media (width <=400px) {

    #intention,
    #intention::placeholder,
    #main-timer {
        padding: 0;
    }
}

</style>
