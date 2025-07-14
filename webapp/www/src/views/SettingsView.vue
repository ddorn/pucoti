<template>
  <div class="min-h-screen bg-dark text-light p-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <RouterLink to="/" class="inline-block text-acid hover:opacity-80 mb-4 text-sm">
          ← Back to Timer
        </RouterLink>
        <h1 class="font-display text-4xl text-light mb-2">Settings</h1>
        <p class="text-light opacity-60 text-sm">Press 's' from timer to return here</p>
      </div>
      
      <!-- Commands Section -->
      <div class="mb-12 bg-darker p-6 rounded-lg">
        <h2 class="font-display text-2xl text-light mb-2">Commands</h2>
        <p class="text-light opacity-80 mb-6">
          Configure commands to run at specific times during your timer. Use human-readable durations like "5m", "1h 30m", or negative values like "-1m" (1 minute before zero).
        </p>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Command List -->
          <div class="bg-dark p-4 rounded-md border border-white/10">
            <h3 class="text-light text-lg mb-4">Configured Commands</h3>
            
            <div v-if="commands.length === 0" class="text-light opacity-60 italic text-center py-8">
              No commands configured yet. Add one using the form →
            </div>
            
            <div v-else class="space-y-2">
              <div 
                v-for="command in commands" 
                :key="command.id"
                class="flex items-center justify-between p-4 border rounded cursor-pointer transition-all bg-darker"
                :class="{ 
                  'border-white/10 hover:border-white/20': selectedCommandId !== command.id,
                  'border-acid bg-dark': selectedCommandId === command.id 
                }"
                @click="selectCommand(command.id)"
              >
                <div class="flex-1 min-w-0">
                  <div class="text-light font-semibold mb-1">
                    At {{ command.at }}
                    <span v-if="command.every" class="text-acid font-normal text-sm ml-2">
                      (every {{ command.every }})
                    </span>
                  </div>
                  <div class="text-light opacity-70 text-sm font-mono truncate">
                    {{ command.cmd }}
                  </div>
                </div>
                <button 
                  @click.stop="deleteCommand(command.id)"
                  class="text-light opacity-50 hover:text-red-500 hover:opacity-100 text-xl px-2 py-1 ml-4 rounded transition-all hover:bg-red-500/10"
                  title="Delete command"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
          
          <!-- Command Form -->
          <div class="bg-dark p-4 rounded-md border border-white/10">
            <h3 class="text-light text-lg mb-4">
              {{ selectedCommandId ? 'Edit Command' : 'Add Command' }}
            </h3>
            
            <form @submit.prevent="saveCommand" class="space-y-6">
              <div>
                <label for="cmd-at" class="block text-light font-semibold mb-2">Trigger Time</label>
                <input 
                  id="cmd-at"
                  v-model="formData.at"
                  type="text"
                  placeholder="e.g., -1m, 0s, 5m"
                  required
                  class="w-full p-3 border border-white/20 rounded bg-darker text-light focus:border-acid focus:outline-none focus:ring-2 focus:ring-acid/10"
                />
                <small class="block mt-2 text-light opacity-70 text-sm leading-relaxed">
                  Negative values (e.g., "-1m") trigger before timer reaches zero.
                  Positive values (e.g., "5m") trigger after timer goes past zero.
                </small>
              </div>
              
              <div>
                <label for="cmd-command" class="block text-light font-semibold mb-2">Command</label>
                <textarea 
                  id="cmd-command"
                  v-model="formData.cmd"
                  placeholder="e.g., notify-send 'Timer' 'Time is up!'"
                  required
                  rows="3"
                  class="w-full p-3 border border-white/20 rounded bg-darker text-light font-mono focus:border-acid focus:outline-none focus:ring-2 focus:ring-acid/10 resize-y"
                ></textarea>
                <small class="block mt-2 text-light opacity-70 text-sm leading-relaxed">
                  Shell command to execute. Examples:<br>
                  • <code class="bg-darker px-1 py-0.5 rounded text-acid">notify-send 'Title' 'Message'</code> (Linux)<br>
                  • <code class="bg-darker px-1 py-0.5 rounded text-acid">osascript -e 'display notification "Message" with title "Title"'</code> (macOS)<br>
                  • <code class="bg-darker px-1 py-0.5 rounded text-acid">powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Message')"</code> (Windows)
                </small>
              </div>
              
              <div>
                <label for="cmd-every" class="block text-light font-semibold mb-2">Repeat Every (Optional)</label>
                <input 
                  id="cmd-every"
                  v-model="formData.every"
                  type="text"
                  placeholder="e.g., 1m, 30s"
                  class="w-full p-3 border border-white/20 rounded bg-darker text-light focus:border-acid focus:outline-none focus:ring-2 focus:ring-acid/10"
                />
                <small class="block mt-2 text-light opacity-70 text-sm">
                  If specified, the command will repeat at this interval after the initial trigger.
                </small>
              </div>
              
              <div class="flex gap-3">
                <button 
                  type="submit" 
                  class="bg-acid text-dark px-6 py-3 rounded font-bold hover:bg-light transition-colors"
                >
                  {{ selectedCommandId ? 'Update Command' : 'Add Command' }}
                </button>
                <button 
                  v-if="selectedCommandId" 
                  type="button" 
                  @click="cancelEdit"
                  class="bg-darker text-light px-6 py-3 rounded border border-white/20 hover:bg-dark hover:border-white/30 transition-all"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Test Section -->
      <div class="bg-darker p-6 rounded-lg">
        <h2 class="font-display text-2xl text-light mb-2">Test Command</h2>
        <p class="text-light opacity-80 mb-6">
          Test a command without adding it to your configuration.
        </p>
        <div class="flex gap-4 max-w-2xl">
          <input 
            v-model="testCommand"
            type="text"
            placeholder="Enter command to test"
            class="flex-1 p-3 border border-white/20 rounded bg-darker text-light font-mono focus:border-acid focus:outline-none focus:ring-2 focus:ring-acid/10"
          />
          <button 
            @click="runTestCommand"
            :disabled="!testCommand.trim()"
            class="bg-acid text-dark px-6 py-3 rounded font-bold hover:bg-light transition-colors disabled:opacity-60 disabled:cursor-not-allowed whitespace-nowrap"
          >
            Test Command
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { RouterLink } from 'vue-router'
import { usePucotiStore } from '@/stores/counter'
import type { CommandConfig } from '@/types'
import { hasNeutralino } from '@/neutralino-utils'

const store = usePucotiStore()

// Reactive data
const commands = ref<CommandConfig[]>([])
const selectedCommandId = ref<string>('')
const testCommand = ref('')

const formData = reactive({
  at: '',
  cmd: '',
  every: ''
})

// Load commands on mount
onMounted(() => {
  loadCommands()
})

function loadCommands() {
  commands.value = store.getCommands()
}

function selectCommand(id: string) {
  const command = commands.value.find(cmd => cmd.id === id)
  if (command) {
    selectedCommandId.value = id
    formData.at = command.at
    formData.cmd = command.cmd
    formData.every = command.every || ''
  }
}

function cancelEdit() {
  selectedCommandId.value = ''
  resetForm()
}

function resetForm() {
  formData.at = ''
  formData.cmd = ''
  formData.every = ''
}

function saveCommand() {
  const commandData = {
    at: formData.at.trim(),
    cmd: formData.cmd.trim(),
    every: formData.every.trim() || undefined
  }

  if (selectedCommandId.value) {
    // Update existing command
    store.updateCommand(selectedCommandId.value, commandData)
  } else {
    // Add new command
    store.addCommand(commandData)
  }

  loadCommands()
  cancelEdit()
}

function deleteCommand(id: string) {
  if (confirm('Are you sure you want to delete this command?')) {
    store.deleteCommand(id)
    if (selectedCommandId.value === id) {
      cancelEdit()
    }
    loadCommands()
  }
}

async function runTestCommand() {
  if (!hasNeutralino()) {
    alert('Command execution is only available when running in Neutralino')
    return
  }

  try {
    await window.Neutralino.os.execCommand(testCommand.value.trim(), { background: true })
    alert('Command executed successfully!')
  } catch (error) {
    alert(`Failed to execute command: ${error}`)
  }
}
</script>