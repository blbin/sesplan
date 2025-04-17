<!-- src/components/landing/LandingFeatures.vue -->
<template>
  <section id="features" class="features">
    <div class="container">
      <h2>Key Features</h2>
      <p class="subtitle">Everything you need for your RPG adventure</p>

      <div class="features-grid">
        <div class="feature-card">
          <div class="icon ai-icon">🤖</div>
          <h3>AI Content Generation</h3>
          <p>Automatically generate NPCs, locations, plot hooks, and other game elements using artificial intelligence.</p>
        </div>

        <div class="feature-card">
          <div class="icon">📝</div>
          <h3>Character Management</h3>
          <p>Create, edit, and organize your characters with a clear system for stats and inventory.</p>
        </div>

        <div class="feature-card">
          <div class="icon">🗺️</div>
          <h3>World Building</h3>
          <p>Build rich worlds with unique geography, history, and cultures for your campaigns.</p>
        </div>

        <div class="feature-card">
          <div class="icon">📅</div>
          <h3>Session Scheduling</h3>
          <p>Synchronize schedules with players and keep track of planned game sessions.</p>
        </div>

        <div class="feature-card">
          <div class="icon">📊</div>
          <h3>Progress Tracking</h3>
          <p>Record campaign events and track character and story development over time.</p>
        </div>

        <div class="feature-card">
          <div class="icon">🎲</div>
          <h3>Game Tools</h3>
          <p>Utilize virtual dice, random encounter generators, and other helper tools for smooth gameplay.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LandingFeatures'
});
</script>

<style scoped>
.features {
  padding: 80px 0;
  background-color: #f9f7fe;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

h2 {
  text-align: center;
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.subtitle {
  text-align: center;
  font-size: 1.2rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto 50px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-card .icon {
  font-size: 2.5rem;
  margin-bottom: 20px;
  display: inline-block;
}

.ai-icon {
  background: linear-gradient(135deg, #7851a9, #d442f8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.feature-card h3 {
  font-size: 1.4rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.feature-card p {
  color: #64748b;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .features {
    padding: 60px 0;
  }

  h2 {
    font-size: 2rem;
  }

  .subtitle {
    font-size: 1.1rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>