<template>
    <div class="timer-container scale-max-size">
        <span class="timer-value" :style="{ 'color': color }">{{ shownTime }}</span>
    </div>
</template>

<script setup lang="ts">
import { timerToMs, timerToString } from '@/timeUtils';
import type { Timer } from '@/types';
import { onMounted, onUnmounted, ref } from 'vue';


const props = defineProps<{
    timer: Timer;
}>();

const shownTime = ref("ti:me")
const color = ref("");


// Listen to clock-tick, to update the time
function onClockTick() {
    shownTime.value = timerToString(props.timer);
    color.value = timerToMs(props.timer) < 0 ? "var(--timer-negative)" : props.timer.color;
}

onMounted(() => {
    onClockTick();
    document.addEventListener("clock-tick", onClockTick);
});
onUnmounted(() => {
    document.removeEventListener("clock-tick", onClockTick);
});

</script>
