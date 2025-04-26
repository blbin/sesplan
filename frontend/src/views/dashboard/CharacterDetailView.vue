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
        <router-link v-if="character.world_id" :to="{ name: 'dashboard-world-detail', params: { worldId: character.world_id } }" class="btn btn-secondary">Back to World</router-link>
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

        <p class="mt-4"><strong>World ID:</strong> {{ character.world_id }}</p>
        <p><strong>Owner ID:</strong> {{ character.user_id }}</p>
        <p><strong>Created:</strong> {{ formatDate(character.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDate(character.updated_at) }}</p>
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
            <!-- Journal Entries Section -->
            <section class="journal-entries-section details-section">
              <div class="section-header">
                 <h3>{{ character.journal ? character.journal.name : 'Journal' }}</h3>
                 <button v-if="character.journal" @click="openAddEntryModal" class="btn btn-primary btn-sm">Add Entry</button>
              </div>
              <p v-if="entriesLoading" class="loading-message small">Loading entries...</p>
              <p v-else-if="entriesError" class="error-message small">{{ entriesError }}</p>
              <p v-else-if="entries.length === 0">No entries in this journal yet.</p>
              <ul v-else class="item-list entry-list">
                 <li v-for="entry in entries" :key="entry.id" class="item-list-item">
                    <div class="item-info">
                       <h4>{{ entry.title || 'Untitled Entry' }}</h4>
                       <p class="entry-content">{{ entry.content }}</p>
                       <small class="entry-meta">Created: {{ formatDate(entry.created_at) }} | Updated: {{ formatDate(entry.updated_at) }}</small>
                    </div>
                    <div class="item-actions">
                       <button @click="openEditEntryModal(entry)" class="btn btn-secondary btn-sm">Edit</button>
                       <button @click="confirmDeleteEntry(entry)" class="btn btn-danger btn-sm">Delete</button>
                    </div>
                 </li>
              </ul>
            </section>
            <!-- Placeholder for other sections -->
            <section class="details-section">
                <h3>Items</h3>
                <p>Item management coming soon.</p>
            </section>
            <section class="details-section">
                <h3>Relationships</h3>
                <p>Character relationship tracking coming soon.</p>
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

    <!-- Add/Edit Journal Entry Modal -->
    <div v-if="showEntryModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
        <h2>{{ editingEntry ? 'Edit Journal Entry' : 'Add New Journal Entry' }}</h2>
          <button @click="closeEntryModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
        <form @submit.prevent="handleSaveEntry">
          <div class="form-group">
            <label for="entryTitle">Title (Optional):</label>
              <input type="text" id="entryTitle" v-model="entryForm.title" class="form-control">
          </div>
          <div class="form-group">
            <label for="entryContent">Content:</label>
              <textarea id="entryContent" v-model="entryForm.content" required class="form-control"></textarea>
          </div>
            <div class="form-actions">
            <button type="button" @click="closeEntryModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!entryForm.content.trim()">
              {{ editingEntry ? 'Save Changes' : 'Create Entry' }}
            </button>
          </div>
           <p v-if="entryError" class="error-message">{{ entryError }}</p>
        </form>
        </div>
      </div>
    </div>

     <!-- Delete Journal Entry Confirmation Modal -->
    <div v-if="entryToDelete" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h2>Confirm Delete Entry</h2>
          <button @click="entryToDelete = null" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
        <p>Are you sure you want to delete this journal entry?</p>
        <p v-if="entryToDelete.title"><strong>Title:</strong> {{ entryToDelete.title }}</p>
           <div class="form-actions">
            <button type="button" @click="entryToDelete = null" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="handleDeleteEntry" class="btn btn-danger">Delete</button>
          </div>
           <p v-if="deleteEntryError" class="error-message">{{ deleteEntryError }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, reactive, computed } from 'vue';
import * as charactersApi from '@/services/api/characters';
import * as journalEntriesApi from '@/services/api/journalEntries';
import * as characterTagTypeApi from '@/services/api/characterTagTypeService'; // Import Character Tag Type API
import * as characterTagApi from '@/services/api/characterTagService'; // Import Character Tag API
import type { Character, CharacterUpdate } from '@/types/character';
import type { JournalEntry, JournalEntryCreate, JournalEntryUpdate } from '@/types/journal_entry';
import type { CharacterTagType } from '@/types/characterTagType'; // Import Character Tag Type
import CreateCharacterForm from '@/components/dashboard/CreateCharacterForm.vue'; // Updated path
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'; // Import editor
import MarkdownIt from 'markdown-it'; // Import renderer

interface JournalEntryFormData {
    title: string | null;
    content: string;
}

export default defineComponent({
  name: 'CharacterDetailView',
  components: { CreateCharacterForm, MarkdownEditor },
  props: {
    characterId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const character = ref<Character | null>(null);
    const entries = ref<JournalEntry[]>([]);
    const loading = ref(true);
    const entriesLoading = ref(false);
    const error = ref<string | null>(null);
    const entriesError = ref<string | null>(null);
    const entryError = ref<string | null>(null);
    const deleteEntryError = ref<string | null>(null);

    const showEntryModal = ref(false);
    const editingEntry = ref<JournalEntry | null>(null);
    const entryToDelete = ref<JournalEntry | null>(null);

    // Character edit modal
    const showEditCharacterModal = ref(false);

    // State for character tag editing
    const showTagEditDialog = ref(false);
    const availableTagTypes = ref<CharacterTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]); 
    const isSavingTags = ref(false);
    const tagSyncError = ref<string | null>(null);

    // State for tag type management
    const showTagTypeDialog = ref(false);
    const editingTagType = ref<CharacterTagType | null>(null);
    const tagTypeName = ref('');
    const isSavingTagType = ref(false);
    const tagTypeDialogError = ref<string | null>(null);

    // State for delete tag type confirmation
    const showDeleteTagTypeConfirm = ref(false);
    const tagTypeToDelete = ref<CharacterTagType | null>(null);
    const isDeletingTagType = ref(false);
    const deleteTagTypeError = ref<string | null>(null);

    // --- Inline Description Editing State ---
    const isEditingDescription = ref(false);
    const editableDescription = ref('');
    const isSavingDescription = ref(false);
    const saveDescriptionError = ref<string | null>(null);

    // --- Computed Properties ---
    // Initialize markdown-it
    const md = new MarkdownIt({
      html: false, 
      linkify: true,
      typographer: true,
    });

    // Computed property for rendering description
    const renderedDescription = computed(() => {
      if (character.value?.description) {
        return md.render(character.value.description);
      }
      return '<p><em>No description provided.</em></p>';
    });

    // Computed to check if description changed
    const isDescriptionChanged = computed(() => {
      const currentDesc = character.value?.description ?? '';
      const editedDesc = editableDescription.value.trim() === '' ? '' : editableDescription.value;
      return currentDesc !== editedDesc;
    });

    const entryForm = reactive<JournalEntryFormData>({
        title: null,
        content: '',
    });
    
    const currentJournalId = computed(() => character.value?.journal?.id);
    const currentWorldId = computed(() => character.value?.world_id);
    const numericCharacterId = computed(() => Number(props.characterId));

    const fetchCharacter = async (id: number) => {
      loading.value = true;
      error.value = null;
      character.value = null;
      entries.value = [];
      entriesError.value = null;
      try {
        character.value = await charactersApi.getCharacterById(id);
        if (character.value) {
            if (currentJournalId.value) {
                await fetchEntries(currentJournalId.value);
            }
            if (currentWorldId.value) {
                await fetchTagTypes(currentWorldId.value); // Fetch tag types for the world
            }
        }
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

    const fetchEntries = async (journalId: number) => {
        entriesLoading.value = true;
        entriesError.value = null;
        try {
            entries.value = await journalEntriesApi.getEntriesByJournal(journalId);
        } catch (err: any) {
             console.error("Fetch Entries Error:", err);
             entriesError.value = `Failed to load journal entries: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        } finally {
            entriesLoading.value = false;
        }
    };

    const fetchTagTypes = async (worldId: number) => {
        if (!worldId) return;
        tagTypesLoading.value = true;
        tagTypesError.value = null;
        try {
            availableTagTypes.value = await characterTagTypeApi.getCharacterTagTypes(worldId);
        } catch (err: any) {
            console.error('Error fetching character tag types:', err);
            tagTypesError.value = err.message || 'Failed to load character tag types';
            availableTagTypes.value = []; 
        } finally {
            tagTypesLoading.value = false;
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

    // Journal Entry Modal Functions
    const resetEntryForm = () => {
        entryForm.title = null;
        entryForm.content = '';
        editingEntry.value = null;
        entryError.value = null;
    };
    
    const openAddEntryModal = () => {
        resetEntryForm();
        showEntryModal.value = true;
    };

    const openEditEntryModal = (entry: JournalEntry) => {
        editingEntry.value = entry;
        entryForm.title = entry.title;
        entryForm.content = entry.content;
        entryError.value = null;
        showEntryModal.value = true;
    };
    
    const closeEntryModal = () => {
        showEntryModal.value = false;
        resetEntryForm();
    };

    const handleSaveEntry = async () => {
        if (!currentJournalId.value) {
            entryError.value = "Cannot save entry: Journal ID is missing.";
            return;
        }
        entryError.value = null;

        try {
            if (editingEntry.value) {
                const entryUpdateData: JournalEntryUpdate = {};
                if (entryForm.title !== editingEntry.value.title) {
                    entryUpdateData.title = entryForm.title;
                }
                if (entryForm.content !== editingEntry.value.content) {
                    entryUpdateData.content = entryForm.content;
                }
                if (Object.keys(entryUpdateData).length > 0) {
                    const updatedEntry = await journalEntriesApi.updateJournalEntry(
                        editingEntry.value.id,
                        entryUpdateData
                    );
                    const index = entries.value.findIndex(e => e.id === updatedEntry.id);
                    if (index !== -1) {
                        entries.value[index] = updatedEntry;
                    }
                }
            } else {
                const entryCreateData: JournalEntryCreate = {
                    title: entryForm.title,
                    content: entryForm.content,
                    journal_id: currentJournalId.value
                };
                const newEntry = await journalEntriesApi.createJournalEntry(entryCreateData);
                entries.value.push(newEntry);
            }
            closeEntryModal();
        } catch (err: any) {
            console.error("Save Entry Error:", err);
            entryError.value = `Failed to save entry: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
    };

    const confirmDeleteEntry = (entry: JournalEntry) => {
        entryToDelete.value = entry;
        deleteEntryError.value = null;
    };

    const handleDeleteEntry = async () => {
        if (!entryToDelete.value) return;
        deleteEntryError.value = null;
        try {
            await journalEntriesApi.deleteJournalEntry(entryToDelete.value.id);
            entries.value = entries.value.filter(e => e.id !== entryToDelete.value!.id);
            entryToDelete.value = null; // Close confirmation modal
        } catch (err: any) {
             console.error("Delete Entry Error:", err);
             deleteEntryError.value = `Failed to delete entry: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
    };

    // Edit Character Modal Functions
    const openEditCharacterModal = () => {
      showEditCharacterModal.value = true;
    };

    const closeEditCharacterModal = () => {
      showEditCharacterModal.value = false;
    };

    const handleCharacterSaved = () => {
      closeEditCharacterModal();
      fetchCharacter(numericCharacterId.value); // Refresh character details
    };

    // Tag Assignment Modal Functions
     const openTagEditDialog = () => {
       if (!character.value || currentWorldId.value === undefined) return;
       selectedTagTypeIds.value = character.value.tags?.map(t => t.character_tag_type_id) || [];
       if (availableTagTypes.value.length === 0 || tagTypesError.value) {
         fetchTagTypes(currentWorldId.value);
       }
       tagSyncError.value = null;
       showTagEditDialog.value = true;
     };
 
     const closeTagEditDialog = () => {
       showTagEditDialog.value = false;
     };
 
     const saveTags = async () => {
       if (!character.value) return;
       isSavingTags.value = true;
       tagSyncError.value = null;
 
       const originalTagTypeIds = character.value.tags?.map(t => t.character_tag_type_id) || [];
       const currentTagTypeIds = new Set(selectedTagTypeIds.value);
       const originalTagTypeIdsSet = new Set(originalTagTypeIds);
 
       const tagsToAdd = selectedTagTypeIds.value.filter(id => !originalTagTypeIdsSet.has(id));
       const tagsToRemove = originalTagTypeIds.filter(id => !currentTagTypeIds.has(id));
 
       const addPromises = tagsToAdd.map(tagTypeId => 
         characterTagApi.addTagToCharacter(numericCharacterId.value, tagTypeId)
       );
       const removePromises = tagsToRemove.map(tagTypeId => 
         characterTagApi.removeTagFromCharacter(numericCharacterId.value, tagTypeId)
       );
 
       try {
         await Promise.all([...addPromises, ...removePromises]);
         closeTagEditDialog();
         fetchCharacter(numericCharacterId.value); // Refresh character to show updated tags
       } catch (err: any) {
         console.error("Error syncing character tags:", err);
         tagSyncError.value = `Failed to sync tags: ${err.message || 'Unknown error'}`;
       } finally {
         isSavingTags.value = false;
       }
     };

     // Tag Type Management Modal Functions
    const openAddTagTypeDialog = () => {
      editingTagType.value = null;
      tagTypeName.value = '';
      tagTypeDialogError.value = null;
      showTagTypeDialog.value = true;
    };

    const openEditTagTypeDialog = (tagType: CharacterTagType) => {
      editingTagType.value = { ...tagType };
      tagTypeName.value = tagType.name;
      tagTypeDialogError.value = null;
      showTagTypeDialog.value = true;
    };

    const closeTagTypeDialog = () => {
      showTagTypeDialog.value = false;
      editingTagType.value = null;
      tagTypeName.value = '';
      tagTypeDialogError.value = null;
    };

    const saveTagType = async () => {
      if (!tagTypeName.value || !currentWorldId.value) return;
      isSavingTagType.value = true;
      tagTypeDialogError.value = null;

      try {
        if (editingTagType.value) {
          // Update
          const updateData = { name: tagTypeName.value };
          const updated = await characterTagTypeApi.updateCharacterTagType(currentWorldId.value, editingTagType.value.id, updateData);
          const index = availableTagTypes.value.findIndex(t => t.id === updated.id);
          if (index !== -1) availableTagTypes.value[index] = updated;
        } else {
          // Create
          const createData = { name: tagTypeName.value };
          const created = await characterTagTypeApi.createCharacterTagType(currentWorldId.value, createData);
          availableTagTypes.value.push(created);
        }
        closeTagTypeDialog();
        // Refresh tag types in case they are needed elsewhere or for the edit dialog
        if (currentWorldId.value) fetchTagTypes(currentWorldId.value);
      } catch (err: any) {
        console.error('Error saving character tag type:', err);
        tagTypeDialogError.value = err.response?.data?.detail || err.message || 'Failed to save tag type';
      } finally {
        isSavingTagType.value = false;
      }
    };

    // Delete Tag Type Confirmation Modal Functions
    const confirmDeleteTagType = (tagType: CharacterTagType) => {
      tagTypeToDelete.value = tagType;
      deleteTagTypeError.value = null;
      showDeleteTagTypeConfirm.value = true;
    };

    const cancelDeleteTagType = () => {
      showDeleteTagTypeConfirm.value = false;
      tagTypeToDelete.value = null;
      deleteTagTypeError.value = null;
    };

    const executeDeleteTagType = async () => {
      if (!tagTypeToDelete.value || !currentWorldId.value) return;
      isDeletingTagType.value = true;
      deleteTagTypeError.value = null;
      try {
        await characterTagTypeApi.deleteCharacterTagType(currentWorldId.value, tagTypeToDelete.value.id);
        availableTagTypes.value = availableTagTypes.value.filter(t => t.id !== tagTypeToDelete.value?.id);
        cancelDeleteTagType(); // Close modal on success
        // Refresh character details in case a deleted tag type was assigned
        fetchCharacter(numericCharacterId.value);
      } catch (err: any) {
        console.error('Error deleting character tag type:', err);
        deleteTagTypeError.value = err.response?.data?.detail || err.message || 'Failed to delete tag type';
      } finally {
        isDeletingTagType.value = false;
      }
    };

    // --- Functions for Inline Description Editing ---
    const startEditingDescription = () => {
      if (!character.value) return;
      editableDescription.value = character.value.description ?? '';
      saveDescriptionError.value = null;
      isEditingDescription.value = true;
    };

    const cancelDescriptionEdit = () => {
      isEditingDescription.value = false;
      saveDescriptionError.value = null;
    };

    const saveDescription = async () => {
      if (!character.value || !isDescriptionChanged.value) return;

      isSavingDescription.value = true;
      saveDescriptionError.value = null;
      const newDescription = editableDescription.value.trim() === '' ? null : editableDescription.value;
      
      try {
        const updatePayload: CharacterUpdate = { 
          description: newDescription
          // Ensure other required fields for update are NOT included if not changed
        };
        const updatedCharacter = await charactersApi.updateCharacter(Number(props.characterId), updatePayload);
        
        // Update local state
        character.value = { ...character.value, ...updatedCharacter }; // Merge in case API returns partial data
        isEditingDescription.value = false;
        
      } catch (err: any) {
        console.error("Error saving description:", err);
        saveDescriptionError.value = err.response?.data?.detail || err.message || 'Failed to save description.';
      } finally {
        isSavingDescription.value = false;
      }
    };

    // Watcher for characterId prop changes
    watch(
      () => props.characterId,
      (newId) => {
      if (newId) {
        fetchCharacter(Number(newId));
        } else {
          character.value = null;
          error.value = "Character ID is missing.";
          loading.value = false;
      }
      },
      { immediate: true }
    );

    return {
      character,
      entries,
      loading,
      entriesLoading,
      error,
      entriesError,
      formatDate,
      // Journal Entry Modals
      showEntryModal,
      editingEntry,
      entryForm,
      entryError,
      openAddEntryModal,
      openEditEntryModal,
      closeEntryModal,
      handleSaveEntry,
      entryToDelete,
      deleteEntryError,
      confirmDeleteEntry,
      handleDeleteEntry,
      // Edit Character Modal
      showEditCharacterModal,
      openEditCharacterModal,
      closeEditCharacterModal,
      handleCharacterSaved,
      // Tag Assignment Modal
      showTagEditDialog,
      availableTagTypes,
      tagTypesLoading,
      tagTypesError,
      selectedTagTypeIds,
      isSavingTags,
      tagSyncError,
      openTagEditDialog,
      closeTagEditDialog,
      saveTags,
      // Tag Type Management Modals
      showTagTypeDialog,
      editingTagType,
      tagTypeName,
      isSavingTagType,
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
      // --- Inline Description Editing Exports ---
      isEditingDescription,
      editableDescription,
      isSavingDescription,
      saveDescriptionError,
      startEditingDescription,
      cancelDescriptionEdit,
      saveDescription,
      isDescriptionChanged,
      renderedDescription,
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
</style> 