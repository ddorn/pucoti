import { hasNeutralino } from './neutralino-utils'
import { humanTimeToMs } from './utils'
import type { CommandConfig } from './types'

export class CommandExecutor {
  private commands: CommandConfig[] = []

  constructor() {
    this.loadCommands()
  }

  /**
   * Load commands from localStorage
   */
  private loadCommands(): void {
    try {
      const saved = localStorage.getItem('pucoti-commands')
      if (saved) {
        this.commands = JSON.parse(saved)
      }
    } catch (error) {
      console.error('Failed to load commands from localStorage:', error)
      this.commands = []
    }
  }

  /**
   * Save commands to localStorage
   */
  private saveCommands(): void {
    try {
      localStorage.setItem('pucoti-commands', JSON.stringify(this.commands))
    } catch (error) {
      console.error('Failed to save commands to localStorage:', error)
    }
  }

  /**
   * Get all commands
   */
  getCommands(): CommandConfig[] {
    return [...this.commands]
  }

  /**
   * Add a new command
   */
  addCommand(command: Omit<CommandConfig, 'id'>): string {
    const id = crypto.randomUUID()
    const newCommand: CommandConfig = {
      ...command,
      id,
    }
    this.commands.push(newCommand)
    this.saveCommands()
    return id
  }

  /**
   * Update an existing command
   */
  updateCommand(id: string, updates: Partial<Omit<CommandConfig, 'id'>>): boolean {
    const index = this.commands.findIndex(cmd => cmd.id === id)
    if (index === -1) {
      return false
    }

    this.commands[index] = { ...this.commands[index], ...updates }
    this.saveCommands()
    return true
  }

  /**
   * Delete a command
   */
  deleteCommand(id: string): boolean {
    const index = this.commands.findIndex(cmd => cmd.id === id)
    if (index === -1) {
      return false
    }

    this.commands.splice(index, 1)
    this.saveCommands()
    return true
  }

  /**
   * Execute a command using Neutralino OS API
   */
  private async executeCommand(cmd: string): Promise<void> {
    if (!hasNeutralino()) {
      console.log('Neutralino not available, skipping command:', cmd)
      return
    }

    try {
      await window.Neutralino.os.execCommand(cmd, { background: true })
      console.log('Command executed:', cmd)
    } catch (error) {
      console.error('Failed to execute command:', cmd, error)
    }
  }

  /**
   * Check and execute commands based on current timer state
   * @param currentTimeMs - Current timer time in milliseconds (positive = time remaining, negative = time past zero)
   */
  async checkAndExecuteCommands(currentTimeMs: number): Promise<void> {
    const now = Date.now()

    for (const command of this.commands) {
      try {
        const triggerTimeMs = humanTimeToMs(command.at)
        
        // Check if we should execute this command
        if (this.shouldExecuteCommand(command, currentTimeMs, triggerTimeMs, now)) {
          await this.executeCommand(command.cmd)
          command.lastExecuted = now
          this.saveCommands()
        }
      } catch (error) {
        console.error('Error processing command:', command, error)
      }
    }
  }

  /**
   * Determine if a command should be executed
   */
  private shouldExecuteCommand(
    command: CommandConfig,
    currentTimeMs: number,
    triggerTimeMs: number,
    now: number
  ): boolean {
    // Check if current time has crossed the trigger threshold
    const hasReachedTrigger = currentTimeMs <= triggerTimeMs

    if (!hasReachedTrigger) {
      // Reset lastExecuted if we haven't reached the trigger yet
      if (command.lastExecuted !== undefined) {
        command.lastExecuted = undefined
        this.saveCommands()
      }
      return false
    }

    // If no lastExecuted, this is the first time we've reached the trigger
    if (command.lastExecuted === undefined) {
      return true
    }

    // If there's no "every" setting, only execute once
    if (!command.every) {
      return false
    }

    // Check if enough time has passed since last execution for repeat
    try {
      const repeatIntervalMs = humanTimeToMs(command.every)
      return now - command.lastExecuted >= repeatIntervalMs
    } catch (error) {
      console.error('Invalid "every" duration for command:', command.every, error)
      return false
    }
  }

  /**
   * Reset all command execution states (useful when timer is reset)
   */
  resetCommandStates(): void {
    let hasChanges = false
    for (const command of this.commands) {
      if (command.lastExecuted !== undefined) {
        command.lastExecuted = undefined
        hasChanges = true
      }
    }
    if (hasChanges) {
      this.saveCommands()
    }
  }
}

// Global instance
export const commandExecutor = new CommandExecutor()
