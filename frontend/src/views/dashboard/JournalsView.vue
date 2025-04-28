<template>
  <v-container fluid class="journals-view">
    <h1 class="mb-4">My Journals</h1>

    <v-progress-linear indeterminate v-if="loading"></v-progress-linear>

    <v-alert type="error" v-if="error" class="mb-4">
      {{ error }}
    </v-alert>

    <v-row v-if="!loading && !error">
      <v-col v-if="journals.length === 0">
        <p>No journals found for your characters.</p>
      </v-col>
      <v-col
        v-else
        v-for="journal in journals"
        :key="journal.id"
        cols="12"
        md="6"
        lg="4"
      >
        <v-card 
          :title="journal.name || 'Unnamed Journal'"
          :subtitle="`Character ID: ${journal.character_id}`" 
          class="mb-4"
          elevation="2"
        >
          <v-card-text>
            {{ journal.description || 'No description.' }}
          </v-card-text>
          <v-card-actions>
             <!-- TODO: Add link to view journal entries -->
            <v-btn 
              color="primary" 
              variant="text" 
              :disabled="true"
            >
              View Entries (Coming Soon)
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getMyJournals } from '@/services/api/journals';
import type { Journal } from '@/types/journal';

const journals = ref<Journal[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const loadJournals = async () => {
  if (loading.value) return;
  
  loading.value = true;
  error.value = null;
  try {
    const fetchedJournals = await getMyJournals();
    journals.value = fetchedJournals || [];
  } catch (err: any) {
    console.error("Failed to load journals:", err);
    journals.value = [];
    error.value = `Failed to load journals: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
  } finally {
    loading.value = false;
  }
};

onMounted(loadJournals);

</script>

<style scoped>
.journals-view {
  /* Add specific styles if needed */
}
.mb-4 {
  margin-bottom: 1rem;
}
</style> 