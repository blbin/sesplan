<template>
  <div class="landing-page">
    <landing-header />
    <landing-hero />
    <landing-features />
    <landing-about />
    <landing-contact />
    <landing-footer />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import LandingHeader from '@/components/landing/LandingHeader.vue';
import LandingHero from '@/components/landing/LandingHero.vue';
import LandingFeatures from '@/components/landing/LandingFeatures.vue';
import LandingAbout from '@/components/landing/LandingAbout.vue';
import LandingContact from '@/components/landing/LandingContact.vue';
import LandingFooter from '@/components/landing/LandingFooter.vue';

export default defineComponent({
  name: 'LandingPage',
  components: {
    LandingHeader,
    LandingHero,
    LandingFeatures,
    LandingAbout,
    LandingContact,
    LandingFooter
  },
  mounted() {
    document.title = 'Sesplan | Streamline Your RPG Campaign Planning';

    let metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute('content', 'Sesplan is the ultimate online tool for planning and organizing your tabletop RPG campaigns. Manage worlds, sessions, characters, and collaborate with your players easily.');
    } else {
      metaDescription = document.createElement('meta');
      metaDescription.setAttribute('name', 'description');
      metaDescription.setAttribute('content', 'Sesplan is the ultimate online tool for planning and organizing your tabletop RPG campaigns. Manage worlds, sessions, characters, and collaborate with your players easily.');
      document.head.appendChild(metaDescription);
    }
  }
});
</script>

<style>
/* Pouze globální styly specifické pro landing page */
.landing-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  line-height: 1.6;
  color: #333;
  padding-top: 80px; /* Přidáno pro vytvoření místa pro fixed header */
}

@media (max-width: 768px) {
  .landing-page {
    padding-top: 70px;
  }
}

@media (max-width: 576px) {
  .landing-page {
    padding-top: 60px;
  }
}
</style>