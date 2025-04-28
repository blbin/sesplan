<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-logo">
          <div class="logo-placeholder">RPG</div>
          <span>Sesplan</span>
        </div>
      </div>

      <div class="footer-content">
        <div class="footer-column">
          <h4>Company</h4>
          <ul>
            <li><a href="#about">About Us</a></li>
            <li><router-link to="/privacy">Privacy Policy</router-link></li>
            <li><router-link to="/terms">Terms of Use</router-link></li>
          </ul>
        </div>

        <div class="footer-column">
          <h4>Follow Us</h4>
          <div class="social-links">
            <a href="https://discord.gg/qckebehtuV" target="_blank" aria-label="Discord">
              <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286z"/></svg>
            </a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <p class="copyright">
          &copy; {{ new Date().getFullYear() }} Patrik Trejtnar. All rights reserved.
        </p>
        <!-- 
        <div class="small-links">
          <router-link to="/cookies">Cookies</router-link>
          <router-link to="/sitemap">Sitemap</router-link>
        </div>
        -->
      </div>

      <div class="footer-dice">
        <span>🎲</span>
      </div>
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LandingFooter',
  setup() {
    return {
      // Removed newsletter related returns
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
}

@media (max-width: 576px) {
  .footer-content {
    grid-template-columns: 1fr;
  }

  .social-links {
    justify-content: center;
  }
}
</style>