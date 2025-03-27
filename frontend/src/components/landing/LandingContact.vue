<template>
  <section id="contact" class="contact">
    <div class="container">
      <h2>Kontaktujte nás</h2>
      <p class="contact-intro">Máte dotaz nebo nápad na vylepšení? Napište nám!</p>

      <div class="contact-content">
        <div class="contact-info">
          <div class="info-item">
            <div class="icon">📧</div>
            <h3>Email</h3>
            <p>info@rpgmaster.cz</p>
          </div>

          <div class="info-item">
            <div class="icon">💬</div>
            <h3>Discord</h3>
            <p>Připojte se do naší komunity</p>
            <a href="https://discord.gg/rpgmaster" class="discord-link" target="_blank">
              discord.gg/rpgmaster
            </a>
          </div>

          <div class="faq">
            <h3>Často kladené dotazy</h3>
            <div class="faq-item" v-for="(item, index) in faqItems" :key="index">
              <div class="faq-question" @click="toggleFaq(index)">
                {{ item.question }}
                <span class="faq-icon">{{ item.isOpen ? '−' : '+' }}</span>
              </div>
              <div class="faq-answer" v-if="item.isOpen">
                {{ item.answer }}
              </div>
            </div>
          </div>
        </div>

        <form class="contact-form" @submit.prevent="submitContact">
          <div class="form-group">
            <label for="name">Jméno</label>
            <input type="text" id="name" v-model="contactForm.name" required />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="contactForm.email" required />
          </div>

          <div class="form-group">
            <label for="subject">Předmět</label>
            <select id="subject" v-model="contactForm.subject" required>
              <option value="">Vyberte předmět</option>
              <option value="general">Obecný dotaz</option>
              <option value="support">Technická podpora</option>
              <option value="feedback">Zpětná vazba</option>
              <option value="feature">Návrh funkce</option>
            </select>
          </div>

          <div class="form-group">
            <label for="message">Zpráva</label>
            <textarea id="message" v-model="contactForm.message" rows="6" required></textarea>
          </div>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? 'Odesílání...' : 'Odeslat zprávu' }}
          </button>

          <div v-if="submitStatus" class="submit-status" :class="{ 'status-success': submitStatus === 'success' }">
            {{ submitStatus === 'success' ? 'Zpráva byla úspěšně odeslána!' : 'Došlo k chybě při odesílání. Zkuste to prosím znovu.' }}
          </div>
        </form>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';

export default defineComponent({
  name: 'LandingContact',
  setup() {
    const contactForm = reactive({
      name: '',
      email: '',
      subject: '',
      message: ''
    });

    const isSubmitting = ref(false);
    const submitStatus = ref('');

    const faqItems = reactive([
      {
        question: 'Je aplikace RPGMaster zdarma?',
        answer: 'Základní verze aplikace je zcela zdarma. Pro pokročilé funkce nabízíme prémiové předplatné.',
        isOpen: false
      },
      {
        question: 'Jaké RPG systémy jsou podporovány?',
        answer: 'Podporujeme většinu populárních systémů včetně D&D 5e, Pathfinder, Dračí Doupě a mnoho dalších. Neustále přidáváme nové.',
        isOpen: false
      },
      {
        question: 'Můžu používat vlastní pravidla a systémy?',
        answer: 'Ano! Aplikace je navržena tak, aby byla flexibilní a umožňovala přizpůsobení pro jakýkoliv RPG systém nebo vlastní pravidla.',
        isOpen: false
      }
    ]);

    const toggleFaq = (index: number) => {
      faqItems[index].isOpen = !faqItems[index].isOpen;
    };

    const submitContact = async () => {
      isSubmitting.value = true;

      try {
        // Simulace odeslání na server
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Reset formuláře
        contactForm.name = '';
        contactForm.email = '';
        contactForm.subject = '';
        contactForm.message = '';

        submitStatus.value = 'success';

        // Skrytí statusu po 5 sekundách
        setTimeout(() => {
          submitStatus.value = '';
        }, 5000);
      } catch (error) {
        submitStatus.value = 'error';
      } finally {
        isSubmitting.value = false;
      }
    };

    return {
      contactForm,
      isSubmitting,
      submitStatus,
      faqItems,
      toggleFaq,
      submitContact
    };
  }
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
  gap: 60px;
}

.contact-info {
  flex: 1;
}

.info-item {
  margin-bottom: 30px;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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
}

.discord-link:hover {
  text-decoration: underline;
}

.faq {
  margin-top: 40px;
}

.faq h3 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.faq-item {
  margin-bottom: 15px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.faq-question {
  padding: 15px 20px;
  background-color: white;
  font-weight: 600;
  color: #4a5568;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.faq-icon {
  font-size: 1.2rem;
  color: #7851a9;
}

.faq-answer {
  padding: 15px 20px;
  background-color: #f8f8fb;
  color: #64748b;
  line-height: 1.6;
}

.contact-form {
  flex: 1;
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #4a5568;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #7851a9;
  outline: none;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #7851a9;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #634288;
}

.submit-btn:disabled {
  background-color: #a990c9;
  cursor: not-allowed;
}

.submit-status {
  margin-top: 15px;
  padding: 10px;
  border-radius: 6px;
  background-color: #f8d7da;
  color: #721c24;
  text-align: center;
}

.status-success {
  background-color: #d4edda;
  color: #155724;
}

@media (max-width: 992px) {
  .contact-content {
    flex-direction: column;
  }
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
  }

  .info-item, .contact-form {
    padding: 20px;
  }
}
</style>