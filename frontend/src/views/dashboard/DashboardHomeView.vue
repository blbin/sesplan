<template>
  <!-- Tento obsah byl původně v DashboardView.vue -->
  <MetricsSection />
  <div class="dashboard-widgets">
    <ActivityWidget />
    <DeadlineWidget />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
// Import potřebných komponent
import MetricsSection from '../../components/dashboard/MetricsSection.vue';
import ActivityWidget from '../../components/dashboard/ActivityWidget.vue';
import DeadlineWidget from '../../components/dashboard/DeadlineWidget.vue';

export default defineComponent({
  name: 'DashboardHomeView',
  components: {
    MetricsSection,
    ActivityWidget,
    DeadlineWidget
  },
  setup() {
    // Zde může být logika specifická pro domovskou stránku dashboardu, pokud je potřeba
    return {};
  }
});
</script>

<style scoped>
/* Styly specifické pro widgety, pokud byly v DashboardView.vue */
.dashboard-widgets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-top: 20px; /* Přidáme trochu mezery nad widgety */
}

/* Responsive Design - můžeme přesunout z DashboardView, pokud se týkají jen widgetů */
@media (max-width: 1024px) {
  .dashboard-widgets {
    grid-template-columns: 1fr;
  }
}

</style> 