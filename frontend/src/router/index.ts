import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import PredictGeneDependencies from '../views/PredictGeneDependencies.vue';
import TCGA from '../views/TCGA.vue';
import About from '../views/About.vue';  // Import the About component

const routes = [
  { path: '/', name: 'HomePage', component: HomePage },
  { path: '/predict-gene-dependencies', name: 'PredictGeneDependencies', component: PredictGeneDependencies },
  { path: '/tcga', name: 'TCGA', component: TCGA },
  { path: '/about', name: 'About', component: About },  // Add the About route
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;