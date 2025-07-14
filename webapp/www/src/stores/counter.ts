import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { IntentionHistoryItem, Timer, CommandConfig } from '@/types'
import { tickClock } from '@/lib'
import { commandExecutor } from '@/command-executor'

export interface SocialConfig {
  room: string
  username: string
  sendPurpose: boolean
  server: string
}

export interface UpdateRoomRequest {
  username: string
  timer_end: number
  start: number
  purpose?: string
  purpose_start?: number
}

export interface UserData extends UpdateRoomRequest {
  last_update: number
}

export const usePucotiStore = defineStore('pucoti', {
  state: () => {
    const countdownDuration = 10 * 60 * 1000
    const now = new Date().getTime()
    const ringTime = now + countdownDuration

    return {
      countdownDuration,
      intentionHistory: [] as IntentionHistoryItem[],
      pucotiStart: now,
      lastRung: 0,
      ringEvery: '20s', // seconds
      secondaryTimers: ['onIntention'],
      timers: {
        main: {
          zeroAt: ringTime,
          increasing: false,
          name: 'Main timer',
          color: 'var(--color-light)',
        },
        onIntention: {
          zeroAt: now,
          increasing: true,
          name: 'On intention',
          color: 'var(--color-acid)',
        },
      } as Record<string, Timer>,
      social: {
        room: 'public',
        username: '',
        sendPurpose: true,
        server: 'https://sharepoint.pucoti.com',
      } as SocialConfig,
      friendActivity: [] as UserData[],
      lastServerUpdate: 0,
      userId: crypto.randomUUID(),
      serverOffline: false,
    }
  },
  getters: {
    intentionStart(): number {
      if (this.intentionHistory.length > 0) {
        return this.intentionHistory[this.intentionHistory.length - 1].start
      }
      return Date.now()
    },
    intention(): string {
      if (this.intentionHistory.length > 0) {
        return this.intentionHistory[this.intentionHistory.length - 1].intention
      }
      return ''
    },
  },
  actions: {
    setIntention(intention: string) {
      const now = Date.now()
      if (this.intentionHistory.length > 0) {
        this.intentionHistory[this.intentionHistory.length - 1].end = now
      }

      this.intentionHistory.push({
        intention,
        start: now,
      })
      this.timers.onIntention.zeroAt = now
    },
    addTime(ms: number) {
      this.timers.main.zeroAt += ms
      tickClock()
    },
    setRingIn(ms: number) {
      this.timers.main.zeroAt = Date.now() + ms
      commandExecutor.resetCommandStates()
      tickClock()
    },
    updateHistoricalIntention(index: number, newIntention: string) {
      if (index >= 0 && index < this.intentionHistory.length) {
        this.intentionHistory[index].intention = newIntention
      }
    },
    continueFromHistory(intention: string) {
      // Set the current intention without resetting the timer
      const now = Date.now()
      if (this.intentionHistory.length > 0) {
        this.intentionHistory[this.intentionHistory.length - 1].end = now
      }

      this.intentionHistory.push({
        intention,
        start: now,
      })
      this.timers.onIntention.zeroAt = now
    },
    setSocialConfig(config: Partial<SocialConfig>) {
      this.social = { ...this.social, ...config }
      // Save to localStorage
      localStorage.setItem('pucoti-social-config', JSON.stringify(this.social))
    },
    joinRoom(room: string, username: string) {
      this.setSocialConfig({
        room: room.trim(),
        username: username.trim(),
      })
    },
    leaveRoom() {
      this.setSocialConfig({ room: '', username: '' })
      this.friendActivity = []
      // Clear persisted config
      localStorage.removeItem('pucoti-social-config')
    },
    async updateServer(force = false) {
      const UPDATE_SERVER_EVERY = 5000 // 5 seconds (same as legacy app)
      const now = Date.now()
      
      if (!force && now - this.lastServerUpdate < UPDATE_SERVER_EVERY) {
        return
      }

      if (!this.social.username || !this.social.room) {
        return
      }

      this.lastServerUpdate = now

      const payload: UpdateRoomRequest = {
        username: this.social.username,
        timer_end: this.timers.main.zeroAt,
        start: this.pucotiStart,
        purpose: this.social.sendPurpose ? this.intention : undefined,
        purpose_start: this.social.sendPurpose ? this.intentionStart : undefined,
      }

      try {
        const response = await fetch(
          `${this.social.server}/room/${this.social.room}/user/${this.userId}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
          }
        )

        if (response.ok) {
          const data = await response.json()
          this.friendActivity = data as UserData[]
          this.serverOffline = false
        } else {
          console.error('Failed to update server:', response.statusText)
          this.serverOffline = true
        }
      } catch (error) {
        console.error('Error updating server:', error)
        this.serverOffline = true
      }
    },
    loadSocialConfig() {
      const saved = localStorage.getItem('pucoti-social-config')
      if (saved) {
        try {
          const config = JSON.parse(saved) as SocialConfig
          this.social = { ...this.social, ...config }
        } catch (error) {
          console.error('Failed to load social config:', error)
        }
      }
    },
    initializeSocial() {
      this.loadSocialConfig()
      // Start sending updates immediately if we're already in a room
      if (this.social.room && this.social.username) {
        this.updateServer(true)
      }
    },
    // Command execution methods
    getCommands(): CommandConfig[] {
      return commandExecutor.getCommands()
    },
    addCommand(command: Omit<CommandConfig, 'id'>): string {
      return commandExecutor.addCommand(command)
    },
    updateCommand(id: string, updates: Partial<Omit<CommandConfig, 'id'>>): boolean {
      return commandExecutor.updateCommand(id, updates)
    },
    deleteCommand(id: string): boolean {
      return commandExecutor.deleteCommand(id)
    },
    async checkCommands(): Promise<void> {
      const currentTimeMs = this.timers.main.zeroAt - Date.now()
      await commandExecutor.checkAndExecuteCommands(currentTimeMs)
    },
  },
})
