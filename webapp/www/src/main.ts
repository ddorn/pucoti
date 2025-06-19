import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { initializeNeutralinojs } from './neutralino-utils'

import App from './App.vue'
import router from './router'

initializeNeutralinojs()

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
