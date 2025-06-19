import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { init } from '@neutralinojs/lib'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

// Initialize Neutralino.js when globals are available
function initializeNeutralinojs() {
  if (typeof window.NL_PORT !== 'undefined' && typeof window.NL_TOKEN !== 'undefined') {
    init()
  } else {
    // Wait a bit and try again if globals aren't ready yet
    console.log('Neutralino.js globals not ready yet, waiting...')
    setTimeout(initializeNeutralinojs, 100)
  }
}

initializeNeutralinojs()
