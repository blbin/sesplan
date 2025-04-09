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