// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import LandingPage from '../views/LandingPage.vue'
import { useAuthStore } from '../store/auth.store'; 

const routes: RouteRecordRaw[] = [
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
      },
      // Nová routa pro DETAIL světa
      {
        path: 'worlds/:worldId',
        name: 'dashboard-world-detail',
        component: () => import('../views/dashboard/WorldDetailView.vue'),
        props: true,
        meta: { requiresAuth: true },
        // Children odebráno, detail lokace je sourozenec
        // children: [ ... ]
      },
      // Původní nevnořená cesta pro LocationDetail - UPRAVENO
      {
        // Přidáno /worlds/:worldId/ na začátek
        path: 'worlds/:worldId/locations/:locationId', 
        name: 'LocationDetail', 
        component: () => import('@/views/dashboard/LocationDetailView.vue'),
        // Předáváme worldId a locationId
        props: route => ({
             worldId: Number(route.params.worldId), // Převedeme na číslo
             locationId: Number(route.params.locationId) 
        }),
        meta: { requiresAuth: true }
      },
      // Nová routa pro OrganizationDetail - UPRAVENO
      {
        // Přidáno /worlds/:worldId/ na začátek
        path: 'worlds/:worldId/organizations/:organizationId', 
        name: 'OrganizationDetail',
        component: () => import('@/views/dashboard/OrganizationDetailView.vue'),
        // Předáváme worldId a organizationId
        props: route => ({
             worldId: Number(route.params.worldId), 
             organizationId: Number(route.params.organizationId)
         }),
        meta: { requiresAuth: true }
      },
      // Nová routa pro ItemDetail - UPRAVENO
      {
        // Přidáno /worlds/:worldId/ na začátek
        path: 'worlds/:worldId/items/:itemId', 
        name: 'ItemDetail', 
        component: () => import('@/views/dashboard/ItemDetailView.vue'),
        // Předáváme worldId a itemId
        props: route => ({
             worldId: Number(route.params.worldId),
             itemId: Number(route.params.itemId)
         }),
        meta: { requiresAuth: true }
      },
      // Nová routa pro kampaně
      {
        path: 'campaigns',
        name: 'CampaignList',
        component: () => import('@/views/dashboard/CampaignsView.vue'),
        meta: { requiresAuth: true },
      },
      // Nová routa pro detail kampaně
      {
        path: 'campaigns/:campaignId',
        name: 'CampaignDetail',
        component: () => import('@/views/dashboard/CampaignDetailView.vue'),
        props: true, // Pass route params as props
        meta: { requiresAuth: true },
      },
      // Session Detail Route (now top-level under dashboard)
      {
        path: 'campaigns/:campaignId/sessions/:sessionId', // Full path
        name: 'SessionDetail',
        component: () => import('@/views/dashboard/SessionDetailView.vue'),
        props: true, // Pass campaignId and sessionId as props
        meta: { requiresAuth: true },
      },
      // Nová routa pro seznam sessions
      {
        path: 'sessions',
        name: 'SessionList',
        component: () => import('@/views/dashboard/SessionListView.vue'),
        meta: { requiresAuth: true }
      },
      // Nová routa pro postavy
      {
        path: 'characters',
        name: 'CharacterList',
        component: () => import('@/views/dashboard/CharactersView.vue'),
        meta: { requiresAuth: true }
      },
      // Nová routa pro detail postavy
      {
        path: 'characters/:characterId',
        name: 'CharacterDetail',
        component: () => import('@/views/dashboard/CharacterDetailView.vue'),
        props: true,
        meta: { requiresAuth: true }
      },
      // Nová routa pro deníky
      {
        path: 'journals',
        name: 'JournalList',
        component: () => import('@/views/dashboard/JournalsView.vue'),
        meta: { requiresAuth: true }
      },
      // Nová routa pro DETAIL deníku
      {
        path: 'journals/:journalId',
        name: 'JournalDetail',
        component: () => import('@/views/dashboard/JournalDetailView.vue'),
        props: true, // Pass journalId as prop
        meta: { requiresAuth: true }
      },
      // Přesunutá routa pro nastavení uživatele
      {
        path: 'settings', // Relativní cesta k /dashboard
        name: 'settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { requiresAuth: true } // Vyžaduje přihlášení
      }
    ]
  },
  {
    path: '/',
    name: 'landing',
    component: LandingPage
    // meta: { guestOnly: true } // Landing page může být dostupná všem
  },
  // Add route for accepting invites
  {
    path: '/invite/:token',
    name: 'accept-invite',
    component: () => import('../views/AcceptInviteView.vue'),
    meta: { requiresAuth: true } // User must be logged in to accept
  },
  // Přidání routy pro nastavení uživatele
  // {
  //   path: '/settings',
  //   name: 'settings',
  //   component: () => import('../views/SettingsView.vue'),
  //   meta: { requiresAuth: true } // Vyžaduje přihlášení
  // }
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