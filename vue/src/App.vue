<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { usePucotiStore } from './stores/counter';
import { onUnmounted } from 'vue';
import { humanTimeToMs } from './lib';
import Neutralino from '@neutralinojs/lib';

let store = usePucotiStore();

store.setIntention("");

let handle = setInterval(() => {
  store.updateTimers();
}, 1000);


let audio = new Audio("/bell.mp3");

function checkTime() {
  let now = new Date().getTime();
  let timeOnCountdown = store.ringTime - now;
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
    let runTime = -humanTimeToMs(cmd.at) + store.ringTime;
    if (now > runTime) {
      if (now - cmd.lastRan > humanTimeToMs(cmd.every)) {
        cmd.lastRan = now;
        try {
          Neutralino.os.spawnProcess(cmd.cmd);
        } catch (e) {
          console.error(`Could not run command: ${cmd.cmd}`, e);
        }
      }
    } else {
      cmd.lastRan = 0;
    }
  });
}

let handle2 = setInterval(checkTime, 500);

onUnmounted(() => {
  clearInterval(handle);
  clearInterval(handle2);
});

</script>

<template>
  <RouterView />
</template>
