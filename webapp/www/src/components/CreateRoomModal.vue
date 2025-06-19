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

const roomName = ref('')
const username = ref(store.social.username || '')
const isLoading = ref(false)
const error = ref('')

const generateRoomName = () => {
  const adjectives = ['swift', 'bright', 'calm', 'bold', 'wise', 'keen', 'pure', 'vast']
  const nouns = ['focus', 'flow', 'spark', 'wave', 'peak', 'zen', 'core', 'beam']
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
  const noun = nouns[Math.floor(Math.random() * nouns.length)]
  const num = Math.floor(Math.random() * 100)
  roomName.value = `${adj}-${noun}-${num}`
}

const createRoom = async () => {
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
    error.value = 'Failed to create room. Please try again.'
    console.error('Error creating room:', err)
  } finally {
    isLoading.value = false
  }
}

const handleClose = () => {
  if (!isLoading.value) {
    emit('close')
  }
}

// Generate initial room name
if (!roomName.value) {
  generateRoomName()
}
</script>

<template>
  <Modal :show="show" title="Create Room" @close="handleClose">
    <form @submit.prevent="createRoom" class="space-y-4">
      <div>
        <label for="room-name" class="block text-sm font-medium text-light/80 mb-2">
          Room Name
        </label>
        <div class="flex gap-2">
          <input
            id="room-name"
            v-model="roomName"
            type="text"
            placeholder="my-awesome-room"
            class="flex-1 bg-light/10 border border-light/20 rounded px-3 py-2 text-light placeholder:text-light/40 focus:outline-none focus:ring-2 focus:ring-acid focus:border-transparent"
            :disabled="isLoading"
            required
          />
          <Button
            label="🎲"
            @click="generateRoomName"
            :disabled="isLoading"
            class="px-3"
            title="Generate random room name"
          />
        </div>
        <p class="text-xs text-light/60 mt-1">
          Choose a unique name for your room. Others will use this to join.
        </p>
      </div>

      <div>
        <label for="username" class="block text-sm font-medium text-light/80 mb-2">
          Your Username
        </label>
        <input
          id="username"
          v-model="username"
          type="text"
          placeholder="Your name"
          class="w-full bg-light/10 border border-light/20 rounded px-3 py-2 text-light placeholder:text-light/40 focus:outline-none focus:ring-2 focus:ring-acid focus:border-transparent"
          :disabled="isLoading"
          required
        />
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
          label="Create Room"
          type="submit"
          :disabled="isLoading || !roomName.trim() || !username.trim()"
          class="flex-1"
        />
      </div>
    </form>

    <div v-if="isLoading" class="absolute inset-0 bg-dark/80 flex items-center justify-center rounded-lg">
      <div class="text-light">Creating room...</div>
    </div>
  </Modal>
</template>