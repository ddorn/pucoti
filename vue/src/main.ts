import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Neutralino from '@neutralinojs/lib'

import App from './App.vue'
import router from './router'

const app = createApp(App)

;(async () => {
    if  (!window.NL_PORT) {
        const config = await import('./auth_info.json')
        window.NL_PORT = config.port
        window.NL_TOKEN = config.accessToken
    }
    Neutralino.init()
})()


app.use(createPinia())
app.use(router)

app.mount('#app')
