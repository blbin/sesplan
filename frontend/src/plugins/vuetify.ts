// Vuetify Configuration
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

// Styly
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Definujeme světlé a tmavé téma
const lightTheme = {
  dark: false,
  colors: {
    primary: '#7851a9', // Fialová barva, která již byla použita v sidebar
    secondary: '#4a5568',
    accent: '#4299e1',
    error: '#e53e3e',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
    background: '#f8f9fa',
    surface: '#FFFFFF',
  }
}

// Vytvoření Vuetify instance
export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
}) 