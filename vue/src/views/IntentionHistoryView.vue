<template>
    <h1 class="page-title">Intention history</h1>

    <table>
        <tr>
            <th>Span</th>
            <th>Intention</th>
            <th>Started</th>
        </tr>
        <tr v-for="intention in data" :key="intention.id">
            <td>{{ intention.span }}</td>
            <td>{{ intention.intention }}</td>
            <td>{{ intention.started }}</td>
        </tr>
    </table>
</template>


<script setup lang="ts">
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
}

window.addEventListener("keydown", handleKeybindings);
onUnmounted(() => {
    window.removeEventListener("keydown", handleKeybindings);
});

</script>

<style scoped>
    tr {
        color: white;
    }
</style>
