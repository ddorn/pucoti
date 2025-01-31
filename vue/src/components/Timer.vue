<template>
    <div class="timer-container scale-max-size">
        <span class="timer-value" :style="{ 'color': color }">{{ time }}</span>
    </div>
</template>

<script setup lang="ts">
import { fmtSeconds } from '@/lib';
import type { Timer } from '@/types';
import { computed } from 'vue';


const props = defineProps<{
    timer: Timer;
}>();

const time = computed(() => fmtSeconds(props.timer.value).join(":"));
const color = computed(() => props.timer.value < 0 ? "var(--timer-negative)" : props.timer.color);

</script>
