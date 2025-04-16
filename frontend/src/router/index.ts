// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import LandingPage from '../views/LandingPage.vue'
import { useAuthStore } from '../store/auth.store'; 

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/landing' // Nebo '/dashboard' pokud je uživatel přihlášen?
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guestOnly: true } // Přidáme meta pro přesměrování přihlášených
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guestOnly: true } // Přidáme meta pro přesměrování přihlášených
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }, // Tato trasa vyžaduje přihlášení
    children: [
      // Přidáváme defaultní view pro /dashboard
      {
        path: '', // Prázdná cesta znamená, že se načte pro /dashboard
        name: 'dashboard-home',
        component: () => import('../views/dashboard/DashboardHomeView.vue'), // Naše nová komponenta
        meta: { requiresAuth: true }
      },
      // Nová routa pro světy
      {
        path: 'worlds',
        name: 'dashboard-worlds',
        component: () => import('../views/dashboard/WorldsView.vue'),
        meta: { requiresAuth: true } // Zajistíme, že i podstránka vyžaduje přihlášení
      }
      // Zde mohou být další podstránky dashboardu
    ]
  },
  {
    path: '/landing',
    name: 'landing',
    component: LandingPage
    // meta: { guestOnly: true } // Landing page může být dostupná všem
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigační strážce
router.beforeEach(async (to, _from, next) => {
  // Ujistíme se, že Pinia store je inicializován
  const authStore = useAuthStore();

  // Pokusíme se načíst data uživatele, pokud máme token a ještě je nemáme
  // Důležité pro obnovení stránky
  if (authStore.token && !authStore.isLoggedIn) {
    await authStore.initializeAuth();
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const guestOnly = to.matched.some(record => record.meta.guestOnly);

  if (requiresAuth && !authStore.isLoggedIn) {
    // Pokud trasa vyžaduje přihlášení a uživatel není přihlášen, přesměruj na login
    next({ name: 'login', query: { redirect: to.fullPath } }); // Uložíme původní cíl
  } else if (guestOnly && authStore.isLoggedIn) {
    // Pokud je trasa jen pro nepřihlášené (login, register) a uživatel je přihlášen, přesměruj na dashboard
    next({ name: 'dashboard' });
  } else {
    // Jinak povolíme navigaci
    next();
  }
});

export default router