<template>
  <div>
    <h1 class="page-title">PUCOTI Bindings</h1>

    <table class="help-bindings">
      <tr v-for="binding in bindings" :key="binding.key" class="help-binding--wrapper" >
        <td class="help-binding--key"><kbd>{{ binding.key }}</kbd></td>
        <td class="help-binding--def">{{ binding.def }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup lang="ts">


const bindings = [
  { key: "j k", def: "-/+ 1 minute" },
  { key: "J K", def: "-/+ 5 minutes" },
  { key: "0-9", def: "set duration" },
  { key: "shift 0-9", def: "set duration *10min" },
  { key: "r", def: "reset timer" },
  { key: "Return", def: "enter intention" },
  { key: "i", def: "toggle intention history" },
  // { key: "T", def: "toggle total time" },
  { key: "h", def: "toggle this help" },
  { key: "s", def: "toggle settings" },
  { key: "Escape", def: "go back"},
];



</script>
