import { init } from '@neutralinojs/lib'

export function hasNeutralino(): boolean {
  return !!window.NL_PORT
}

export function initializeNeutralinojs(): void {
  if (hasNeutralino() && window.NL_TOKEN) {
    // We don't want to call init multiple times.
    // Once called, it moves NL_TOKEN to local storage, so we can check for that.
    // If we were to re-run init, it would not find the token anymore.
    init()
    console.log('Neutralino.js initialized successfully')
  } else if (!hasNeutralino()) {
    console.error('Neutralino.js not available')
  }
}
