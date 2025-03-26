import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
  // Načtení proměnných prostředí pro aktuální mode
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [vue()],
    base: '/',
    server: {
      proxy: {
        '/': {
          target: env.VITE_API_URL,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});