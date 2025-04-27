<template>
  <header v-if="campaign && !loading && !error" class="view-header mb-4 d-flex justify-space-between align-center">
    <h1>{{ campaign.name }}</h1>
    <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary">
      &larr; Back to Campaigns
    </router-link>
  </header>
  <div v-else-if="loading" class="loading-state d-flex justify-center align-center flex-column pa-5">
    <v-progress-circular indeterminate color="primary"></v-progress-circular>
    <p class="mt-4">Loading campaign header...</p>
  </div>
  <div v-else-if="error" class="error-message pa-5">
    <v-alert type="error" prominent border="start">
      Error loading campaign data: {{ error }}
    </v-alert>
    <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary mt-4">
      &larr; Back to Campaigns
    </router-link>
  </div>
  <div v-else class="not-found pa-5"> <!-- Handle case where campaign is null after loading without error -->
      <v-alert type="warning" border="start">
        Campaign details could not be loaded.
      </v-alert>
       <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary mt-4">
        &larr; Back to Campaigns
      </router-link>
    </div>
</template>

<script setup lang="ts">
import type { Campaign } from '@/types/campaign';
import { VProgressCircular, VAlert } from 'vuetify/components';

// Accept campaign data, loading state, and error state as props
const props = defineProps<{
  campaign: Campaign | null;
  loading: boolean;
  error: string | null;
}>();

// Log props to satisfy TS6133 in strict build environments
console.log('CampaignDetailHeader props:', props);

</script>

<style scoped>
/* Scoped styles for the header component */

.loading-state,
.error-message,
.not-found {
  text-align: center;
}

.btn-secondary {
  /* Basic styling for the back button if not handled globally */
  text-decoration: none;
  padding: 0.5rem 1rem;
  background-color: #6c757d;
  color: white;
  border-radius: 0.25rem;
  border: none;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style> 