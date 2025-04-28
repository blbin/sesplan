<template>
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <h1>Sesplan - Your tabletopRPG session planning space 🌌</h1>
        <p>Optimize your game with a modern tool for Game Masters and players</p>
        <div class="feature-points">
          <div class="feature-point">
            <span class="icon">✨</span>
            <span>AI game content generation</span>
          </div>
          <div class="feature-point">
            <span class="icon">🧙</span>
            <span>Character and NPC management</span>
          </div>
          <div class="feature-point">
            <span class="icon">🗺️</span>
            <span>World and campaign creation</span>
          </div>
        </div>
        <div class="cta-buttons">
          <router-link to="/login" class="btn btn-primary">Log in</router-link>
          <router-link to="/register" class="btn btn-secondary">Start for free</router-link>
        </div>
      </div>
      <div class="hero-image">
        <div class="hero-placeholder">
          <div class="placeholder-text">RPG Platform</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LandingHero'
});
</script>

<style scoped>
.hero {
  padding: 40px 0;
  background: linear-gradient(to right, #f8f9fa, #e9ecef);
  overflow: hidden;
  position: relative;
  width: 100%;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 40px;
  box-sizing: border-box;
}

.hero-content {
  flex: 1;
  z-index: 2;
}

.hero-content h1 {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 20px;
  color: #2c3e50;
  line-height: 1.2;
  word-wrap: break-word;
}

.hero-content p {
  font-size: 1.25rem;
  margin-bottom: 30px;
  color: #4a5568;
  max-width: 600px;
}

.feature-points {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 30px;
}

.feature-point {
  display: flex;
  align-items: center;
  font-size: 1.1rem;
  color: #4a5568;
}

.feature-point .icon {
  margin-right: 10px;
  font-size: 1.4rem;
}

.cta-buttons {
  display: flex;
  gap: 15px;
}

.btn {
  display: inline-block;
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background-color: #7851a9;
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #634288;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}

.btn-secondary {
  background-color: white;
  color: #7851a9;
  border: 2px solid #7851a9;
}

.btn-secondary:hover {
  background-color: #f9f5ff;
  transform: translateY(-2px);
  box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
}

.hero-image {
  flex: 1;
  text-align: center;
  z-index: 1;
}

.hero-placeholder {
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #8e59d7, #634288);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.5s ease;
}

.placeholder-text {
  color: white;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-placeholder:hover {
  transform: translateY(-10px) scale(1.02);
}

/* Responzivní design */
@media (max-width: 992px) {
  .container {
    flex-direction: column;
    text-align: center;
  }

  .hero-content h1 {
    font-size: 2.5rem;
    width: 100%;
    max-width: 100%;
  }

  .feature-points {
    align-items: center;
  }

  .cta-buttons {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .hero {
    padding: 30px 0;
  }

  .hero-content h1 {
    font-size: 2rem;
    width: 100%;
    max-width: 100%;
    word-break: break-word;
    hyphens: auto;
  }

  .hero-content p {
    font-size: 1.1rem;
    width: 100%;
  }

  .btn {
    padding: 12px 24px;
    width: auto;
  }
}

@media (max-width: 576px) {
  .hero {
    padding: 20px 0;
  }
  
  .container {
    padding: 0 15px;
  }

  .cta-buttons {
    flex-direction: column;
    width: 100%;
  }

  .btn {
    width: 100%;
  }

  .feature-point {
    font-size: 1rem;
  }

  .hero-content h1 {
    font-size: 1.6rem;
    hyphens: auto;
  }
  
  .hero-placeholder {
    height: 200px;
  }
}
</style>