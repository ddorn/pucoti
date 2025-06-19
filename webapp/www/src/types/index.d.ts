export type IntentionHistoryItem = {
  intention: string
  start: number
  end?: number
}

export type Timer = {
  zeroAt: number
  increasing: boolean
  color: string
  name: string
}
