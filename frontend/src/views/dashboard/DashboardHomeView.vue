<template>
  <div>
    <h1>Welcome to Sesplan!</h1>
    <p>The application is in version 0.1.x.</p>
    <p>
      For feedback, ideas, or bug reports, please join our
      <a href="https://discord.gg/qckebehtuV" target="_blank" rel="noopener noreferrer">Discord server</a>.
    </p>
    <p class="mt-4">
      Need help getting started? Check out our <router-link :to="{ name: 'manual' }">User Manual</router-link>!
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
// Import potřebných komponent
// import MetricsSection from '../../components/dashboard/MetricsSection.vue'; // Odstraněno
// import ActivityWidget from '../../components/dashboard/ActivityWidget.vue'; // Odstraněno
// import DeadlineWidget from '../../components/dashboard/DeadlineWidget.vue'; // Odstraněno

export default defineComponent({
  name: 'DashboardHomeView',
  components: {
    // MetricsSection, // Odstraněno
    // ActivityWidget, // Odstraněno
    // DeadlineWidget // Odstraněno
  },
  setup() {
    // Zde může být logika specifická pro domovskou stránku dashboardu, pokud je potřeba
    return {};
  }
});
</script>

<style scoped>
/* Styly specifické pro widgety, pokud byly v DashboardView.vue */
/* .dashboard-widgets { // Odstraněno
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px;
} */

/* Responsive Design - můžeme přesunout z DashboardView, pokud se týkají jen widgetů */
/* @media (max-width: 1024px) { // Odstraněno
  .dashboard-widgets {
    grid-template-columns: 1fr;
  }
} */

/* Přidáme jednoduché stylování pro nový obsah */
div {
  padding: 2rem;
  text-align: center;
}

h1 {
  margin-bottom: 1rem;
}

p {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

a {
  color: #1E88E5; /* Modrá barva, můžete upravit dle designu */
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.mt-4 {
  margin-top: 1.5rem; /* Add some space above the manual link */
}
</style> 