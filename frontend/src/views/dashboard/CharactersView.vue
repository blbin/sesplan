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
      <ul v-else class="item-list">
        <li v-for="character in characters" :key="character.id" class="item-list-item">
          <div class="item-info">
            <h2>
              <router-link :to="`/dashboard/characters/${character.id}`" class="item-link">
                {{ character.name }}
              </router-link>
            </h2>
            <p>{{ character.description || 'No description' }}</p>
            <small class="world-info">World: {{ getWorldName(character.world_id) }}</small>
          </div>
          <div class="item-actions">
            <button @click="openEditModal(character)" class="btn btn-secondary btn-sm">Edit</button>
            <button @click="confirmDelete(character)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Modal for Add/Edit Character -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal">
        <h2>{{ editingCharacter ? 'Edit Character' : 'Add New Character' }}</h2>
        <form @submit.prevent="handleSaveCharacter">
          <!-- World Selection (only for creating) -->
          <div v-if="!editingCharacter" class="form-group">
             <label for="characterWorld">World:</label>
             <select id="characterWorld" v-model="characterForm.world_id" required>
                <option disabled value="">Please select a world</option>
                <option v-for="world in availableWorlds" :key="world.id" :value="world.id">
                  {{ world.name }}
                </option>
             </select>
             <p v-if="loadingWorlds">Loading worlds...</p>
             <p v-if="worldError" class="error-message">{{ worldError }}</p>
          </div>

          <div class="form-group">
            <label for="characterName">Name:</label>
            <input type="text" id="characterName" v-model="characterForm.name" required>
          </div>
          <div class="form-group">
            <label for="characterDescription">Description:</label>
            <textarea id="characterDescription" v-model="characterForm.description"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!editingCharacter && !characterForm.world_id">
              {{ editingCharacter ? 'Save Changes' : 'Create Character' }}
            </button>
          </div>
           <p v-if="formError" class="error-message">{{ formError }}</p>
        </form>
      </div>
    </div>

     <!-- Modal for Delete Confirmation -->
    <div v-if="characterToDelete" class="modal-backdrop">
      <div class="modal confirmation-modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete the character "{{ characterToDelete.name }}"?</p>
         <div class="modal-actions">
            <button type="button" @click="characterToDelete = null" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="handleDeleteCharacter" class="btn btn-danger">Delete</button>
          </div>
           <p v-if="deleteError" class="error-message">{{ deleteError }}</p>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from 'vue';
import * as charactersApi from '@/services/api/characters';
import * as worldsApi from '@/services/api/worlds';
import type { Character, CharacterCreate, CharacterUpdate } from '@/types/character';
import type { World } from '@/types/world';

interface CharacterFormData {
  name: string;
  description: string | null;
  world_id: number | null;
}

export default defineComponent({
  name: 'CharactersView',
  setup() {
    const characters = ref<Character[]>([]);
    const availableWorlds = ref<World[]>([]);
    const loading = ref(true);
    const loadingWorlds = ref(false);
    const error = ref<string | null>(null);
    const worldError = ref<string | null>(null);
    const formError = ref<string | null>(null);
    const deleteError = ref<string | null>(null);

    const showModal = ref(false);
    const editingCharacter = ref<Character | null>(null);
    const characterToDelete = ref<Character | null>(null);

    const characterForm = reactive<CharacterFormData>({
      name: '',
      description: null,
      world_id: null
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

    const loadWorlds = async () => {
        loadingWorlds.value = true;
        worldError.value = null;
        try {
            // Fetch worlds the user OWNS to allow character creation
            availableWorlds.value = await worldsApi.getWorlds();
        } catch (err: any) {
            worldError.value = `Failed to load worlds: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
            console.error("Load Worlds Error:", err);
        } finally {
            loadingWorlds.value = false;
        }
    };

    const resetForm = () => {
      characterForm.name = '';
      characterForm.description = null;
      characterForm.world_id = null;
      editingCharacter.value = null;
      formError.value = null;
    };

    const closeModal = () => {
      showModal.value = false;
      resetForm();
    };

     const openAddModal = () => {
        resetForm();
        editingCharacter.value = null;
        showModal.value = true;
        // Load worlds only if needed and not already loaded
        if (availableWorlds.value.length === 0 && !loadingWorlds.value) {
            loadWorlds();
        }
    };

     const openEditModal = (character: Character) => {
      editingCharacter.value = character;
      characterForm.name = character.name;
      characterForm.description = character.description;
      characterForm.world_id = character.world_id; // Keep world_id for reference
      showModal.value = true;
    };

    const getWorldName = (worldId: number): string => {
        // Try finding world in already loaded list first
        const world = availableWorlds.value.find(w => w.id === worldId);
        // If not found (e.g., world list wasn't loaded yet or character belongs to another world)
        // just return the ID. A better approach might be to fetch world names on demand.
        return world ? world.name : `ID: ${worldId}`;
    };

    const handleSaveCharacter = async () => {
       formError.value = null;
       try {
         if (editingCharacter.value) {
           // Update
           const characterDataToUpdate: CharacterUpdate = {};
           if (characterForm.name !== editingCharacter.value.name) {
               characterDataToUpdate.name = characterForm.name;
           }
           if (characterForm.description !== editingCharacter.value.description) {
               characterDataToUpdate.description = characterForm.description;
           }
           // Only send update if something changed
           if (Object.keys(characterDataToUpdate).length > 0) {
                const updatedCharacter = await charactersApi.updateCharacter(editingCharacter.value.id, characterDataToUpdate);
                const index = characters.value.findIndex(c => c.id === updatedCharacter.id);
                if (index !== -1) {
                    characters.value[index] = updatedCharacter;
                }
           } else {
               console.log("No changes detected for update.");
           }
         } else {
           // Create
           if (!characterForm.name.trim()) {
                formError.value = "Character name cannot be empty.";
                return;
           }
           if (!characterForm.world_id) {
               formError.value = "Please select a world for the character.";
               return;
           }
           const newCharacterData: CharacterCreate = {
               name: characterForm.name,
               description: characterForm.description,
               world_id: characterForm.world_id
           };
           const newCharacter = await charactersApi.createCharacter(newCharacterData);
           characters.value.push(newCharacter);
           // If world list wasn't loaded before, load it now to display name
           if (availableWorlds.value.length === 0) loadWorlds();
         }
         closeModal();
       } catch(err: any) {
          formError.value = `Save failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
          console.error("Save Character Error:", err);
       }
    };

    const confirmDelete = (character: Character) => {
        characterToDelete.value = character;
        deleteError.value = null;
    };

    const handleDeleteCharacter = async () => {
      if (!characterToDelete.value) return;
      deleteError.value = null;
      try {
          await charactersApi.deleteCharacter(characterToDelete.value.id);
          characters.value = characters.value.filter(c => c.id !== characterToDelete.value!.id);
          characterToDelete.value = null;
      } catch (err: any) {
           deleteError.value = `Delete failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
           console.error("Delete Character Error:", err);
      }
    };

    onMounted(() => {
        loadCharacters();
        // Optional: Pre-load worlds if the list is often needed immediately
        // loadWorlds();
    });

    return {
      characters,
      availableWorlds,
      loading,
      loadingWorlds,
      error,
      worldError,
      formError,
      deleteError,
      showModal,
      editingCharacter,
      characterToDelete,
      characterForm,
      closeModal,
      openAddModal,
      openEditModal,
      getWorldName,
      handleSaveCharacter,
      confirmDelete,
      handleDeleteCharacter,
    };
  }
});
</script>

<style scoped>
/* Using similar styles as CampaignsView / WorldsView for consistency */
.characters-view {
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

.list-container {
  background-color: #fff;
  padding: 1.5rem 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}

.item-list-item:last-child {
  border-bottom: none;
}

.item-info h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.2rem;
}

.item-info p {
  margin: 0 0 0.5rem 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.item-link {
    text-decoration: none;
    color: #007bff; /* Link color */
}
.item-link:hover {
    text-decoration: underline;
}

.world-info {
    font-size: 0.8rem;
    color: #888;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal Styles (basic - reuse/adapt from other views) */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 2rem;
  border-radius: 0.5rem;
  min-width: 400px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  box-sizing: border-box;
}

.form-group textarea {
    min-height: 80px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.confirmation-modal p {
    margin-bottom: 1.5rem;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 0.8rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
  margin-top: 1rem;
}

/* Button styles (reuse/adapt) */
.btn { padding: 0.5rem 1rem; border-radius: 0.3rem; cursor: pointer; border: none; font-weight: 500; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }

</style> 