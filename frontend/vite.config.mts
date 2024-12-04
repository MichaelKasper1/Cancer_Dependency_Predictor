import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  define: {
    '__VUE_OPTIONS_API__': JSON.stringify(true),
    '__VUE_PROD_DEVTOOLS__': JSON.stringify(false),
    '__VUE_PROD_HYDRATION_MISMATCH_DETAILS__': JSON.stringify(false),
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // Django backend URL connection
        changeOrigin: true,
        secure: false,
      },
    },
  },
});