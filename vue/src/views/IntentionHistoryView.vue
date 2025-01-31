<template>
    <h1 class="page-title">Intention history</h1>

    <CenteredChild>
        <table v-if="data.length > 0">
            <tr class="header">
                <th>Span</th>
                <th>Intention</th>
                <th>Started</th>
            </tr>
            <tr v-for="intention in data" :key="intention.id">
                <td>{{ intention.span }}</td>
                <td>{{ intention.intention }}</td>
                <td>
                    <TimeSince :instant="intention.start" :absolute="absolute"/>
                </td>
            </tr>
        </table>
        <p v-else>No intentions yet.</p>
    </CenteredChild>
</template>


<script setup lang="ts">
import CenteredChild from '@/components/CenteredChild.vue';
import TimeSince from '@/components/TimeSince.vue';
import { tickClock } from '@/lib';
import { usePucotiStore } from '@/stores/pucotiStore';
import { fmtSeconds, fmtTime } from '@/timeUtils';
import { computed, onUnmounted, ref } from 'vue';


const store = usePucotiStore();
const absolute = ref(false);

const data = computed(() => {
    const now = Date.now();
    return store.intentionHistory.map((intention, idx) => {
        return {
            ...intention,
            id: idx,
            span: fmtSeconds((intention.end || now) - intention.start).join(":"),
            started: fmtTime(new Date(intention.start), absolute.value),
        }
    }).filter((intention) => {
        return intention.intention !== "";
    });
});


function handleKeybindings(e: KeyboardEvent) {
    switch (e.key) {
        case "l":
            absolute.value = !absolute.value;
            break;
        default:
            return;
    }
    e.preventDefault();
    tickClock();
}

window.addEventListener("keydown", handleKeybindings);
onUnmounted(() => {
    window.removeEventListener("keydown", handleKeybindings);
});

</script>

<style scoped>
    th, td {
        color: var(--purpose);
    }
    th:first-child, td:first-child {
        color: var(--total-time)
    }
    th:last-child, td:last-child {
        color: var(--timer)
    }

</style>
