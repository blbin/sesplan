<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-logo">
          <div class="logo-placeholder">RPG</div>
          <span>RPGMaster</span>
        </div>

        <div class="newsletter">
          <h3>Odebírejte novinky</h3>
          <p>Získejte informace o nových funkcích, tipech a aktualizacích</p>
          <form @submit.prevent="subscribeNewsletter">
            <input type="email" v-model="newsletter" placeholder="Váš email" required />
            <button type="submit">Přihlásit se</button>
          </form>
        </div>
      </div>

      <div class="footer-content">
        <div class="footer-column">
          <h4>Aplikace</h4>
          <ul>
            <li><router-link to="/features">Funkce</router-link></li>
            <li><router-link to="/pricing">Ceník</router-link></li>
            <li><router-link to="/faq">Časté dotazy</router-link></li>
            <li><router-link to="/support">Podpora</router-link></li>
          </ul>
        </div>

        <div class="footer-column">
          <h4>RPG Zdroje</h4>
          <ul>
            <li><a href="#">Generátor NPC</a></li>
            <li><a href="#">Mapy a lokace</a></li>
            <li><a href="#">Nástroje pro DM</a></li>
            <li><a href="#">Bestiář</a></li>
          </ul>
        </div>

        <div class="footer-column">
          <h4>Společnost</h4>
          <ul>
            <li><router-link to="/about">O nás</router-link></li>
            <li><router-link to="/blog">Blog</router-link></li>
            <li><router-link to="/privacy">Ochrana soukromí</router-link></li>
            <li><router-link to="/terms">Podmínky použití</router-link></li>
          </ul>
        </div>

        <div class="footer-column">
          <h4>Sledujte nás</h4>
          <div class="social-links">
            <a href="#" aria-label="Discord">
              <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286z"/></svg>
            </a>
            <a href="#" aria-label="Twitter">
              <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/></svg>
            </a>
            <a href="#" aria-label="Instagram">
              <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.897 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.897-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"/></svg>
            </a>
            <a href="#" aria-label="YouTube">
              <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            </a>
          </div>

          <div class="app-badges">
            <p>Mobilní aplikace:</p>
            <div class="badges">
              <a href="#" class="app-badge">
                <div class="badge-placeholder">Google Play</div>
              </a>
              <a href="#" class="app-badge">
                <div class="badge-placeholder">App Store</div>
              </a>
            </div>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p class="copyright">
          &copy; {{ new Date().getFullYear() }} RPGMaster. Všechna práva vyhrazena.
        </p>
        <div class="small-links">
          <router-link to="/cookies">Cookies</router-link>
          <router-link to="/sitemap">Mapa stránek</router-link>
        </div>
      </div>

      <div class="footer-dice">
        <span>🎲</span>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'LandingFooter',
  setup() {
    const newsletter = ref('');

    const subscribeNewsletter = () => {
      // Implementace přihlášení k newsletteru
      alert(`Email ${newsletter.value} byl přihlášen k odběru novinek`);
      newsletter.value = '';
    };

    return {
      newsletter,
      subscribeNewsletter
    };
  }
});
</script>

<style scoped>
.footer {
  background-color: #1a1a2e;
  color: #fff;
  padding: 60px 0 30px;
  position: relative;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  position: relative;
}

.footer-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 50px;
  flex-wrap: wrap;
  gap: 40px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 12px;
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
}

.footer-logo span {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
}

.newsletter {
  max-width: 400px;
}

.newsletter h3 {
  font-size: 1.2rem;
  margin-bottom: 10px;
}

.newsletter p {
  font-size: 0.9rem;
  margin-bottom: 15px;
  opacity: 0.8;
}

.newsletter form {
  display: flex;
  gap: 10px;
}

.newsletter input {
  flex: 1;
  padding: 12px 15px;
  border-radius: 6px;
  border: none;
  font-size: 0.9rem;
  outline: none;
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.newsletter input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.newsletter button {
  padding: 12px 20px;
  background-color: #7851a9;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.newsletter button:hover {
  background-color: #8a62bb;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
  margin-bottom: 50px;
}

.footer-column h4 {
  font-size: 1.1rem;
  margin-bottom: 20px;
  position: relative;
  padding-bottom: 10px;
}

.footer-column h4::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 30px;
  height: 2px;
  background-color: #7851a9;
}

.footer-column ul {
  list-style: none;
  padding: 0;
}

.footer-column li {
  margin-bottom: 12px;
}

.footer-column a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: color 0.3s;
  font-size: 0.95rem;
}

.footer-column a:hover {
  color: #fff;
}

.social-links {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.social-links a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transition: background-color 0.3s, transform 0.3s;
}

.social-links a:hover {
  background-color: #7851a9;
  transform: translateY(-3px);
}

.app-badges p {
  margin-bottom: 10px;
  font-size: 0.9rem;
  opacity: 0.8;
}

.badges {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.app-badge {
  display: block;
}

.badge-placeholder {
  padding: 8px 12px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: white;
  font-size: 0.8rem;
  text-align: center;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.copyright {
  font-size: 0.9rem;
  opacity: 0.7;
}

.small-links {
  display: flex;
  gap: 20px;
}

.small-links a {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
}

.small-links a:hover {
  color: #fff;
}

.footer-dice {
  position: absolute;
  bottom: 130px;
  right: 50px;
  font-size: 3rem;
  opacity: 0.1;
  transform: rotate(20deg);
  animation: float 5s infinite ease-in-out;
}

@keyframes float {
  0%, 100% {
    transform: rotate(20deg) translateY(0);
  }
  50% {
    transform: rotate(30deg) translateY(-10px);
  }
}

@media (max-width: 992px) {
  .footer-top {
    flex-direction: column;
    gap: 30px;
  }

  .newsletter {
    max-width: 100%;
  }

  .footer-content {
    grid-template-columns: repeat(2, 1fr);
  }

  .footer-dice {
    display: none;
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 40px 0 20px;
  }

  .footer-bottom {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .newsletter form {
    flex-direction: column;
  }

  .newsletter button {
    width: 100%;
  }
}

@media (max-width: 576px) {
  .footer-content {
    grid-template-columns: 1fr;
  }

  .social-links {
    justify-content: center;
  }

  .badges {
    justify-content: center;
  }
}
</style>