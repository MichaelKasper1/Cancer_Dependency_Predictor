import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import PredictGeneDependencies from '../views/PredictGeneDependencies.vue';
import TCGA from '../views/TCGA.vue';

const routes = [
  { path: '/', name: 'HomePage', component: HomePage },
  { path: '/predict-gene-dependencies', name: 'PredictGeneDependencies', component: PredictGeneDependencies },
  { path: '/tcga', name: 'TCGA', component: TCGA }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;