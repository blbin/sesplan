<template>
  <section id="contact" class="contact">
    <div class="container">
      <h2>Contact Us</h2>
      <p class="contact-intro">Have a question or an idea for improvement? Let us know!</p>

      <div class="contact-content">
        <div class="contact-info">
          <div class="info-item">
            <div class="icon">📧</div>
            <h3>Email</h3>
            <p>info@sesplan.app</p>
          </div>

          <div class="info-item">
            <div class="icon">💬</div>
            <h3>Discord</h3>
            <p>Join our community</p>
            <a href="https://discord.gg/sesplan" class="discord-link" target="_blank">
              discord.gg/sesplan
            </a>
          </div>

          <div class="faq">
            <h3>Frequently Asked Questions (FAQ)</h3>
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
            <label for="name">Name</label>
            <input type="text" id="name" v-model="contactForm.name" required />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="contactForm.email" required />
          </div>

          <div class="form-group">
            <label for="subject">Subject</label>
            <select id="subject" v-model="contactForm.subject" required>
              <option value="">Select subject</option>
              <option value="general">General Inquiry</option>
              <option value="support">Technical Support</option>
              <option value="feedback">Feedback</option>
              <option value="feature">Feature Suggestion</option>
            </select>
          </div>

          <div class="form-group">
            <label for="message">Message</label>
            <textarea id="message" v-model="contactForm.message" rows="6" required></textarea>
          </div>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? 'Sending...' : 'Send Message' }}
          </button>

          <div v-if="submitStatus" class="submit-status" :class="{ 'status-success': submitStatus === 'success' }">
            {{ submitStatus === 'success' ? 'Message sent successfully!' : 'An error occurred while sending. Please try again.' }}
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
        question: 'Is the Sesplan app free?',
        answer: 'The basic version of the app is completely free. We offer a premium subscription for advanced features.',
        isOpen: false
      },
      {
        question: 'Which RPG systems are supported?',
        answer: 'We support most popular systems including D&D 5e, Pathfinder, Dračí Doupě, and many others. We are constantly adding new ones.',
        isOpen: false
      },
      {
        question: 'Can I use custom rules and systems?',
        answer: 'Yes! The application is designed to be flexible and allow customization for any RPG system or custom rules.',
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