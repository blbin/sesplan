<template>
  <header class="app-header" v-if="isLoggedIn">
    <div class="header-content">
      <span class="username">Welcome, {{ currentUser?.username }}</span>
      <button @click="handleLogout" class="logout-button">Logout</button>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth.store';

export default defineComponent({
  name: 'AppHeader',
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const isLoggedIn = computed(() => authStore.isLoggedIn);
    const currentUser = computed(() => authStore.currentUser);

    const handleLogout = () => {
      authStore.logout();
      router.push({ name: 'login' }); // Přesměrování po odhlášení
    };

    return {
      isLoggedIn,
      currentUser,
      handleLogout,
    };
  },
});
</script>

<style scoped>
.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 0.8rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: flex-end; /* Zarovnání doprava */
  align-items: center;
  max-width: 1200px; /* Omezení šířky obsahu */
  margin: 0 auto;
  gap: 1rem; /* Mezera mezi jménem a tlačítkem */
}

.username {
  font-weight: 500;
}

.logout-button {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.logout-button:hover {
  background-color: #c0392b;
}
</style> 