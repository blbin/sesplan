<template>
  <section class="characters-section detail-section">
    <!-- Remove the internal section header -->
    <!-- 
    <div class="section-header">
      <h2>Characters</h2>
      <button v-if="canManage" @click="$emit('open-add-character')" class="btn btn-primary btn-sm">Add Character</button>
    </div>
     -->
    
    <p v-if="charactersLoading" class="loading-state">Loading characters...</p>
    <p v-else-if="charactersError" class="error-message">{{ charactersError }}</p>
    <p v-else-if="characters.length === 0" class="empty-state">No characters found in this world.</p>
    <ul v-else class="entity-list">
      <li v-for="character in characters" :key="character.id" class="entity-list-item">
         <div class="entity-info">
           <router-link :to="{ name: 'CharacterDetail', params: { characterId: character.id } }" class="entity-name-link">
             <span class="entity-name">{{ character.name }}</span>
                </router-link>
           <div class="entity-details">
              <div 
                v-if="character.description"
                class="entity-description-preview" 
                v-html="renderDescriptionPreview(character.description)"
              ></div>
              <span v-else class="entity-description-preview text-muted"><em>No description</em></span>
              <!-- Add tags or other info if available -->
              <span class="entity-date">Created: {{ formatDate(character.created_at) }}</span>
            </div>
         </div>
         <!-- Actions Placeholder -->
         <!-- <div class="entity-actions"> ... </div> -->
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, toRefs } from 'vue';
import * as charactersApi from '@/services/api/characters';
import type { Character } from '@/types/character';
import MarkdownIt from 'markdown-it'; // Import markdown-it
import { formatDate } from '@/utils/dateFormatter'; // Import formatDate

const props = defineProps<{
  worldId: number | string;
  // Remove unused canManage prop
  // canManage: boolean; 
}>();

// Remove canManage from toRefs
const { worldId } = toRefs(props);

const characters = ref<Character[]>([]);
const charactersLoading = ref(false);
const charactersError = ref<string | undefined>(undefined);

// Initialize markdown-it instance
const md = new MarkdownIt({ html: false, linkify: true });

// Method to render description preview
const renderDescriptionPreview = (markdown: string | null): string => {
  if (!markdown) {
    return '';
  }
  const maxLength = 100;
  let truncatedMd = markdown.length > maxLength 
    ? markdown.substring(0, maxLength) + '...' 
    : markdown;
  return md.render(truncatedMd);
};

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
/* Adopt styles from WorldLocationList, potentially using more generic class names */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.detail-section h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.entity-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.entity-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e9ecef;
}

.entity-list-item:last-child {
    border-bottom: none;
}

.entity-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 1rem;
}

.entity-name-link {
    text-decoration: none;
    color: var(--v-theme-primary, #7851a9); /* Use primary theme color */
    font-weight: 600;
    cursor: pointer;
    display: inline-block; /* Needed for margin */
    margin-bottom: 0.25rem; /* Space below name */
}

.entity-name-link:hover .entity-name {
    text-decoration: underline;
}

.entity-name {
  font-size: 1.1rem;
}

.entity-details {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.entity-description-preview {
  line-height: 1.4;
}

.entity-description-preview :deep(p) {
    margin: 0;
    display: inline;
}

.entity-date {
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 0.25rem;
}

.text-muted {
    color: #6c757d;
    font-style: italic;
}

.loading-state,
.error-message,
.empty-state {
  padding: 1rem; /* Adjusted padding */
  text-align: center; /* Center align messages */
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dee2e6; /* Use dashed border for distinction */
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.error-message {
  color: #dc3545; 
  border-color: #f5c6cb;
  background-color: #f8d7da;
}

/* Placeholder for actions if needed later */
/*
.entity-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
*/

/* Ensure button styles are consistent if not globally defined */
.btn {
  /* Basic button resets or styles */
  display: inline-block;
  font-weight: 400;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  border: 1px solid transparent;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  text-decoration: none;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  color: #fff;
  background-color: #0069d9;
  border-color: #0062cc;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 0.2rem;
}
</style> 