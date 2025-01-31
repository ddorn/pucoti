<script setup lang="ts">
import { RouterView } from 'vue-router'
import { usePucotiStore } from './stores/pucotiStore';
import { onUnmounted } from 'vue';
import { humanTimeToMs } from './timeUtils';
import router from './router/router';
import { runCmd } from './platform';
import { tickClock } from './lib';

const store = usePucotiStore();

store.setIntention("");

const audio = new Audio("/bell.mp3");

function checkTime() {
  const now = Date.now();
  const timeOnCountdown = store.timers.main.zeroAt - now;
  if (timeOnCountdown <= 0) {
    if (now - store.lastRung > humanTimeToMs(store.ringEvery)) {
      store.lastRung = now;
      audio.currentTime = 0;
      audio.play();
    }
  } else {
    store.lastRung = 0;
  }

  // Check if any command should run
  store.commands.forEach((cmd) => {
    const runAt = store.timers.main.zeroAt - humanTimeToMs(cmd.at);
    if (now > runAt) {
      console.log(now - cmd.lastRan, humanTimeToMs(cmd.every), cmd.lastRan);
      if (now - cmd.lastRan > humanTimeToMs(cmd.every)) {
        cmd.lastRan = now;
        try {
          runCmd(cmd.cmd);
        } catch (e) {
          console.error(`Could not run command: ${cmd.cmd}`, e);
        }
      }
    } else {
      cmd.lastRan = 0;
    }
  });
}

function handleKeybindings(e: KeyboardEvent) {
  const bindings = {
    "h": "/help",
    "s": "/settings",
    "i": "/intentionhistory",
  }
  const target = bindings[e.key];
  // If already on the page, go back, otherwise go to the page
  if (target) {
    if (window.location.pathname === target) {
      router.back();
    } else {
      router.push(target);
    }
  } else if (e.key === "Escape") {
    const route = window.location.pathname;
    router.back();
    // If we are still on the same page, go to home.
    // This happens if the app has started not on the home page,
    // then there is no way to go back to the timer.
    if (route === window.location.pathname && route !== "/") {
      router.push("/");
    }
  }
}

const handle = setInterval(() => {
  // Send a signal to all timers to update
  tickClock();
}, 1000);
const handle2 = setInterval(checkTime, 500);
document.addEventListener("keydown", handleKeybindings);

onUnmounted(() => {
  clearInterval(handle);
  clearInterval(handle2);
  document.removeEventListener("keydown", handleKeybindings);
});

</script>

<template>
  <RouterView />
</template>
