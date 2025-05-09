<template>
  <section id="about" class="about">
    <div class="container">
      <div class="about-content">
        <div class="about-text">
          <h2>About Sesplan</h2>
          <p class="lead">A modern tool to support role-playing games</p>
          <p>
            Sesplan is a versatile tool that gives you the freedom to create and manage your RPG campaigns and worlds without being tied to a specific game system. It provides space and tools for Game Masters and players alike to organize, plan, and record your adventures.
          </p>
          <p>
            Optional artificial intelligence integration can help with inspiration and generating content such as location descriptions, characters, or events, as well as summarizing notes. This can ease your preparation and allow you to focus more on storytelling and the fun at the table.
          </p>
          <!--
          <div class="stats">
            <div class="stat-item">
              <div class="stat-number">1000+</div>
              <div class="stat-label">Active Users</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">30+</div>
              <div class="stat-label">RPG Systems</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">500+</div>
              <div class="stat-label">Campaigns</div>
            </div>
          </div>
          -->
        </div>
        <div class="about-image">
          <div class="about-placeholder">
            <div class="placeholder-text">RPG Session</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LandingAbout'
});
</script>

<style scoped>
.about {
  padding: 80px 0;
  background-color: #fff;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.about-content {
  display: flex;
  align-items: center;
  gap: 60px;
}

.about-text {
  flex: 1;
}

h2 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.lead {
  font-size: 1.3rem;
  color: #7851a9;
  margin-bottom: 20px;
  font-weight: 500;
}

p {
  color: #4a5568;
  line-height: 1.7;
  margin-bottom: 20px;
}

.about-image {
  flex: 1;
}

.about-placeholder {
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #634288, #8e59d7);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.placeholder-text {
  color: white;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

@media (max-width: 992px) {
  .about-content {
    flex-direction: column-reverse;
    text-align: center;
  }

  .stats {
    justify-content: center;
  }

  .stat-item {
    text-align: center;
    margin: 0 15px;
  }
}

@media (max-width: 768px) {
  .about {
    padding: 60px 0;
  }

  h2 {
    font-size: 2rem;
  }

  .lead {
    font-size: 1.2rem;
  }
}
</style>