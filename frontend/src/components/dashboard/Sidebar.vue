<template>
  <aside class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
    <div class="sidebar-header">
      <router-link :to="{ name: 'dashboard-home' }" class="logo-link">
        <div class="logo">
          <div class="logo-placeholder">SP</div>
          <h2 v-show="!isSidebarCollapsed">Sesplan</h2>
        </div>
      </router-link>
      <button class="sidebar-toggle" @click="$emit('toggle-sidebar')">
        <span class="toggle-icon">{{ isSidebarCollapsed ? '→' : '←' }}</span>
      </button>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-section-header" v-show="!isSidebarCollapsed">GameMaster</div>
      <hr v-show="!isSidebarCollapsed" class="nav-divider"/>
      <router-link :to="{ name: 'dashboard-worlds' }" class="nav-item" active-class="active">
        <i class="icon">🌍</i>
        <span v-show="!isSidebarCollapsed">Worlds</span>
      </router-link>
      <router-link :to="{ name: 'CampaignList' }" class="nav-item" active-class="active">
        <i class="icon">🗺️</i>
        <span v-show="!isSidebarCollapsed">Campaigns</span>
      </router-link>
      <hr class="nav-divider"/>
      <div class="nav-section-header" v-show="!isSidebarCollapsed">Player</div>
      <router-link :to="{ name: 'SessionList' }" class="nav-item" active-class="active">
        <i class="icon">📅</i>
        <span v-show="!isSidebarCollapsed">Sessions</span>
      </router-link>
      <router-link :to="{ name: 'CharacterList' }" class="nav-item" active-class="active">
        <i class="icon">👤</i>
        <span v-show="!isSidebarCollapsed">Characters</span>
      </router-link>
      <router-link :to="{ name: 'JournalList' }" class="nav-item" active-class="active">
        <i class="icon">📖</i>
        <span v-show="!isSidebarCollapsed">Journals</span>
      </router-link>
      <hr class="nav-divider"/>
    </nav>
    <div class="sidebar-footer" v-show="!isSidebarCollapsed">
      <hr class="nav-divider"/>
      <router-link :to="{ name: 'manual' }" class="nav-item nav-item-footer" active-class="active">
        <i class="icon">❓</i>
        <span>User Manual</span>
      </router-link>
    </div>
    <div class="sidebar-footer-collapsed" v-show="isSidebarCollapsed">
      <hr class="nav-divider"/>
      <router-link :to="{ name: 'manual' }" class="nav-item nav-item-footer" active-class="active">
        <i class="icon">❓</i>
      </router-link>
    </div>
  </aside>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Sidebar',
  props: {
    isSidebarCollapsed: {
      type: Boolean,
      required: true
    }
  },
  emits: ['toggle-sidebar']
});
</script>

<style scoped>
.sidebar {
  width: 240px;
  background-color: #fff;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  z-index: 100;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-link {
  text-decoration: none;
  color: inherit;
  display: inline-block;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-placeholder {
  height: 32px;
  width: 32px;
  background-color: #7851a9;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border-radius: 8px;
  margin-right: 10px;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #7851a9;
  white-space: nowrap;
}

.sidebar-toggle {
  background: none;
  border: none;
  color: #7851a9;
  cursor: pointer;
  padding: 5px;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.sidebar-toggle:hover {
  background-color: #f9f5ff;
  border-radius: 4px;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
}

.nav-section-header {
  padding: 10px 20px 5px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  white-space: nowrap;
}

.nav-divider {
  margin: 5px 20px;
  border: none;
  border-top: 1px solid #e9ecef;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  text-decoration: none;
}

.nav-item:hover {
  background-color: #f9f5ff;
  color: #7851a9;
}

.nav-item.active {
  background-color: #f9f5ff;
  color: #7851a9;
  border-left: 3px solid #7851a9;
}

.icon {
  margin-right: 12px;
  font-size: 1.2rem;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px 0;
}

.sidebar.collapsed .icon {
  margin-right: 0;
}

.sidebar.collapsed .nav-section-header,
.sidebar.collapsed .nav-divider {
  display: none;
}

.sidebar-footer {
  padding: 0 0 10px 0;
  margin-top: auto;
}

.sidebar-footer-collapsed {
  padding: 0 0 10px 0;
  margin-top: auto;
}

.sidebar.collapsed .nav-item span {
  display: none;
}

.sidebar.collapsed .sidebar-footer-collapsed .nav-item-footer {
  justify-content: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    transform: translateX(-100%);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
    width: 240px;
  }
}

@media (max-width: 480px) {
  .sidebar:not(.collapsed) {
    width: 85%;
  }
}
</style> 