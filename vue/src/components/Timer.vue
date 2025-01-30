<template>
    <div class="timer-container scale-max-size">
        <span class="timer-value">{{ time }}</span>
    </div>
</template>

<script setup lang="ts">
import { fmtSeconds } from '@/lib';
import type { Timer } from '@/types';
import { computed } from 'vue';

//   if (timer.value < 0) {
//     element.style.color = "var(--timer-negative)";
//   } else {
//     element.style.color = timer.color;
//   }

const props = defineProps<{
    timer: Timer;
}>();

const time = computed(() => fmtSeconds(props.timer.value).join(":"));


</script>
