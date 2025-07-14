import { format } from 'date-fns'
import type { Timer } from './types'

export const MINUTE = 60 * 1000

export function timerToMs(timer: Timer): number {
  return timer.increasing ? Date.now() - timer.zeroAt : timer.zeroAt - Date.now()
}

export function timerToString(timer: Timer): string {
  let time = timerToMs(timer)

  if (time < 0) {
    time = -time
  }

  const parts = fmtSeconds(time)
  return parts.join(':')
}

/**
 * Format a time in seconds to the parts of a string.
 *
 * Example: 3661 -> ["1", "01", "01"]
 * Example: 61 -> ["01", "01"]
 *
 * @param {number} time Duration in seconds
 * @returns {string[]} Array of strings representing the time in the format [hours, minutes, seconds]. Hours is there only if it's not 0
 */
export function fmtSeconds(time: number) {
  const seconds = Math.floor(Math.abs(time) / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const parts = []
  if (hours > 0) {
    parts.push(hours)
  }
  parts.push((minutes % 60).toString().padStart(2, '0'))
  parts.push((seconds % 60).toString().padStart(2, '0'))
  return parts
}

/**
 * Convert a human duration such as "1h 30m" to seconds.
 * @param {string} duration - The duration string to convert
 * @returns {number} The duration in miliseconds
 */
export function humanTimeToMs(duration: string): number {
  if (duration.startsWith('-')) {
    return -humanTimeToMs(duration.slice(1))
  }

  duration = duration.toLowerCase()

  // Parse the duration.
  let total = 0
  const multiplier = { s: 1, m: 60, h: 3600, d: 86400 }

  const parts = duration.split(' ')
  for (const part of parts) {
    try {
      const value = parseInt(part.slice(0, -1))
      const unit = part.slice(-1)

      if (isNaN(value) || !(unit in multiplier)) {
        throw new Error(`Invalid duration part: ${part}`)
      }

      total += value * multiplier[unit]
    } catch (error) {
      throw new Error(`Invalid duration part: ${part}`)
    }
  }

  return total * 1000
}

export function fmtTimeRelative(seconds: Date): string {
  /**
   * Get a datetime object or a number Epoch timestamp and return a
   * pretty string like 'an hour ago', 'Yesterday', '3 months ago',
   * 'just now', etc.
   *
   * The time must be in the past.
   */

  const diff = Date.now() - seconds.getTime()
  const secondDiff = Math.floor(diff / 1000)
  const dayDiff = Math.floor(secondDiff / 86400)

  if (dayDiff < 0) {
    throw new Error('Invalid date difference')
  }

  if (dayDiff === 0) {
    if (secondDiff < 10) return 'just now'
    if (secondDiff < 60) return `${secondDiff}s ago`
    if (secondDiff < 120) return `1m ${secondDiff % 60}s ago`
    if (secondDiff < 3600) return `${Math.floor(secondDiff / 60)}m ago`
    if (secondDiff < 7200) return `1h ${Math.floor((secondDiff % 3600) / 60)}m ago`
    if (secondDiff < 86400) return `${Math.floor(secondDiff / 3600)}h ago`
  }
  if (dayDiff <= 1) return 'Yesterday'
  if (dayDiff < 7) return `${dayDiff} days ago`
  if (dayDiff < 31) return `${Math.floor(dayDiff / 7)} weeks ago`
  if (dayDiff < 365) return `${Math.floor(dayDiff / 30)} months ago`

  return `${Math.floor(dayDiff / 365)} years ago`
}

/**
 * Human readable time format for dates in the past.
 * E.g. "at 12:34", "Yest at 12:34", "Mon at 12:34", "Mon 12 at 12:34", "Mon 12 Jan at 12:34"
 */
export function fmtTimeAbsolute(seconds: Date): string {
  const now = new Date()

  const diff = now.getTime() - seconds.getTime()
  const dayDiff = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (dayDiff < 0) {
    throw new Error('Invalid date difference')
  }

  if (dayDiff === 0) {
    // return `at ${format(seconds, 'HH:mm')}`;
    return format(seconds, "'at' HH:mm")
  }
  if (dayDiff === 1) {
    // return `Yest at ${format(seconds, 'HH:mm')}`;
    return format(seconds, "'Yest' HH:mm")
  }
  if (dayDiff < 7) {
    // return `${format(seconds, 'EEE')} at ${format(seconds, 'HH:mm')}`;
    return format(seconds, "EEE 'at' HH:mm")
  }
  if (dayDiff < 31 && now.getMonth() === seconds.getMonth()) {
    // return `${format(seconds, 'EEE dd')} at ${format(seconds, 'HH:mm')}`;
    return format(seconds, "EEE dd 'at' HH:mm")
  }
  if (now.getFullYear() === seconds.getFullYear()) {
    // return `${format(seconds, 'EEE dd MMM')} at ${format(seconds, 'HH:mm')}`;
    return format(seconds, "EEE dd MMM 'at' HH:mm")
  }
  // return `${format(seconds, 'EEE dd MMM yyyy')} at ${format(seconds, 'HH:mm')}`;
  return format(seconds, "EEE dd MMM yyyy 'at' HH:mm")
}

export function fmtTime(seconds: Date, relative: boolean = true): string {
  return relative ? fmtTimeRelative(seconds) : fmtTimeAbsolute(seconds)
}

export function computeTimerEnd(timer: number, start: number): number {
  // +0.5 to show visually round time -> more satisfying
  return timer + (Math.round(Date.now() / 1000 + 0.5) - start)
}
