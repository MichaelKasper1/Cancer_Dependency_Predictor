import 'vuetify/styles'; // Ensure you import Vuetify styles
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify'; // Import Vuetify

createApp(App)
  .use(router)
  .use(vuetify) // Use Vuetify
  .mount('#app');