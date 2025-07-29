<script setup lang="ts">
import { ref } from 'vue'
import Modal from './Modal.vue'
import Button from './Button.vue'
import { usePucotiStore } from '@/stores/counter'

interface Props {
  show: boolean
}

interface Emits {
  (e: 'close'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const store = usePucotiStore()

const roomName = ref(store.social.room || '')
const username = ref(store.social.username || '')
const isLoading = ref(false)
const error = ref('')

const joinRoom = async () => {
  if (!roomName.value.trim() || !username.value.trim()) {
    error.value = 'Please fill in both room name and username'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    store.joinRoom(roomName.value, username.value)
    await store.updateServer(true)
    emit('close')
  } catch (err) {
    error.value = 'Failed to join room. Please check the room name and try again.'
    console.error('Error joining room:', err)
  } finally {
    isLoading.value = false
  }
}

const handleClose = () => {
  if (!isLoading.value) {
    emit('close')
  }
}
</script>

<template>
  <Modal :show="show" title="Join Room" @close="handleClose">
    <form @submit.prevent="joinRoom" class="space-y-4">
      <div>
        <label for="join-room-name" class="block text-sm font-medium text-light/80 mb-2">
          Room Name
        </label>
        <input
          id="join-room-name"
          v-model="roomName"
          type="text"
          placeholder="room-name-to-join"
          class="w-full bg-light/10 border border-light/20 rounded px-3 py-2 text-light placeholder:text-light/40 focus:outline-none focus:ring-2 focus:ring-acid focus:border-transparent"
          :disabled="isLoading"
          required
        />
        <p class="text-xs text-light/60 mt-1">
          Enter the room name shared by your friend or colleague.
        </p>
      </div>

      <div>
        <label for="join-username" class="block text-sm font-medium text-light/80 mb-2">
          Your Username
        </label>
        <input
          id="join-username"
          v-model="username"
          type="text"
          placeholder="Your name"
          class="w-full bg-light/10 border border-light/20 rounded px-3 py-2 text-light placeholder:text-light/40 focus:outline-none focus:ring-2 focus:ring-acid focus:border-transparent"
          :disabled="isLoading"
          required
        />
        <p class="text-xs text-light/60 mt-1">
          This name will be visible to others in the room.
        </p>
      </div>

      <div v-if="error" class="text-red-400 text-sm">
        {{ error }}
      </div>

      <div class="flex gap-3 pt-4">
        <Button
          label="Cancel"
          @click="handleClose"
          :disabled="isLoading"
          outline
          class="flex-1"
        />
        <Button
          label="Join Room"
          type="submit"
          :disabled="isLoading || !roomName.trim() || !username.trim()"
          class="flex-1"
        />
      </div>
    </form>

    <div v-if="isLoading" class="absolute inset-0 bg-dark/80 flex items-center justify-center rounded-lg">
      <div class="text-light">Joining room...</div>
    </div>
  </Modal>
</template>
