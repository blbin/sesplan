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
        <router-view></router-view>
      </div>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useDisplay } from 'vuetify';
import Sidebar from '../components/dashboard/Sidebar.vue';
import DashboardHeader from '../components/dashboard/DashboardHeader.vue';

export default defineComponent({
  name: 'DashboardView',
  components: {
    Sidebar,
    DashboardHeader,
  },
  setup() {
    const { mobile } = useDisplay();
    const isSidebarCollapsed = ref(mobile.value);

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

.dashboard-content {
  padding-bottom: 20px;
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