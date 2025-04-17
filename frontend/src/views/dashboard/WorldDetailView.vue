<template>
  <div class="world-detail-view">
    <!-- Loading state for world details -->
    <div v-if="worldLoading" class="loading-message">Loading world details...</div>
    <!-- Error state for world details -->
    <div v-else-if="worldError" class="error-message">
      <p>{{ worldError }}</p>
      <router-link :to="{ name: 'dashboard-worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>
    <!-- Content when world details are loaded -->
    <div v-else-if="world" class="world-content">
      <header class="view-header">
        <h1>{{ world.name }}</h1>
        <!-- Add Edit/Delete buttons for world here if needed -->
        <router-link :to="{ name: 'dashboard-worlds' }" class="btn btn-secondary">Back to List</router-link>
      </header>

      <div class="details-section">
        <h2>World Details</h2>
        <p><strong>Description:</strong> {{ world.description || 'No description provided.' }}</p>
        <p><strong>Public:</strong> {{ world.is_public ? 'Yes' : 'No' }}</p>
        <p><strong>Created:</strong> {{ formatDate(world.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDate(world.updated_at) }}</p>
        <!-- Add more world details as needed -->
      </div>

      <!-- Section for Characters -->
      <section class="characters-section">
        <h2>Characters in this World</h2>
        <!-- Loading state for characters -->
        <p v-if="charactersLoading" class="loading-message small">Loading characters...</p>
        <!-- Error state for characters (including permission denied) -->
        <p v-else-if="charactersError" class="error-message small">{{ charactersError }}</p>
        <!-- No characters found -->
        <p v-else-if="characters.length === 0">No characters found in this world.</p>
        <!-- Character list -->
        <ul v-else class="item-list">
          <li v-for="character in characters" :key="character.id" class="item-list-item">
             <div class="item-info">
                <h3>
                    <router-link :to="`/dashboard/characters/${character.id}`" class="item-link">
                        {{ character.name }}
                    </router-link>
                </h3>
                <p>{{ character.description || 'No description' }}</p>
             </div>
             <!-- Actions for character (e.g., quick edit/delete) could go here -->
          </li>
        </ul>
      </section>

      <!-- Placeholder for other related sections like Campaigns, Items, Events etc. -->

    </div>
    <!-- Fallback if world somehow wasn't found after loading -->
    <div v-else>
        <p>World not found.</p>
        <router-link :to="{ name: 'dashboard-worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import * as worldsApi from '@/services/api/worlds';
import * as charactersApi from '@/services/api/characters';
import type { World } from '@/types/world';
import type { Character } from '@/types/character';

export default defineComponent({
  name: 'WorldDetailView',
  props: {
    worldId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const world = ref<World | null>(null);
    const characters = ref<Character[]>([]);
    const worldLoading = ref(true);
    const charactersLoading = ref(false); // Start false, load after world loads
    const worldError = ref<string | null>(null);
    const charactersError = ref<string | null>(null);

    const fetchWorldDetails = async (id: number) => {
      worldLoading.value = true;
      worldError.value = null;
      world.value = null;
      try {
        world.value = await worldsApi.getWorldById(id);
        // If world loaded successfully, try fetching characters
        fetchWorldCharacters(id);
      } catch (err: any) {
        console.error("Fetch World Error:", err);
        if (err.response?.status === 404) {
            worldError.value = 'World not found.';
        } else {
            worldError.value = `Failed to load world details: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
      } finally {
        worldLoading.value = false;
      }
    };

    const fetchWorldCharacters = async (id: number) => {
        charactersLoading.value = true;
        charactersError.value = null;
        characters.value = [];
        try {
            characters.value = await charactersApi.getAllWorldCharacters(id);
        } catch (err: any) {
            console.error("Fetch World Characters Error:", err);
            if (err.response?.status === 403) {
                 charactersError.value = 'You do not have permission to view characters in this world.';
            } else if (err.response?.status === 404) {
                 // This case might happen if the world exists but the character endpoint doesn't? Unlikely.
                 charactersError.value = 'Character endpoint not found for this world.';
            } else {
                 charactersError.value = `Failed to load characters: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
            }
        } finally {
            charactersLoading.value = false;
        }
    };

    // Helper to format date strings
    const formatDate = (dateString: string): string => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString();
        } catch (e) {
            return dateString;
        }
    };

    // Fetch data on mount and when the route parameter changes
    onMounted(() => {
      fetchWorldDetails(Number(props.worldId));
    });

    watch(() => props.worldId, (newId) => {
      if (newId) {
        fetchWorldDetails(Number(newId));
      }
    });

    return {
      world,
      characters,
      worldLoading,
      charactersLoading,
      worldError,
      charactersError,
      formatDate,
    };
  },
});
</script>

<style scoped>
/* Using similar structure and styles as CharacterDetailView */
.world-detail-view {
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

.world-content {
    background-color: #fff;
    padding: 1.5rem 2rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.details-section,
.characters-section {
  margin-bottom: 2rem;
}

.details-section h2,
.characters-section h2 {
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

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-list-item {
  /* Reuse styles from CharactersView if applicable, or define new ones */
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}
.item-list-item:last-child {
    border-bottom: none;
}

.item-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
}

.item-info p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.item-link {
    text-decoration: none;
    color: #007bff;
}
.item-link:hover {
    text-decoration: underline;
}


.loading-message,
.error-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
}
.loading-message.small,
.error-message.small {
    padding: 1rem;
    font-size: 1rem;
    text-align: left;
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