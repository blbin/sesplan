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
        <router-link 
          v-if="character.world_id" 
          :to="{ 
            name: 'dashboard-world-detail', 
            params: { worldId: character.world_id },
            query: { tab: 'characters' }
          }" 
          class="btn btn-secondary"
         >
           Back to World (Characters)
         </router-link>
        <button @click="openEditCharacterModal" class="btn btn-primary">Edit Character</button>
      </header>

      <div class="details-section">
        <h2>Details</h2>
        <!-- Inline Description Edit -->
        <div class="description-section">
          <div class="description-header">
            <strong>Description:</strong>
            <v-btn 
              v-if="!isEditingDescription"
              icon="mdi-pencil" 
              variant="text" 
              size="x-small" 
              @click="startEditingDescription"
              class="ml-2"
              title="Edit Description"
            ></v-btn>
          </div>
          
          <div v-if="!isEditingDescription" class="description-content mt-2" v-html="renderedDescription"></div>
          
          <div v-else class="description-editor mt-2">
            <MarkdownEditor v-model="editableDescription" />
            <div v-if="saveDescriptionError" class="error-message mt-2">{{ saveDescriptionError }}</div>
            <div class="editor-actions mt-2">
              <v-btn 
                size="small" 
                @click="cancelDescriptionEdit"
                :disabled="isSavingDescription"
              >Cancel</v-btn>
              <v-btn 
                color="primary" 
                size="small" 
                @click="saveDescription"
                :loading="isSavingDescription"
                :disabled="!isDescriptionChanged"
              >Save</v-btn>
            </div>
          </div>
        </div>
        <!-- End Inline Description Edit -->

        <!-- Display World Name or ID -->
        <p class="mt-4">
           <strong>World:</strong> 
           <span v-if="detailsLoading"> Loading...</span>
           <router-link v-else-if="world" :to="{ name: 'dashboard-world-detail', params: { worldId: world.id } }">{{ world.name }}</router-link>
           <span v-else-if="detailsError && !world"> Error loading world</span>
           <span v-else>{{ character.world_id }} (Not found)</span>
        </p>
        <!-- Display Owner Username or ID -->
        <p>
           <strong>Owner:</strong> 
           <span v-if="detailsLoading"> Loading...</span>
           <span v-else-if="owner">{{ owner.username }}</span>
           <span v-else-if="detailsError && !owner"> Error loading owner</span>
           <span v-else>{{ character.user_id }} (Not found)</span>
        </p>
        <p><strong>Created:</strong> {{ formatDate(character.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDate(character.updated_at) }}</p>
        <div v-if="detailsError" class="error-message small">{{ detailsError }}</div>
      </div>

      <!-- Character Tags Section -->
      <div class="details-section tags-section">
        <h2>Tags</h2>
        <div v-if="character.tags && character.tags.length > 0" class="tags-container">
          <span v-for="tag in character.tags" :key="tag.id" class="tag-chip">
            {{ tag.tag_type?.name || `Tag ID: ${tag.character_tag_type_id}` }}
          </span>
        </div>
        <p v-else>No tags assigned.</p>
        <button @click="openTagEditDialog" class="btn btn-secondary mt-2">Edit Tags</button>
      </div>

      <!-- Manage Character Tag Types -->
      <div class="details-section">
         <div class="section-header">
           <h2>Manage Character Tag Types</h2>
           <button @click="openAddTagTypeDialog" class="btn btn-primary">Add Tag Type</button>
         </div>
 
         <div v-if="tagTypesLoading" class="loading-state">Loading tag types...</div>
         <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
         <div v-else-if="availableTagTypes.length > 0" class="tag-types-list">
           <div v-for="tagType in availableTagTypes" :key="tagType.id" class="tag-type-item">
             <span class="tag-type-name">{{ tagType.name }}</span>
             <div class="tag-type-actions">
               <button @click="openEditTagTypeDialog(tagType)" class="btn-icon">✏️</button>
               <button @click="confirmDeleteTagType(tagType)" class="btn-icon">🗑️</button>
             </div>
           </div>
         </div>
         <div v-else class="empty-state">No character tag types defined for this world yet.</div>
       </div>

       <!-- Related Sections (Journal, Items etc.) -->
       <div class="related-sections">
            <section class="journal-section details-section">
               <CharacterJournalTab v-if="numericCharacterId" :character-id="numericCharacterId" />
            </section>
            <!-- Items Section -->
            <section class="details-section items-section">
                <h3>Items</h3>
                <div v-if="itemsLoading" class="loading-message small">Loading items...</div>
                <div v-else-if="itemsError" class="error-message small">{{ itemsError }}</div>
                <div v-else-if="characterItems.length === 0" class="info-message small">This character has no items.</div>
                <ul v-else class="item-list">
                    <li v-for="item in characterItems" :key="item.id" class="item-list-item">
                        <div class="item-info">
                            <!-- TODO: Link to item detail when available -->
                            <h4>{{ item.name }}</h4> 
                            <p v-if="item.description">{{ item.description }}</p>
                        </div>
                        <!-- TODO: Add actions (unequip/drop?) when implemented -->
                    </li>
                </ul>
                <!-- TODO: Add button to add existing/create new item? -->
            </section>
       </div>

    </div>
    <div v-else>
        <p>Character not found.</p>
         <router-link :to="{ name: 'dashboard-characters' }" class="btn btn-secondary">Back to Characters</router-link>
    </div>

    <!-- Edit Character Modal -->
     <div v-if="showEditCharacterModal" class="modal-overlay">
       <div class="modal-container">
         <div class="modal-header">
           <h3>Edit Character</h3>
           <button @click="closeEditCharacterModal" class="close-btn">&times;</button>
         </div>
         <div class="modal-body">
           <CreateCharacterForm 
             v-if="character?.world_id" 
             :worldId="character.world_id" 
             :characterToEdit="character" 
             @saved="handleCharacterSaved" 
             @cancel="closeEditCharacterModal"
           />
           <div v-else>Error: Missing world ID.</div>
         </div>
       </div>
     </div>

    <!-- Edit Character Tags Modal -->
      <div v-if="showTagEditDialog" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Edit Tags for {{ character?.name }}</h3>
            <button @click="closeTagEditDialog" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="tagTypesLoading">Loading tag types...</div>
            <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
            <div v-else>
              <div class="form-group">
                <label>Select Tags:</label>
                <div class="tag-checkboxes">
                  <div v-for="tagType in availableTagTypes" :key="tagType.id" class="tag-checkbox">
                    <input 
                      type="checkbox" 
                      :id="'char-tag-' + tagType.id" 
                      :value="tagType.id" 
                      v-model="selectedTagTypeIds"
                    >
                    <label :for="'char-tag-' + tagType.id">{{ tagType.name }}</label>
                  </div>
                </div>
                <div v-if="availableTagTypes.length === 0" class="empty-tags-message">
                  No character tag types available. Create some first.
                </div>
              </div>
              <div v-if="tagSyncError" class="error-message">{{ tagSyncError }}</div>
              <div class="form-actions">
                <button @click="closeTagEditDialog" class="btn btn-secondary">Cancel</button>
                <button 
                  @click="saveTags" 
                  class="btn btn-primary" 
                  :disabled="tagTypesLoading || isSavingTags"
                >
                  {{ isSavingTags ? 'Saving...' : 'Save Tags' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Character Tag Type Modal -->
      <div v-if="showTagTypeDialog" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ editingTagType ? 'Edit Character Tag Type' : 'Add Character Tag Type' }}</h3>
            <button @click="closeTagTypeDialog" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="charTagTypeName">Tag Type Name:</label>
              <input 
                type="text" 
                id="charTagTypeName" 
                v-model="tagTypeName" 
                class="form-control" 
                :class="{ 'error': tagTypeDialogError }"
                @keyup.enter="saveTagType"
              >
              <div v-if="tagTypeDialogError" class="error-message">{{ tagTypeDialogError }}</div>
            </div>
            <div class="form-actions">
              <button @click="closeTagTypeDialog" class="btn btn-secondary">Cancel</button>
              <button 
                @click="saveTagType" 
                class="btn btn-primary" 
                :disabled="!tagTypeName || isSavingTagType"
              >
                {{ isSavingTagType ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Character Tag Type Confirmation Modal -->
      <div v-if="showDeleteTagTypeConfirm" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Confirm Delete Tag Type</h3>
            <button @click="cancelDeleteTagType" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete tag type "{{ tagTypeToDelete?.name }}"?</p>
            <div v-if="deleteTagTypeError" class="error-message">{{ deleteTagTypeError }}</div>
            <div class="form-actions">
              <button @click="cancelDeleteTagType" class="btn btn-secondary">Cancel</button>
              <button 
                @click="executeDeleteTagType" 
                class="btn btn-danger" 
                :disabled="isDeletingTagType"
              >
                {{ isDeletingTagType ? 'Deleting...' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import * as charactersApi from '@/services/api/characters';
import * as characterTagTypeApi from '@/services/api/characterTagTypeService'; // Import Character Tag Type API
import * as characterTagApi from '@/services/api/characterTagService'; // Import Character Tag API
import * as itemsApi from '@/services/api/items'; // Import items API
import * as worldsApi from '@/services/api/worlds'; // Import worlds API
import * as usersApi from '@/services/api/users'; // Import users API
import type { Character, CharacterUpdate } from '@/types/character';
import type { CharacterTagType } from '@/types/characterTagType'; // Import Character Tag Type
import CreateCharacterForm from '@/components/dashboard/CreateCharacterForm.vue'; // Updated path
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'; // Import editor
import MarkdownIt from 'markdown-it'; // Import renderer
import CharacterJournalTab from '@/components/dashboard/CharacterJournalTab.vue'; // Import the new component
import { VBtn, VProgressCircular, VAlert } from 'vuetify/components'; // Add necessary Vuetify components
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
import type { Item } from '@/types/item'; // Import Item type
import type { World } from '@/types/world'; // Import World type
import type { User } from '@/types/user'; // Import User type

export default defineComponent({
  name: 'CharacterDetailView',
  components: {
    VBtn, VProgressCircular, VAlert, // Register Vuetify components
    CreateCharacterForm,
    ConfirmDeleteModal,
    CharacterJournalTab, 
    MarkdownEditor, // Register MarkdownEditor
  },
  setup() {
    const route = useRoute();
    const character = ref<Character | null>(null);
    const loading = ref(true);
    const error = ref<string | null>(null);
    
    // Description Editing State
    const isEditingDescription = ref(false);
    const editableDescription = ref('');
    const isSavingDescription = ref(false);
    const saveDescriptionError = ref<string | null>(null);

    // Tag related state
    const showTagEditDialog = ref(false); // Restore
    const availableTagTypes = ref<CharacterTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]);
    const isSavingTags = ref(false);
    const tagSyncError = ref<string | null>(null);

    // Tag Type Management Modal State
    const showTagTypeDialog = ref(false);
    const editingTagType = ref<CharacterTagType | null>(null);
    const isSavingTagType = ref(false);
    const tagTypeName = ref(''); // Added for the form inside the modal
    const tagTypeDialogError = ref<string | null>(null);

    // Delete Tag Type Confirmation Modal State
    const showDeleteTagTypeConfirm = ref(false);
    const tagTypeToDelete = ref<CharacterTagType | null>(null);
    const isDeletingTagType = ref(false);
    const deleteTagTypeError = ref<string | null>(null);

    // Character Edit Modal State
    const showEditCharacterModal = ref(false);

    // Items State
    const characterItems = ref<Item[]>([]);
    const itemsLoading = ref(false);
    const itemsError = ref<string | null>(null);

    // State for loaded World and User data
    const world = ref<World | null>(null);
    const owner = ref<User | null>(null);
    const detailsLoading = ref(false); // Combined loading state for world/user
    const detailsError = ref<string | null>(null);

    const characterIdRef = computed(() => route.params.characterId as string | undefined);
    const numericCharacterId = computed(() => {
      const id = Number(characterIdRef.value);
      return !isNaN(id) && id > 0 ? id : null;
    });

    // Initialize markdown-it (assuming it's defined above or imported)
    const md = new MarkdownIt({ html: false, linkify: true, typographer: true }); 
    const renderedDescription = computed(() => {
      return character.value?.description ? md.render(character.value.description) : '<p><em>No description provided.</em></p>';
    });
    const isDescriptionChanged = computed(() => character.value?.description !== editableDescription.value);

    // --- Fetching Data ---
    const fetchCharacterDetails = async () => {
      if (!numericCharacterId.value) {
          error.value = "Invalid Character ID.";
          loading.value = false;
          return;
      }
      loading.value = true;
      error.value = null;
      world.value = null; // Reset world/owner
      owner.value = null;
      detailsError.value = null;
      try {
        character.value = await charactersApi.getCharacterById(numericCharacterId.value);
        console.log('Character data received from API:', character.value); 
        
        // Fetch world and owner details in parallel after character is loaded
        if (character.value) {
             detailsLoading.value = true;
             const worldId = character.value.world_id;
             const ownerId = character.value.user_id;
             
             const promises = [];
             if (worldId) {
                 promises.push(worldsApi.getWorldById(worldId));
             } else {
                 promises.push(Promise.resolve(null)); // Placeholder if no worldId
             }
             if (ownerId) {
                 promises.push(usersApi.getUserById(ownerId));
             } else {
                 promises.push(Promise.resolve(null)); // Placeholder if no ownerId
             }

             // Also fetch items
             promises.push(fetchCharacterItems()); // Assuming this returns a promise
             // Also fetch available tag types (needs worldId)
             if(worldId) {
                promises.push(loadAvailableTagTypes(worldId)); // Pass worldId
             } else {
                console.warn("Cannot load tag types, worldId missing from character.");
             }

             try {
                 const results = await Promise.allSettled(promises);
                 
                 // Process World result
                 if (results[0].status === 'fulfilled' && results[0].value) {
                     world.value = results[0].value as World;
                 } else if (results[0].status === 'rejected') {
                     console.error("Fetch World Error:", results[0].reason);
                     detailsError.value = 'Failed to load world details. ';
                 }

                 // Process Owner result
                 if (results[1].status === 'fulfilled' && results[1].value) {
                     owner.value = results[1].value as User;
                 } else if (results[1].status === 'rejected') {
                     console.error("Fetch Owner Error:", results[1].reason);
                     detailsError.value = (detailsError.value || '') + 'Failed to load owner details.';
                 }

                 // Errors from fetchCharacterItems and loadAvailableTagTypes are handled internally in those functions

             } catch (settledError) {
                  // This catch block is less likely needed with Promise.allSettled
                  console.error("Error processing details promises:", settledError);
                  detailsError.value = "An unexpected error occurred loading details.";
             } finally {
                 detailsLoading.value = false;
             }
        }
        // ... tag pre-filling, description setup (can stay here) ...
        selectedTagTypeIds.value = character.value?.tags?.map(t => t.character_tag_type_id) || [];
        editableDescription.value = character.value?.description || '';

      } catch (err: any) {
        error.value = `Failed to load character: ${err.response?.data?.detail || err.message}`;
        console.error("Load Character Error:", err);
      } finally {
        loading.value = false; // Main character loading finished
      }
    };

    // Modified loadAvailableTagTypes to accept worldId
    const loadAvailableTagTypes = async (worldId: number) => {
        if (!worldId) return;
        tagTypesLoading.value = true;
        tagTypesError.value = null;
        try {
            availableTagTypes.value = await characterTagTypeApi.getCharacterTagTypes(worldId);
        } catch (err: any) {
            console.error('Error loading character tag types:', err);
            tagTypesError.value = `Failed to load tag types: ${err.message}`;
        } finally {
            tagTypesLoading.value = false;
        }
    };

    const fetchCharacterItems = async () => {
        if (!character.value || !character.value.world_id) {
            itemsError.value = "Cannot load items: Character or World ID missing.";
            return;
        }
        itemsLoading.value = true;
        itemsError.value = null;
        try {
            characterItems.value = await itemsApi.getItemsByWorld(
                character.value.world_id, 
                character.value.id // Filter by character ID
            );
        } catch (err: any) {
            console.error("Fetch Character Items Error:", err);
            itemsError.value = `Failed to load items: ${err.message}`;
        } finally {
            itemsLoading.value = false;
        }
    };

    const formatDate = (dateString: string | null): string => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString();
        } catch (e) {
            return dateString;
        }
    };

    // --- Description Editing Functions ---
    const startEditingDescription = () => {
        editableDescription.value = character.value?.description || '';
        isEditingDescription.value = true;
        saveDescriptionError.value = null;
    };

    const cancelDescriptionEdit = () => {
        isEditingDescription.value = false;
        saveDescriptionError.value = null;
    };

    const saveDescription = async () => {
        if (!numericCharacterId.value || !isDescriptionChanged.value) return;
        isSavingDescription.value = true;
        saveDescriptionError.value = null;
        try {
            const updatePayload: CharacterUpdate = { description: editableDescription.value };
            const updatedCharacter = await charactersApi.updateCharacter(numericCharacterId.value, updatePayload);
            // Update local state
            if (character.value) {
                character.value.description = updatedCharacter.description;
                character.value.updated_at = updatedCharacter.updated_at;
            }
            isEditingDescription.value = false;
        } catch (err: any) {
            console.error('Error saving description:', err);
            saveDescriptionError.value = `Failed to save: ${err.message}`;
        } finally {
            isSavingDescription.value = false;
        }
    };

    // --- Character Edit Modal Functions ---
    const openEditCharacterModal = () => { showEditCharacterModal.value = true; };
    const closeEditCharacterModal = () => { showEditCharacterModal.value = false; };
    const handleCharacterSaved = () => {
        closeEditCharacterModal();
        fetchCharacterDetails(); 
    };

    // --- Tag Assignment Modal Functions ---
    const openTagEditDialog = () => {
        if (!character.value || !character.value.world_id) return;
        selectedTagTypeIds.value = character.value.tags?.map(t => t.character_tag_type_id) || [];
        // Load types if needed
        if (availableTagTypes.value.length === 0 || tagTypesError.value) {
          loadAvailableTagTypes(character.value.world_id); // Ensure correct function name is used
        }
        tagSyncError.value = null;
        showTagEditDialog.value = true; 
    };
    
    const closeTagEditDialog = () => { showTagEditDialog.value = false; };

    const saveTags = async () => {
        if (!character.value) return;
        isSavingTags.value = true;
        tagSyncError.value = null;

        const originalTagTypeIds = new Set(character.value.tags?.map(t => t.character_tag_type_id) || []);
        const currentTagTypeIds = new Set(selectedTagTypeIds.value);

        const tagsToAdd = selectedTagTypeIds.value.filter(id => !originalTagTypeIds.has(id));
        const tagsToRemove = [...originalTagTypeIds].filter(id => !currentTagTypeIds.has(id));

        const addPromises = tagsToAdd.map(tagTypeId => 
          characterTagApi.addTagToCharacter(character.value!.id, tagTypeId)
        );
        const removePromises = tagsToRemove.map(tagTypeId => 
          characterTagApi.removeTagFromCharacter(character.value!.id, tagTypeId)
        );
        
        try {
            await Promise.all([...addPromises, ...removePromises]);
            closeTagEditDialog();
            fetchCharacterDetails(); // Refresh character to show updated tags
        } catch (err: any) {
            console.error("Error syncing character tags:", err);
            tagSyncError.value = `Failed to save tags: ${err.message || 'Unknown error'}`;
        } finally {
            isSavingTags.value = false;
        }
    };

    // --- Tag Type Management Functions ---
    const openAddTagTypeDialog = () => {
        editingTagType.value = null;
        tagTypeName.value = '';
        tagTypeDialogError.value = null;
        showTagTypeDialog.value = true;
    };

    const openEditTagTypeDialog = (tagType: CharacterTagType) => {
        editingTagType.value = tagType;
        tagTypeName.value = tagType.name;
        tagTypeDialogError.value = null;
        showTagTypeDialog.value = true;
    };

    const closeTagTypeDialog = () => { 
        showTagTypeDialog.value = false; 
        editingTagType.value = null;
        tagTypeName.value = ''; // Clear name on close
    };

    const saveTagType = async () => {
        if (!tagTypeName.value || !character.value?.world_id) {
            tagTypeDialogError.value = "Character or World ID is missing.";
            return;
        }
        const worldId = character.value.world_id; // Guaranteed to be number here
        isSavingTagType.value = true;
        tagTypeDialogError.value = null;
        try {
            if (editingTagType.value) {
                const updateData = { name: tagTypeName.value };
                await characterTagTypeApi.updateCharacterTagType(worldId, editingTagType.value.id, updateData);
            } else {
                const createData = { name: tagTypeName.value };
                await characterTagTypeApi.createCharacterTagType(worldId, createData);
            }
            closeTagTypeDialog();
            await loadAvailableTagTypes(worldId); // Ensure correct function name is used
        } catch (err: any) {
            console.error('Error saving character tag type:', err);
            tagTypeDialogError.value = `Save failed: ${err.message}`;
        } finally {
            isSavingTagType.value = false;
        }
    };

    // --- Delete Tag Type Functions ---
    const confirmDeleteTagType = (tagType: CharacterTagType) => {
        tagTypeToDelete.value = tagType;
        deleteTagTypeError.value = null;
        showDeleteTagTypeConfirm.value = true;
    };

    const cancelDeleteTagType = () => {
        showDeleteTagTypeConfirm.value = false;
        tagTypeToDelete.value = null;
    };

    const executeDeleteTagType = async () => {
        if (!tagTypeToDelete.value || !character.value?.world_id) {
            deleteTagTypeError.value = "Cannot delete: Character, World ID, or Tag Type is missing.";
            return;
        }
        const worldId = character.value.world_id; // Guaranteed to be number here
        isDeletingTagType.value = true;
        deleteTagTypeError.value = null;
        try {
            await characterTagTypeApi.deleteCharacterTagType(worldId, tagTypeToDelete.value.id);
            cancelDeleteTagType(); 
            await loadAvailableTagTypes(worldId); // Ensure correct function name is used
            fetchCharacterDetails(); 
        } catch (err: any) {
            console.error('Error deleting character tag type:', err);
            deleteTagTypeError.value = `Delete failed: ${err.message}`;
        } finally {
            isDeletingTagType.value = false;
        }
    };

    // --- Lifecycle Hook ---
    onMounted(() => {
      fetchCharacterDetails(); // This now fetches character, world, owner, items, and tag types
    });

    return {
      character,
      loading,
      error,
      numericCharacterId,
      formatDate, 
      // Description Editing
      renderedDescription,
      isEditingDescription,
      editableDescription,
      isSavingDescription,
      saveDescriptionError,
      startEditingDescription,
      cancelDescriptionEdit,
      saveDescription,
      isDescriptionChanged,
      // Tag Assignment
      availableTagTypes,
      tagTypesLoading,
      tagTypesError,
      selectedTagTypeIds,
      isSavingTags,
      tagSyncError,
      showTagEditDialog, 
      openTagEditDialog, 
      closeTagEditDialog, 
      saveTags, 
      // Character Edit Modal
      showEditCharacterModal,
      openEditCharacterModal,
      closeEditCharacterModal,
      handleCharacterSaved,
      // Tag Type Management
      showTagTypeDialog,
      editingTagType,
      isSavingTagType,
      tagTypeName,
      tagTypeDialogError,
      openAddTagTypeDialog,
      openEditTagTypeDialog,
      closeTagTypeDialog,
      saveTagType,
      // Delete Tag Type Modal
      showDeleteTagTypeConfirm,
      tagTypeToDelete,
      isDeletingTagType,
      deleteTagTypeError,
      confirmDeleteTagType,
      cancelDeleteTagType,
      executeDeleteTagType,
      // Items
      characterItems,
      itemsLoading,
      itemsError,
      // World and Owner Details
      world,             // Add world
      owner,             // Add owner
      detailsLoading,    // Add detailsLoading
      detailsError,      // Add detailsError
    };
  },
});
</script>

<style scoped>
/* Using similar styles to LocationDetailView for consistency */
.character-detail-view {
  padding: 1rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.view-header h1 {
  margin: 0;
  font-size: 2rem;
}

.details-section {
  margin-bottom: 2rem;
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.details-section h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  color: #333;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.loading-message,
.error-message,
.loading-state,
.empty-state {
  padding: 1rem; /* Adjusted padding */
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  margin-top: 1rem; /* Added margin */
}

.error-message {
  color: #dc3545;
  border: 1px solid #f5c6cb;
}

.error-message.small {
  padding: 0.5rem;
  font-size: 0.9rem;
}

.loading-message.small {
  padding: 0.5rem;
  font-size: 0.9rem;
  color: #6c757d;
}

/* Tag styles */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag-chip {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: #e9ecef;
  border-radius: 4px;
  font-size: 0.875rem;
}

.tag-types-list {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.tag-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.tag-type-item:last-child {
  border-bottom: none;
}

.tag-type-name {
  font-weight: 500;
}

.tag-type-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  border-radius: 4px;
}

.btn-icon:hover {
  background-color: #f0f0f0;
}

.related-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.journal-entries-section h3,
.related-sections section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  color: #495057;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.entry-list {
  list-style: none;
  padding: 0;
}

.item-list-item {
  display: flex;
  justify-content: space-between;
  align-items: start;
  border-bottom: 1px solid #eee;
  padding: 1rem 0;
}
.item-list-item:last-child {
  border-bottom: none;
}

.item-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}
.item-info p {
  margin: 0 0 0.5rem 0;
  color: #555;
}
.item-info small {
  color: #888;
  font-size: 0.85rem;
}

.item-actions {
    display: flex;
    gap: 0.5rem;
  margin-left: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  white-space: nowrap; /* Prevent wrapping */
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  text-decoration: none;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}
.btn-danger:hover {
  background-color: #c82333;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mt-2 {
  margin-top: 0.5rem;
}

/* Modal styles (consistent with LocationDetailView) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3,
.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.close-btn:hover {
  color: #343a40;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.form-control.error {
  border-color: #dc3545;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.tag-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.75rem;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tag-checkbox input {
  margin: 0;
}

.empty-tags-message {
  padding: 1rem;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

/* Add styles similar to LocationDetailView */
.description-section {
  position: relative;
  margin-bottom: 1rem; 
}

.description-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.description-header strong {
  margin-right: auto; 
}

.description-editor {
  border: 1px solid #e0e0e0;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f9f9f9; 
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.mt-4 {
    margin-top: 1.5rem; 
}

.items-section h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    color: #495057;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.5rem;
 }

 .info-message.small {
    font-size: 0.9rem;
    color: #6c757d;
    padding: 0.5rem 0;
 }

 /* Reusing item list styles */

</style> 