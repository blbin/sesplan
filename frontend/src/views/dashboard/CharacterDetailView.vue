<template>
  <div class="character-detail-view">
    <div v-if="loading" class="loading-message">Loading character details...</div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <router-link :to="{ name: 'dashboard-characters' }" class="btn btn-secondary">Back to Characters</router-link>
    </div>
    <div v-else-if="character" class="character-content">
      <header class="view-header">
        <h1>{{ character.name }}</h1>
        <!-- Add Edit/Delete buttons here if needed -->
        <router-link :to="{ name: 'dashboard-characters' }" class="btn btn-secondary">Back to List</router-link>
      </header>

      <div class="details-section">
        <h2>Details</h2>
        <p><strong>Description:</strong> {{ character.description || 'No description provided.' }}</p>
        <p><strong>World ID:</strong> {{ character.world_id }}</p>
        <!-- TODO: Fetch and display world name? -->
        <p><strong>Owner ID:</strong> {{ character.user_id }}</p>
        <!-- TODO: Fetch and display owner username? -->
        <p><strong>Created:</strong> {{ formatDate(character.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDate(character.updated_at) }}</p>
      </div>

       <!-- Placeholder for related sections -->
       <div class="related-sections">
            <section>
                <h3>Journal Entries</h3>
                <p>Journal functionality coming soon.</p>
            </section>
            <section>
                <h3>Items</h3>
                <p>Item management coming soon.</p>
            </section>
            <section>
                <h3>Relationships</h3>
                <p>Character relationship tracking coming soon.</p>
            </section>
       </div>

    </div>
    <div v-else>
        <p>Character not found.</p>
         <router-link :to="{ name: 'dashboard-characters' }" class="btn btn-secondary">Back to Characters</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import * as charactersApi from '@/services/api/characters';
import type { Character } from '@/types/character';

export default defineComponent({
  name: 'CharacterDetailView',
  props: {
    characterId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const character = ref<Character | null>(null);
    const loading = ref(true);
    const error = ref<string | null>(null);

    const fetchCharacter = async (id: number) => {
      loading.value = true;
      error.value = null;
      character.value = null;
      try {
        character.value = await charactersApi.getCharacterById(id);
      } catch (err: any) {
        console.error("Fetch Character Error:", err);
        if (err.response?.status === 404) {
            error.value = 'Character not found.';
        } else {
            error.value = `Failed to load character: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
      } finally {
        loading.value = false;
      }
    };

    // Helper to format date strings
    const formatDate = (dateString: string): string => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString();
        } catch (e) {
            return dateString; // Return original if formatting fails
        }
    };

    // Fetch character on mount and when the route parameter changes
    onMounted(() => {
      fetchCharacter(Number(props.characterId));
    });

    watch(() => props.characterId, (newId) => {
      if (newId) {
        fetchCharacter(Number(newId));
      }
    });

    return {
      character,
      loading,
      error,
      formatDate,
    };
  },
});
</script>

<style scoped>
.character-detail-view {
  padding: 2rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.view-header h1 {
  margin: 0;
}

.character-content {
    background-color: #fff;
    padding: 1.5rem 2rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.details-section,
.related-sections section {
  margin-bottom: 2rem;
}

.details-section h2,
.related-sections h3 {
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.details-section p {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.details-section p strong {
    margin-right: 0.5em;
}

.related-sections {
    margin-top: 2rem;
}

.loading-message,
.error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.error-message p {
    margin-bottom: 1rem;
}

/* Reusing button styles */
.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 0.3rem;
    cursor: pointer;
    border: none;
    font-weight: 500;
    text-decoration: none;
    text-align: center;
}
.btn-secondary {
    background-color: #6c757d;
    color: white;
}
.btn-secondary:hover {
    background-color: #5a6268;
}
</style> 