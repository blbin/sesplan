<template>
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
      <div class="auth-buttons">
        <router-link to="/login" class="login-btn">Přihlášení</router-link>
        <router-link to="/register" class="register-btn">Registrace</router-link>
      </div>
      <button class="menu-toggle" @click="toggleMenu">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
    <nav class="nav-mobile" :class="{ active: menuOpen }">
      <ul>
        <li><a href="#features" @click="closeMenu">Funkce</a></li>
        <li><a href="#about" @click="closeMenu">O aplikaci</a></li>
        <li><a href="#contact" @click="closeMenu">Kontakt</a></li>
        <li class="mobile-auth">
          <router-link to="/login" @click="closeMenu">Přihlášení</router-link>
        </li>
        <li class="mobile-auth">
          <router-link to="/register" @click="closeMenu">Registrace</router-link>
        </li>
      </ul>
    </nav>
  </header>
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
  position: sticky;
  top: 0;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
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
}

.logo {
  display: flex;
  align-items: center;
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
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #7851a9;
}

.nav-desktop ul {
  display: flex;
  gap: 30px;
  list-style: none;
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

.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
}

.menu-toggle span {
  display: block;
  width: 25px;
  height: 3px;
  margin: 5px 0;
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
  transition: transform 0.3s;
  z-index: 99;
}

.nav-mobile.active {
  transform: translateY(0);
}

.nav-mobile ul {
  list-style: none;
  padding: 0;
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

.mobile-auth a {
  font-weight: 600;
  color: #7851a9;
}

@media (max-width: 992px) {
  .nav-desktop, .auth-buttons {
    display: none;
  }

  .menu-toggle {
    display: block;
  }

  .nav-mobile {
    display: block;
  }
}
</style>