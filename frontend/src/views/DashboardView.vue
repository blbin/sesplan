// src/views/DashboardView.vue
<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome! You've successfully logged in.</p>
    <button @click="logout" class="logout-button">Logout</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { authService } from '../services/auth.service';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'DashboardView',
  setup() {
    const router = useRouter();

    const logout = () => {
      authService.logout();
      router.push('/login');
    };

    return { logout };
  }
});
</script>

<style scoped>
.dashboard {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.logout-button {
  background-color: #e53e3e;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
}
</style>