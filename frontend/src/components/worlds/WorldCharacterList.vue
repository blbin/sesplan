<template>
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
                <router-link :to="{ name: 'CharacterDetail', params: { characterId: character.id } }" class="item-link">
                    {{ character.name }}
                </router-link>
            </h3>
            <p>{{ character.description || 'No description' }}</p>
            <!-- TODO: Add character status/class/level here? -->
         </div>
         <!-- Actions for character (e.g., quick edit/delete) could go here if needed and if user has permissions -->
         <!-- <div class="item-actions" v-if="canManageCharacters"> ... </div> -->
      </li>
    </ul>
    <!-- TODO: Add button to create character if user has permission -->
    <!-- <div class="section-actions" v-if="canManageCharacters"> <button>Add Character</button> </div> -->
  </section>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, toRefs } from 'vue';
import * as charactersApi from '@/services/api/characters';
import type { Character } from '@/types/character';

const props = defineProps<{
  worldId: number | string;
  // TODO: Potentially add a 'canManage' prop if actions are added
}>();

const { worldId } = toRefs(props);

const characters = ref<Character[]>([]);
const charactersLoading = ref(false);
const charactersError = ref<string | undefined>(undefined);

const fetchWorldCharacters = async (id: number | string) => {
    const numericWorldId = Number(id);
    if (isNaN(numericWorldId)) {
        charactersError.value = "Invalid World ID provided.";
        return;
    }
    charactersLoading.value = true;
    charactersError.value = undefined;
    characters.value = [];
    try {
        characters.value = await charactersApi.getAllWorldCharacters(numericWorldId);
    } catch (err: any) {
        console.error("Fetch World Characters Error:", err);
        if (err.response?.status === 403) {
             charactersError.value = 'You do not have permission to view characters in this world.';
        } else if (err.response?.status === 404) {
             charactersError.value = 'Character endpoint not found for this world.'; // Or simply "No characters found."
        } else {
             charactersError.value = `Failed to load characters: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
    } finally {
        charactersLoading.value = false;
    }
};

// Watch for worldId changes to load characters
watch(
  worldId,
  (newId) => {
    if (newId) {
      fetchWorldCharacters(newId);
    } else {
      characters.value = [];
      charactersError.value = "No world selected.";
      charactersLoading.value = false;
    }
  },
  { immediate: true } // Load characters immediately when the component mounts
);

</script>

<style scoped>
/* Styles specific to the character list section */
.characters-section {
  margin-bottom: 2rem; /* Spacing below the section */
}

.characters-section h2 {
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
  font-size: 1.2rem; /* Consistent heading size */
  color: #495057;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-list-item {
  display: flex; /* Use flexbox for alignment */
  justify-content: space-between;
  align-items: center; /* Align items vertically */
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}
.item-list-item:last-child {
    border-bottom: none;
}

.item-info {
    flex-grow: 1; /* Allow info to take up space */
    margin-right: 1rem; /* Space before potential actions */
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
    color: #007bff; /* Link color */
    font-weight: 500;
}
.item-link:hover {
    text-decoration: underline;
}

/* Reusing shared loading/error styles from parent/global */
.loading-message.small,
.error-message.small {
    padding: 1rem 0; /* Adjusted padding */
    font-size: 1rem;
    text-align: left;
}

.loading-message.small {
    color: #6c757d;
}

.error-message.small {
  color: #dc3545; 
  /* Removed background/border, assuming simple text message is enough here */
}

/* Styles for potential actions (if added later) */
/*
.item-actions {
    white-space: nowrap;
    flex-shrink: 0;
}
.section-actions {
    margin-top: 1rem;
    text-align: right;
}
*/
</style> 