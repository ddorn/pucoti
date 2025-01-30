import type { IntentionHistoryItem } from '@/types';
import { defineStore } from 'pinia'

export const usePucotiStore = defineStore('pucoti',
  {
    state: () => {
      let countdownDuration = 10 * 60 * 1000;
      let now = new Date().getTime();
      let ringTime = now + countdownDuration;

      return {
        countdownDuration,
        ringTime,
        intentionStart: 0,
        intentionHistory: [] as IntentionHistoryItem[],
        pucotiStart: now,
        lastRung: 0,
        ringEvery: "20s", // seconds
        intention: "",
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
            value: 0,
            color: "var(--timer)",
            name: "Main timer",
          },
          total: {
            value: 0,
            color: "var(--total-time)",
            name: "Total time",
          },
          onIntention: {
            value: 0,
            color: "var(--purpose)",
            name: "On intention",
          },
        }
      }
    },
    actions: {
      setIntention(intention: string) {
        this.intention = intention;
        this.intentionStart = new Date().getTime();
        this.intentionHistory.push({
          intention,
          start: this.intentionStart,
        });
      },
      updateTimers() {
        let now = new Date().getTime();

        this.timers.main.value = this.ringTime - now;
        this.timers.total.value = now - this.pucotiStart;
        this.timers.onIntention.value = now - this.intentionStart;

      },


    },
  }
)
