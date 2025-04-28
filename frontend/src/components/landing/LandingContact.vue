<template>
  <section id="contact" class="contact">
    <div class="container">
      <h2>Contact Us</h2>
      <p class="contact-intro">Join our community on Discord!</p>

      <div class="contact-content justify-center">
        <div class="contact-info text-center">
          <div class="info-item">
            <div class="icon">💬</div>
            <h3>Discord</h3>
            <a href="https://discord.gg/qckebehtuV" class="discord-link" target="_blank">
              discord.gg/qckebehtuV
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LandingContact'
});
</script>

<style scoped>
.contact {
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

.contact-intro {
  text-align: center;
  font-size: 1.2rem;
  color: #64748b;
  max-width: 600px;
  margin: 0 auto 50px;
}

.contact-content {
  display: flex;
  justify-content: center;
  gap: 60px;
}

.contact-info {
  text-align: center;
}

.info-item {
  margin-bottom: 30px;
  padding: 20px 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: inline-block;
}

.info-item .icon {
  font-size: 2rem;
  margin-bottom: 15px;
}

.info-item h3 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.info-item p {
  color: #64748b;
}

.discord-link {
  display: inline-block;
  margin-top: 10px;
  color: #7851a9;
  text-decoration: none;
  font-weight: 500;
  font-size: 1.1rem;
}

.discord-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .contact {
    padding: 60px 0;
  }

  h2 {
    font-size: 2rem;
  }

  .contact-intro {
    font-size: 1.1rem;
    margin-bottom: 40px;
  }
}

@media (max-width: 576px) {
  .info-item {
    padding: 15px 30px;
  }
}
</style>