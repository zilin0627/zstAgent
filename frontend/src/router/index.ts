import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/atlas', name: 'atlas', component: () => import('@/views/PatternAtlasView.vue') },
    { path: '/guide', name: 'guide', component: () => import('@/views/GuideView.vue') },
    { path: '/studio', name: 'studio', component: () => import('@/views/DesignStudioView.vue') },
    { path: '/showcase', name: 'showcase', component: () => import('@/views/ShowcaseView.vue') },
    { path: '/scenarios', name: 'scenarios', component: () => import('@/views/ScenariosView.vue') },
    { path: '/method', name: 'method', component: () => import('@/views/MethodView.vue') },
  ],
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' };
  },
});

export default router;
