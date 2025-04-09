<template>
  <div>
    <header class="header">
      <div class="container">
        <div class="logo">
          <div class="logo-placeholder">RPG</div>
          <h1>SesPlan</h1>
        </div>
        <nav class="nav-desktop">
          <ul>
            <li><a href="#features">Funkce</a></li>
            <li><a href="#about">O aplikaci</a></li>
            <li><a href="#contact">Kontakt</a></li>
          </ul>
        </nav>
        <div class="auth-buttons desktop-auth">
          <router-link to="/login" class="login-btn">Přihlášení</router-link>
          <router-link to="/register" class="register-btn">Registrace</router-link>
        </div>
        <div class="mobile-header-actions">
          <div class="mobile-auth-buttons">
            <router-link to="/login" class="mobile-login-btn">Přihlášení</router-link>
            <router-link to="/register" class="mobile-register-btn">Registrace</router-link>
          </div>
          <button class="menu-toggle" @click="toggleMenu">
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
      </div>
    </header>
    <nav class="nav-mobile" :class="{ active: menuOpen }">
      <ul>
        <li><a href="#features" @click="closeMenu">Funkce</a></li>
        <li><a href="#about" @click="closeMenu">O aplikaci</a></li>
        <li><a href="#contact" @click="closeMenu">Kontakt</a></li>
      </ul>
    </nav>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'LandingHeader',
  setup() {
    const menuOpen = ref(false);

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value;
    };

    const closeMenu = () => {
      menuOpen.value = false;
    };

    return {
      menuOpen,
      toggleMenu,
      closeMenu
    };
  }
});
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  width: 100%;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
  box-sizing: border-box;
}

.logo {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.logo-placeholder {
  height: 40px;
  width: 40px;
  background-color: #7851a9;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border-radius: 8px;
  margin-right: 10px;
  flex-shrink: 0;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #7851a9;
  margin: 0;
}

.nav-desktop ul {
  display: flex;
  gap: 30px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-desktop a {
  font-weight: 500;
  color: #4a5568;
  text-decoration: none;
  transition: color 0.3s;
}

.nav-desktop a:hover {
  color: #7851a9;
}

.auth-buttons {
  display: flex;
  gap: 15px;
}

.login-btn, .register-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: all 0.3s;
}

.login-btn {
  color: #7851a9;
}

.login-btn:hover {
  background-color: #f9f5ff;
}

.register-btn {
  background-color: #7851a9;
  color: white;
}

.register-btn:hover {
  background-color: #634288;
}

.mobile-header-actions {
  display: none;
  align-items: center;
  gap: 10px;
}

.mobile-auth-buttons {
  display: flex;
  gap: 8px;
}

.mobile-login-btn, .mobile-register-btn {
  padding: 6px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.8rem;
  text-decoration: none;
}

.mobile-login-btn {
  color: #7851a9;
  background-color: transparent;
  border: 1px solid #7851a9;
}

.mobile-register-btn {
  background-color: #7851a9;
  color: white;
  border: 1px solid #7851a9;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  margin-left: 5px;
}

.menu-toggle span {
  display: block;
  width: 22px;
  height: 2px;
  margin: 4px 0;
  background-color: #333;
  transition: all 0.3s;
}

.nav-mobile {
  display: none;
  position: fixed;
  top: 80px;
  left: 0;
  right: 0;
  background-color: #fff;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transform: translateY(-100%);
  opacity: 0;
  transition: transform 0.3s, opacity 0.3s;
  z-index: 999;
}

.nav-mobile.active {
  transform: translateY(0);
  opacity: 1;
}

.nav-mobile ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-mobile li {
  margin-bottom: 15px;
}

.nav-mobile a {
  display: block;
  font-size: 1.1rem;
  color: #4a5568;
  text-decoration: none;
  padding: 8px 0;
}

@media (max-width: 992px) {
  .nav-desktop, .desktop-auth {
    display: none;
  }

  .mobile-header-actions {
    display: flex;
  }

  .menu-toggle {
    display: block;
  }

  .nav-mobile {
    display: block;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 12px;
    height: 70px;
  }
  
  .logo h1 {
    font-size: 1.2rem;
  }
  
  .logo-placeholder {
    height: 34px;
    width: 34px;
  }

  .nav-mobile {
    top: 70px;
  }
}

@media (max-width: 576px) {
  .container {
    padding: 0 10px;
    height: 60px;
  }
  
  .logo h1 {
    font-size: 1.1rem;
  }
  
  .logo-placeholder {
    height: 30px;
    width: 30px;
    margin-right: 8px;
  }

  .mobile-login-btn, .mobile-register-btn {
    padding: 5px 8px;
    font-size: 0.75rem;
  }

  .nav-mobile {
    top: 60px;
    padding: 15px;
  }
}

@media (max-width: 400px) {
  .logo h1 {
    font-size: 1rem;
  }
  
  .logo-placeholder {
    height: 28px;
    width: 28px;
    margin-right: 6px;
  }
  
  .mobile-login-btn, .mobile-register-btn {
    padding: 4px 6px;
    font-size: 0.7rem;
  }
}
</style>