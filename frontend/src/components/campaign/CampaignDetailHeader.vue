<template>
  <header v-if="campaign && !loading && !error" class="view-header mb-4 d-flex justify-space-between align-center">
    <div class="d-flex align-center flex-grow-1">
      <div v-if="!isEditingName" class="d-flex align-center">
        <h1 class="text-h5">{{ campaign.name }}</h1>
        <v-btn 
          v-if="isCurrentUserGM"
          icon="mdi-pencil" 
          variant="text" 
          size="x-small" 
          @click="emit('startEditingName')"
          title="Edit name"
          class="ml-2"
        ></v-btn>
      </div>
      <div v-else class="d-flex align-center flex-grow-1">
        <v-text-field
          :model-value="editedName"
          @update:model-value="emit('update:editedName', $event)"
          label="Campaign Name"
          variant="outlined"
          density="compact"
          hide-details
          class="mr-2 flex-grow-1"
          autofocus
          @keyup.enter="emit('saveName')"
          @keyup.esc="emit('cancelEditingName')"
        ></v-text-field>
        <v-btn 
          color="primary" 
          @click="emit('saveName')" 
          :loading="isSavingName"
          size="small"
          :disabled="!editedName || (campaign && editedName === campaign.name) || isSavingName || !editedName.trim()"
        >
          Save
        </v-btn>
        <v-btn 
          variant="text" 
          @click="emit('cancelEditingName')" 
          :disabled="isSavingName"
          size="small"
        >
          Cancel
        </v-btn>
      </div>
    </div>
    <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary ml-4">
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
import { VProgressCircular, VAlert, VBtn, VTextField } from 'vuetify/components';

// Accept campaign data, loading state, and error state as props
const props = defineProps<{
  campaign: Campaign | null;
  loading: boolean;
  error: string | null;
  // Name Editing Props
  isCurrentUserGM: boolean | null; // Can be null initially
  isEditingName: boolean;
  editedName: string;
  isSavingName: boolean;
}>();

const emit = defineEmits<{
  (e: 'startEditingName'): void;
  (e: 'cancelEditingName'): void;
  (e: 'saveName'): void;
  (e: 'update:editedName', value: string): void;
}>();

// Explicitly use props to satisfy TS6133
if (import.meta.env.DEV) {
  // This block will be tree-shaken in production
  console.log('Props received in header:', props);
}

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