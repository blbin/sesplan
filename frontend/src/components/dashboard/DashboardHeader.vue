<template>
  <header class="dashboard-header">
    <div class="header-left">
      <button class="mobile-sidebar-toggle" @click="$emit('toggle-sidebar')">
        <span></span>
        <span></span>
        <span></span>
      </button>
      <!-- Odstraněn text Dashboard -->
      <!-- <h1>Dashboard</h1> -->
    </div>
    <div class="header-actions">
      <!-- Zakomentován search bar -->
      <!--
      <div class="search-bar">
        <input type="text" placeholder="Search..." />
        <i class="icon">🔍</i>
      </div>
      -->
      <!-- Zakomentován zvoneček -->
      <!--
      <div class="notifications">
        <i class="icon">🔔</i>
      </div>
      -->
      <div class="user-profile">
        <div class="user-avatar" @click="toggleDropdown">
          {{ username ? username.charAt(0).toUpperCase() : 'U' }}
        </div>
        <div class="user-name">{{ username || 'User' }}</div>
        <div class="dropdown-menu" v-show="isDropdownOpen">
          <div class="dropdown-item">Profile</div>
          <div class="dropdown-item">Settings</div>
          <div class="dropdown-item" @click="handleLogout">Logout</div>
        </div>
      </div>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../store/auth.store';

export default defineComponent({
  name: 'DashboardHeader',
  props: {
    isSidebarCollapsed: {
      type: Boolean,
      required: true
    }
  },
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const isDropdownOpen = ref(false);
    
    const username = computed(() => {
      return authStore.currentUser?.username || '';
    });
    
    const toggleDropdown = () => {
      isDropdownOpen.value = !isDropdownOpen.value;
    };
    
    const handleLogout = () => {
      authStore.logout();
      router.push({ name: 'login' });
    };
    
    const closeDropdown = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.user-profile')) {
        isDropdownOpen.value = false;
      }
    };
    
    if (typeof window !== 'undefined') {
      window.addEventListener('click', closeDropdown);
    }
    
    return {
      isDropdownOpen,
      toggleDropdown,
      handleLogout,
      username,
    };
  },
  emits: ['toggle-sidebar']
});
</script>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
}

.mobile-sidebar-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  margin-right: 15px;
}

.mobile-sidebar-toggle span {
  display: block;
  width: 25px;
  height: 3px;
  margin: 5px 0;
  background-color: #4a5568;
  transition: all 0.3s;
}

.header-actions {
  display: flex;
  align-items: center;
}

.search-bar {
  position: relative;
  margin-right: 15px;
}

.search-bar input {
  padding: 10px 12px 10px 36px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: #fff;
  width: 220px;
  font-size: 0.9rem;
}

.search-bar .icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #8e59d7;
}

.notifications {
  position: relative;
  cursor: pointer;
  padding: 8px;
  color: #7851a9;
  margin-right: 15px;
}

/* User Profile */
.user-profile {
  position: relative;
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background-color: #7851a9;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-avatar:hover {
  background-color: #634288;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.user-name {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.9rem;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 150px;
  z-index: 999;
  overflow: hidden;
}

.dropdown-item {
  padding: 12px 16px;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f9f5ff;
  color: #7851a9;
}

.dropdown-item:last-child {
  border-top: 1px solid #e9ecef;
  color: #e53e3e;
}

.dropdown-item:last-child:hover {
  background-color: #fee2e2;
}

/* Responsive Design */
@media (max-width: 768px) {
  .mobile-sidebar-toggle {
    display: block;
  }
  
  .search-bar input {
    width: 150px;
  }
}

@media (max-width: 576px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-bar {
    flex: 1;
    margin-right: 10px;
  }
  
  .search-bar input {
    width: 100%;
  }
}
</style> 