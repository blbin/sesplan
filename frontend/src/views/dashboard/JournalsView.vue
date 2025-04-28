<template>
  <v-container fluid class="journals-view">
    <header class="view-header mb-4">
      <h1>My Journals</h1>
      <!-- TODO: Add button for actions if needed in the future -->
    </header>

    <div class="list-container">
      <v-progress-linear indeterminate v-if="loading"></v-progress-linear>
      
      <v-alert type="error" v-else-if="error" class="mb-4">
        {{ error }}
      </v-alert>

      <v-row v-else-if="journals.length === 0">
        <v-col>
          <p>No journals found for your characters.</p>
          <p><small>Journals are automatically created when you create a character.</small></p>
        </v-col>
      </v-row>

      <v-row v-else>
        <v-col
          v-for="journal in journals"
          :key="journal.id"
          cols="12"
          md="6"
          lg="4"
        >
          <v-card class="mb-4" elevation="2">
            <v-card-title>{{ journal.name || 'Unnamed Journal' }}</v-card-title>
            <v-card-subtitle>Character ID: {{ journal.character_id }}</v-card-subtitle>
            <v-card-text>
              {{ journal.description || 'No description available.' }}
            </v-card-text>
            <v-card-actions>
              <v-btn 
                color="primary" 
                variant="text" 
                :disabled="false" 
                @click="navigateToJournalDetail(journal.id)"
              >
                View Entries
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </div>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getMyJournals } from '@/services/api/journals';
import type { Journal } from '@/types/journal';
import { useRouter } from 'vue-router';

const journals = ref<Journal[]>([]);
const loading = ref(false); // Start as false, set to true when loading starts
const error = ref<string | null>(null);
const router = useRouter();

const loadJournals = async () => {
  if (loading.value) return; // Prevent concurrent loads

  loading.value = true;
  error.value = null;
  console.log("Attempting to load journals..."); // Debug log

  try {
    const fetchedJournals = await getMyJournals();
    console.log("Fetched journals:", fetchedJournals); // Debug log
    journals.value = fetchedJournals || []; // Ensure it's always an array
    if (journals.value.length === 0) {
      console.log("No journals received from API."); // Debug log
    }
  } catch (err: any) {
    console.error("Failed to load journals:", err);
    journals.value = []; // Clear journals on error
    error.value = `Failed to load journals: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
  } finally {
    loading.value = false;
    console.log("Finished loading journals attempt."); // Debug log
  }
};

const navigateToJournalDetail = (journalId: number) => {
  router.push({ name: 'JournalDetail', params: { journalId: journalId.toString() } });
};

// Load journals when the component is mounted
onMounted(() => {
  loadJournals();
});

</script>

<style scoped>
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mb-4 {
  margin-bottom: 1rem;
}

.list-container p {
  color: #6c757d; /* Softer text color for messages */
}
</style> 