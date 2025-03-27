<template>
  <section id="about" class="about">
    <div class="container">
      <div class="about-content">
        <div class="about-text">
          <h2>O RPGMaster</h2>
          <p class="lead">Moderní nástroj pro podporu her na hrdiny</p>
          <p>
            Sesplan je komplexní platforma určená pro správu a podporu tabletop RPG her jako jsou
            Dungeons & Dragons, Dračí Doupě a Pathfinder. Naše aplikace poskytuje Game Masterům i hráčům
            nástroje pro plánování, organizaci a běh herních sessions.
          </p>
          <p>
            Klíčovou výhodou je integrace umělé inteligence, která pomáhá generovat herní obsah
            jako města, NPC postavy, události a souhrny deníků postav. Tím usnadňujeme přípravu
            na hru a umožňujeme GM více se soustředit na samotný příběh a zábavu.
          </p>
          <div class="stats">
            <div class="stat-item">
              <div class="stat-number">1000+</div>
              <div class="stat-label">Aktivních uživatelů</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">30+</div>
              <div class="stat-label">RPG systémů</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">500+</div>
              <div class="stat-label">Kampaní</div>
            </div>
          </div>
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

.stats {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  flex-wrap: wrap;
  gap: 20px;
}

.stat-item {
  flex-basis: 120px;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: #7851a9;
  margin-bottom: 5px;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
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