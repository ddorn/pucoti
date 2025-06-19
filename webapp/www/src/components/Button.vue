<script lang="ts" setup>
defineProps<{
  shortcut?: string
  label: string
  outline?: boolean
}>()
</script>
<template>
  <button
    v-bind="$attrs"
    class="inline-flex items-center justify-center gap-x-[1vw] text-light"
    :class="
      outline
        ? 'border-none bg-darker p-[0.3em_0.8em]'
        : 'button-gradient border border-light/20 p-[0.5vw_0.8vw]'
    "
  >
    <span class="text-[1.2em]">{{ label }}</span>
    <kbd
      v-if="shortcut"
      class="flex h-[clamp(1.2em,2vw,5em)] w-[clamp(1.2em,2vw,5em)] items-center justify-center border border-light/10 bg-dark font-mono"
      >{{ shortcut }}</kbd
    >
  </button>
</template>

<style scoped>
.button-gradient {
  background-image: linear-gradient(
    to top,
    transparent 0%,
    color-mix(in oklab, var(--color-light) 15%, var(--color-dark)) 90%
  );
}
</style>
