<script setup lang="ts">
interface Props {
  show: boolean
  title?: string
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<template>
  <Teleport to="body">
    <div
      v-if="show"
      class="modal-overlay fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div
        class="modal-content relative max-h-[90vh] w-full max-w-md overflow-auto rounded-lg bg-dark p-6 shadow-2xl"
        @click.stop
      >
        <button
          class="absolute right-4 top-4 text-light/60 hover:text-light"
          @click="$emit('close')"
        >
          ✕
        </button>
        
        <h2 v-if="title" class="mb-4 font-display text-2xl text-light">
          {{ title }}
        </h2>
        
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  animation: fadeIn 0.2s ease-out;
}

.modal-content {
  animation: slideIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>