<template>
  <div class="characters-view">
    <header class="view-header">
      <h1>Characters</h1>
      <button @click="openAddModal" class="btn btn-primary">
        <i class="icon">+</i> Add New Character
      </button>
    </header>

    <div class="list-container">
      <p v-if="loading">Loading characters...</p>
      <p v-else-if="error" class="error-message">{{ error }}</p>
      <div v-else-if="characters.length === 0">No characters found for this world.</div>
      <ul v-else class="item-list">
        <li v-for="character in characters" :key="character.id" class="item-list-item">
          <div class="item-info">
            <h2>
              <router-link :to="`/dashboard/characters/${character.id}`" class="item-link">
                {{ character.name }}
              </router-link>
            </h2>
            <p>{{ character.description || 'No description' }}</p>
          </div>
          <div class="item-actions">
            <button @click="openEditModal(character)" class="btn btn-secondary btn-sm">Edit</button>
            <button @click="confirmDelete(character)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Modal for Add/Edit Character -->
    <div v-if="showModal && numericWorldId" class="modal-backdrop">
      <div class="modal">
         <CreateCharacterForm
            :worldId="numericWorldId"
            :characterToEdit="editingCharacter"
            :availableTagTypes="characterTagTypes"
            @saved="handleCharacterSaved"
            @cancel="closeModal"
         />
      </div>
    </div>

     <!-- Modal for Delete Confirmation -->
    <div v-if="characterToDelete" class="modal-backdrop">
      <div class="modal confirmation-modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete the character "{{ characterToDelete?.name }}"?</p>
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
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import * as charactersApi from '@/services/api/characters';
import type { Character } from '@/types/character';
import type { CharacterTagType } from '@/types/characterTagType';
import CreateCharacterForm from '@/components/dashboard/CreateCharacterForm.vue';
import * as characterTagTypeApi from '@/services/api/characterTagTypeService';

export default defineComponent({
  name: 'CharactersView',
  components: { CreateCharacterForm },
  setup() {
    const route = useRoute();
    const characters = ref<Character[]>([]);
    const characterTagTypes = ref<CharacterTagType[]>([]);
    const loading = ref(true);
    const loadingTagTypes = ref(false);
    const error = ref<string | null>(null);
    const tagTypesError = ref<string | null>(null);
    const deleteError = ref<string | null>(null);

    const showModal = ref(false);
    const editingCharacter = ref<Character | null>(null);
    const characterToDelete = ref<Character | null>(null);

    const worldIdRef = computed(() => route.params.worldId as string | undefined);
    const numericWorldId = computed(() => {
      const id = Number(worldIdRef.value);
      return !isNaN(id) && id > 0 ? id : null;
    });

    const loadCharacters = async () => {
      if (!numericWorldId.value) {
        error.value = "Invalid World ID.";
        loading.value = false;
        characters.value = [];
        return;
      }
      loading.value = true;
      error.value = null;
      try {
        characters.value = await charactersApi.getAllWorldCharacters(numericWorldId.value);
      } catch (err: any) {
        error.value = `Failed to load characters: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Load Characters Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const loadCharacterTagTypes = async () => {
        if (!numericWorldId.value) return;
        loadingTagTypes.value = true;
        tagTypesError.value = null;
        try {
            characterTagTypes.value = await characterTagTypeApi.getCharacterTagTypes(numericWorldId.value);
        } catch (err: any) {
            tagTypesError.value = `Failed to load character tags: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
            console.error("Load Character Tag Types Error:", err);
        } finally {
            loadingTagTypes.value = false;
        }
    };

    const closeModal = () => {
      showModal.value = false;
      editingCharacter.value = null;
    };

     const openAddModal = () => {
        if (!numericWorldId.value) return;
        editingCharacter.value = null;
        showModal.value = true;
        if (characterTagTypes.value.length === 0 && !loadingTagTypes.value) {
            loadCharacterTagTypes();
        }
    };

     const openEditModal = (character: Character) => {
      if (!numericWorldId.value) return;
      editingCharacter.value = character;
      showModal.value = true;
      if (characterTagTypes.value.length === 0 && !loadingTagTypes.value) {
            loadCharacterTagTypes();
        }
    };

    const handleCharacterSaved = (_savedCharacter: Character) => {
        loadCharacters();
        closeModal();
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
          loadCharacters();
          characterToDelete.value = null;
      } catch (err: any) {
           deleteError.value = `Delete failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
           console.error("Delete Character Error:", err);
      }
    };

    onMounted(() => {
        if (numericWorldId.value) {
            loadCharacters();
            loadCharacterTagTypes();
        } else {
            error.value = "World ID not found in route.";
            loading.value = false;
        }
    });

    return {
      characters,
      characterTagTypes,
      loading,
      loadingTagTypes,
      error,
      tagTypesError,
      deleteError,
      showModal,
      editingCharacter,
      characterToDelete,
      numericWorldId,
      closeModal,
      openAddModal,
      openEditModal,
      handleCharacterSaved,
      confirmDelete,
      handleDeleteCharacter,
    };
  }
});
</script>

<style scoped>
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
    color: #007bff;
}
.item-link:hover {
    text-decoration: underline;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

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
  padding: 0;
  border-radius: 0.5rem;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  overflow: hidden;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 0 1.5rem 1.5rem;
}

.confirmation-modal {
    padding: 2rem;
    max-width: 450px;
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
  margin: 1rem 1.5rem;
}

.btn { padding: 0.5rem 1rem; border-radius: 0.3rem; cursor: pointer; border: none; font-weight: 500; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }

</style> 