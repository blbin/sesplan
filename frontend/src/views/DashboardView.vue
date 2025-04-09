// src/views/DashboardView.vue
<template>
  <div class="dashboard-container">
    <Sidebar 
      :isSidebarCollapsed="isSidebarCollapsed" 
      @toggle-sidebar="toggleSidebar"
    />
    <main class="main-content" :class="{ 'expanded': isSidebarCollapsed }">
      <DashboardHeader 
        @toggle-sidebar="toggleSidebar" 
        :isSidebarCollapsed="isSidebarCollapsed"
      />
      <div class="dashboard-content">
        <MetricsSection />
        <div class="dashboard-widgets">
          <ActivityWidget />
          <DeadlineWidget />
        </div>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import Sidebar from '../components/dashboard/Sidebar.vue';
import DashboardHeader from '../components/dashboard/DashboardHeader.vue';
import MetricsSection from '../components/dashboard/MetricsSection.vue';
import ActivityWidget from '../components/dashboard/ActivityWidget.vue';
import DeadlineWidget from '../components/dashboard/DeadlineWidget.vue';

export default defineComponent({
  name: 'DashboardView',
  components: {
    Sidebar,
    DashboardHeader,
    MetricsSection,
    ActivityWidget,
    DeadlineWidget
  },
  setup() {
    const isSidebarCollapsed = ref(false);

    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
    };

    return { 
      isSidebarCollapsed,
      toggleSidebar
    };
  }
});
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
  color: #4a5568;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.main-content.expanded {
  margin-left: 0;
}

.dashboard-widgets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.dashboard-content {
  padding-bottom: 20px;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .dashboard-widgets {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
  }
}

@media (max-width: 576px) {
  .dashboard-content {
    padding-bottom: 50px;
  }
}
</style>