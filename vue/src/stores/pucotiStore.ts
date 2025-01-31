import { tickClock } from '@/lib';
import type { IntentionHistoryItem, Timer } from '@/types';
import { defineStore } from 'pinia'

export const usePucotiStore = defineStore('pucoti',
  {
    state: () => {
      const countdownDuration = 10 * 60 * 1000;
      const now = new Date().getTime();
      const ringTime = now + countdownDuration;

      return {
        countdownDuration,
        intentionHistory: [] as IntentionHistoryItem[],
        pucotiStart: now,
        lastRung: 0,
        ringEvery: "20s", // seconds
        secondaryTimers: [
          "total",
          // "Main timer",
          "onIntention",
        ],
        commands: [
          {
            at: "0m",
            every: "1m",
            cmd: "notify-send 'Pucoti' 'Time was up 1+ minute ago !!'",
            lastRan: 0,
          },
        ],
        timers: {
          main: {
            zeroAt: ringTime,
            increasing: false,
            color: "var(--timer)",
            name: "Main timer",
          },
          total: {
            zeroAt: now,
            increasing: true,
            color: "var(--total-time)",
            name: "Total time",
          },
          onIntention: {
            zeroAt: now,
            increasing: true,
            color: "var(--purpose)",
            name: "On intention",
          },
        } as Record<string, Timer>,
      }
    },
    getters: {
      intentionStart(): number {
        if (this.intentionHistory.length > 0) {
          return this.intentionHistory[this.intentionHistory.length - 1].start;
        }
        return Date.now();
      },
      intention(): string {
        if (this.intentionHistory.length > 0) {
          return this.intentionHistory[this.intentionHistory.length - 1].intention;
        }
        return "";
      }
    },
    actions: {
      setIntention(intention: string) {
        const now = Date.now();
        if (this.intentionHistory.length > 0) {
          this.intentionHistory[this.intentionHistory.length - 1].end = now;
        }

        this.intentionHistory.push({
          intention,
          start: now,
        });
      },
      addTime(ms: number) {
        this.timers.main.zeroAt += ms;
        tickClock();
      },
      setRingIn(ms: number) {
        this.timers.main.zeroAt = Date.now() + ms;
        tickClock();
      },
    },
  }
)
