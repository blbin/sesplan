<template>
  <div class="characters-view">
    <header class="view-header">
      <h1>My Characters</h1>
      <button @click="openAddModal" class="btn btn-primary">
        <i class="icon">+</i> Add New Character
      </button>
    </header>

    <div class="list-container">
      <p v-if="loading">Loading characters...</p>
      <p v-else-if="error" class="error-message">{{ error }}</p>
      <div v-else-if="characters.length === 0">You haven't created any characters yet.</div>
      <ul v-else class="world-list">
        <li v-for="character in characters" :key="character.id" class="world-list-item">
          <div class="world-info">
            <router-link :to="{ name: 'CharacterDetail', params: { characterId: character.id } }" class="world-name-link">
               <h2>{{ character.name }}</h2>
            </router-link>
             <p class="world-description" v-html="renderMarkdownInline(character.description, 100)"></p>
             <small class="world-meta">Created: {{ formatDate(character.created_at) }}</small>
          </div>
          <div class="world-actions">
            <button @click="openEditModal(character)" class="btn btn-secondary btn-sm">Edit</button>
            <button @click="confirmDelete(character)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Modal for Add/Edit Character -->
    <div v-if="showModal" class="modal-backdrop" @click.self="closeModal">
      <div class="modal">
        <button @click="closeModal" class="close-button">&times;</button>

        <div v-if="!editingCharacter && !selectedWorldIdForNewChar" class="modal-content">
          <h2>Select World for New Character</h2>
          <p v-if="loadingWorlds">Loading worlds...</p>
          <p v-else-if="worldsError" class="error-message">{{ worldsError }}</p>
          <ul v-else-if="userWorlds.length > 0" class="world-selection-list">
             <li v-for="world in userWorlds" :key="world.id">
                <button @click="selectWorldForNewCharacter(world.id)" class="world-select-button">
                    {{ world.name }}
                </button>
            </li>
          </ul>
          <p v-else>You don't seem to own any worlds. Create a world first.</p>
        </div>

        <div v-else-if="editingCharacter || selectedWorldIdForNewChar" class="modal-content">
          <h2>{{ editingCharacter ? 'Edit Character' : 'Add New Character' }}</h2>
           <CreateCharacterForm
             :worldId="formWorldId"
             :characterToEdit="editingCharacter"
             :isSaving="isSavingCharacter"
             :error="formError" 
             @saved="handleCharacterSaved"
             @cancel="closeModal" 
          />
        </div>
        
      </div>
    </div>

     <!-- Modal for Delete Confirmation -->
    <ConfirmDeleteModal
        :show="!!characterToDelete"
        itemType="character"
        :itemName="characterToDelete?.name"
        :isDeleting="isDeletingCharacter"
        :error="deleteError"
        @confirm="handleDeleteCharacter"
        @cancel="characterToDelete = null"
     />

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import * as charactersApi from '@/services/api/characters';
import type { Character } from '@/types/character';
import { formatDate } from '@/utils/dateFormatter';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
import * as worldsApi from '@/services/api/worlds';
import type { World } from '@/types/world';
import CreateCharacterForm from '@/components/dashboard/CreateCharacterForm.vue';

import MarkdownIt from 'markdown-it';
const md = new MarkdownIt({ html: false, linkify: true, typographer: true });
const renderMarkdownInline = (markdown: string | null | undefined, maxLength: number): string => {
  if (!markdown) { return '<em>No description</em>'; }
  let truncatedMd = markdown.length > maxLength ? markdown.substring(0, maxLength) + '...' : markdown;
  return md.renderInline(truncatedMd);
};

export default defineComponent({
  name: 'CharactersView',
  components: { 
      ConfirmDeleteModal,
      CreateCharacterForm
  },
  setup() {
    const characters = ref<Character[]>([]);
    const userWorlds = ref<World[]>([]);
    
    const loading = ref(true);
    const loadingWorlds = ref(false);
    
    const error = ref<string | null>(null);
    const worldsError = ref<string | null>(null);
    const formError = ref<string | null>(null);
    const deleteError = ref<string | null>(null);
    const isDeletingCharacter = ref(false);
    const isSavingCharacter = ref(false);

    const showModal = ref(false);
    const editingCharacter = ref<Character | null>(null);
    const characterToDelete = ref<Character | null>(null);
    const selectedWorldIdForNewChar = ref<number | null>(null);

    // Computed property to safely determine worldId for the form
    const formWorldId = computed(() => {
        if (editingCharacter.value) {
            // Assuming world_id is non-null on the Character type when editing
            return editingCharacter.value.world_id; 
        }
        if (selectedWorldIdForNewChar.value !== null) {
            return selectedWorldIdForNewChar.value;
        }
        // This state should not be reached due to the v-if/v-else-if logic in the template
        console.error("Attempted to render CreateCharacterForm without a valid worldId.");
        // Return a dummy value or handle appropriately, though it indicates a logic error
        return -1; 
    });

    const loadCharacters = async () => {
      loading.value = true;
      error.value = null;
      try {
        characters.value = await charactersApi.getMyCharacters();
      } catch (err: any) {
        error.value = `Failed to load characters: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Load Characters Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const loadUserWorlds = async () => {
        loadingWorlds.value = true;
        worldsError.value = null;
        try {
            userWorlds.value = await worldsApi.getWorlds();
        } catch (err: any) {
            worldsError.value = `Failed to load worlds: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
            console.error("Load User Worlds Error:", err);
        } finally {
            loadingWorlds.value = false;
        }
    };

    const closeModal = () => {
      showModal.value = false;
      editingCharacter.value = null;
      selectedWorldIdForNewChar.value = null;
      formError.value = null;
    };

     const openAddModal = () => {
        editingCharacter.value = null;
        selectedWorldIdForNewChar.value = null;
        formError.value = null;
        showModal.value = true;
        if (userWorlds.value.length === 0 && !loadingWorlds.value) {
            loadUserWorlds();
        }
    };

     const openEditModal = (character: Character) => {
        editingCharacter.value = character;
        selectedWorldIdForNewChar.value = null;
        formError.value = null;
        showModal.value = true;
    };

    const handleCharacterSaved = (_savedCharacter: Character) => {
        closeModal();
        loadCharacters(); 
    };

    const selectWorldForNewCharacter = (worldId: number) => {
        selectedWorldIdForNewChar.value = worldId;
    };

    const confirmDelete = (character: Character) => {
        characterToDelete.value = character;
        deleteError.value = null;
    };

    const handleDeleteCharacter = async () => {
      if (!characterToDelete.value) return;
      const idToDelete = characterToDelete.value.id;
      deleteError.value = null;
      isDeletingCharacter.value = true;
      try {
          await charactersApi.deleteCharacter(idToDelete);
          await loadCharacters();
          characterToDelete.value = null;
      } catch (err: any) {
           deleteError.value = `Delete failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
           console.error("Delete Character Error:", err);
      } finally {
          isDeletingCharacter.value = false;
      }
    };

    onMounted(loadCharacters);

    return {
      characters,
      userWorlds,
      loading,
      loadingWorlds,
      error,
      worldsError,
      formError,
      deleteError,
      isDeletingCharacter,
      isSavingCharacter,
      showModal,
      editingCharacter,
      characterToDelete,
      selectedWorldIdForNewChar,
      closeModal,
      openAddModal,
      openEditModal,
      handleCharacterSaved,
      selectWorldForNewCharacter,
      confirmDelete,
      handleDeleteCharacter,
      renderMarkdownInline,
      formatDate,
      formWorldId,
    };
  }
});
</script>

<style scoped>
.characters-view {
  padding: 2rem;
  background-color: #f8f9fa;
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
  color: #343a40;
}

.list-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.world-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.world-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 0;
  border-bottom: 1px solid #e9ecef;
}
.world-list-item:last-child {
  border-bottom: none;
}

.world-info {
    flex-grow: 1;
    margin-right: 1rem;
}

.world-name-link {
    text-decoration: none;
    color: inherit;
    display: block;
    margin-bottom: 0.25rem;
}
.world-name-link:hover {
   text-decoration: none;
}

.world-name-link h2 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #343a40;
    transition: color 0.2s ease;
    display: inline-block;
}
.world-name-link:hover h2 {
    color: #7851a9;
}

.world-description {
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  color: #6c757d;
  line-height: 1.5;
}

.world-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
}

.world-meta {
    display: block;
    margin-top: 0.75rem;
    font-size: 0.8rem;
    color: #adb5bd;
}

.error-message {
  color: #dc3545;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  text-decoration: none;
}
.btn .icon {
 font-style: normal;
}
.btn:disabled {
    opacity: 0.65;
    cursor: not-allowed;
}
.btn-primary {
  background-color: #7851a9;
  color: white;
}
.btn-primary:not(:disabled):hover {
  background-color: #5f3f87;
}
.btn-secondary {
  background-color: #6c757d;
   color: white;
}
.btn-secondary:not(:disabled):hover {
   background-color: #5a6268;
}
.btn-danger {
  background-color: #dc3545;
  color: white;
}
.btn-danger:not(:disabled):hover {
   background-color: #c82333;
}
.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal {
  background-color: white;
  padding: 0;
  border-radius: 8px;
  min-width: 400px;
  max-width: 600px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  overflow: hidden;
  position: relative;
}

.modal-content {
    padding: 1.5rem 2rem;
}

.modal-content h2 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    font-size: 1.4rem;
    color: #333;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 15px;
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #aaa;
  cursor: pointer;
  line-height: 1;
  padding: 0;
}
.close-button:hover {
    color: #777;
}

.world-selection-list {
    list-style: none;
    padding: 0;
    margin: 1rem 0 0 0;
    max-height: 300px;
    overflow-y: auto;
}

.world-selection-list li {
    margin-bottom: 0.5rem;
}

.world-select-button {
    display: block;
    width: 100%;
    padding: 0.8rem 1rem;
    text-align: left;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    font-size: 1rem;
    color: #343a40;
}

.world-select-button:hover {
    background-color: #e9ecef;
    border-color: #adb5bd;
}

</style> 