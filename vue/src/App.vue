<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { usePucotiStore } from './stores/counter';
import { onUnmounted } from 'vue';

let store = usePucotiStore();

let handle = setInterval(() => {
  store.updateTimers();
}, 1000);

onUnmounted(() => {
  clearInterval(handle);
});

</script>

<template>
  <nav>
    <RouterLink to="/">Home</RouterLink>
    <RouterLink to="/settings">set</RouterLink>
  </nav>

  <RouterView />
</template>
