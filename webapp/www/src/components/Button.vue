<script lang="ts" setup>
const props = defineProps<{
  shortcut?: string
  label: string
  outline?: boolean
}>()
</script>
<template>
  <button v-bind="$attrs" :class="{ outline: outline }">
    <span>{{ label }}</span>
    <kbd v-if="shortcut">{{ shortcut }}</kbd>
  </button>
</template>

<style scoped>
button {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 0 1vw;

  padding: 0.5vw 0.8vw;

  color: var(--color-light);
  border: 1px solid color-mix(in oklab, var(--color-light) 20%, transparent);
  background-image: linear-gradient(to top,
      transparent 0%,
      color-mix(in oklab, var(--color-light) 15%, var(--color-dark)) 90%);
}

button.outline {
  border: none;
  background: var(--color-darker);
  padding: 0.3em 0.8em;
}

span {
  font-size: 1.2em;
}

kbd {
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: monospace;
  width: clamp(1.2em, 2vw, 5em);
  height: clamp(1.2em, 2vw, 5em);
  background-color: var(--color-dark);
  border: 1px solid color-mix(in oklab, var(--color-light) 10%, transparent);
}
</style>
