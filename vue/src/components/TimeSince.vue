<template>
    <span>{{ shownTime }}</span>
</template>

<script setup lang="ts">
import { fmtTime } from '@/timeUtils';
import { onMounted, onUnmounted, ref } from 'vue';


const props = defineProps<{
    instant: number;
    absolute: boolean;
}>();

const shownTime = ref("ti:me")

// Listen to clock-tick, to update the time
function onClockTick() {
    shownTime.value = fmtTime(new Date(props.instant), props.absolute);
}

onMounted(() => {
    onClockTick();
    document.addEventListener("clock-tick", onClockTick);
});
onUnmounted(() => {
    document.removeEventListener("clock-tick", onClockTick);
});

</script>
