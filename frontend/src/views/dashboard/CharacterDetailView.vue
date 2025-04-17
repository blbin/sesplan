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

       <!-- Updated Related Sections -->
       <div class="related-sections">
            <!-- Journal Entries Section -->
            <section class="journal-entries-section">
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
            <!-- Other Sections -->
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

    <!-- Add/Edit Journal Entry Modal -->
    <div v-if="showEntryModal" class="modal-backdrop">
      <div class="modal">
        <h2>{{ editingEntry ? 'Edit Journal Entry' : 'Add New Journal Entry' }}</h2>
        <form @submit.prevent="handleSaveEntry">
          <div class="form-group">
            <label for="entryTitle">Title (Optional):</label>
            <input type="text" id="entryTitle" v-model="entryForm.title">
          </div>
          <div class="form-group">
            <label for="entryContent">Content:</label>
            <textarea id="entryContent" v-model="entryForm.content" required></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeEntryModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!entryForm.content.trim()">
              {{ editingEntry ? 'Save Changes' : 'Create Entry' }}
            </button>
          </div>
           <p v-if="entryError" class="error-message">{{ entryError }}</p>
        </form>
      </div>
    </div>

     <!-- Delete Journal Entry Confirmation Modal -->
    <div v-if="entryToDelete" class="modal-backdrop">
      <div class="modal confirmation-modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete this journal entry?</p>
        <p v-if="entryToDelete.title"><strong>Title:</strong> {{ entryToDelete.title }}</p>
         <div class="modal-actions">
            <button type="button" @click="entryToDelete = null" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="handleDeleteEntry" class="btn btn-danger">Delete</button>
          </div>
           <p v-if="deleteEntryError" class="error-message">{{ deleteEntryError }}</p>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, reactive, computed } from 'vue';
import * as charactersApi from '@/services/api/characters';
import * as journalEntriesApi from '@/services/api/journalEntries';
import type { Character } from '@/types/character';
import type { JournalEntry, JournalEntryCreate, JournalEntryUpdate } from '@/types/journal_entry';

interface JournalEntryFormData {
    title: string | null;
    content: string;
}

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

    const entryForm = reactive<JournalEntryFormData>({
        title: null,
        content: '',
    });
    
    const currentJournalId = computed(() => character.value?.journal?.id);

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

    const formatDate = (dateString: string | null): string => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleString();
        } catch (e) {
            return dateString;
        }
    };

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
                    journal_id: currentJournalId.value,
                };
                const newEntry = await journalEntriesApi.createJournalEntry(entryCreateData);
                entries.value.unshift(newEntry);
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
            entryToDelete.value = null;
        } catch (err: any) {
             console.error("Delete Entry Error:", err);
             deleteEntryError.value = `Failed to delete entry: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
    };

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
      entries,
      loading,
      entriesLoading,
      error,
      entriesError,
      entryError,
      deleteEntryError,
      formatDate,
      showEntryModal,
      editingEntry,
      entryToDelete,
      entryForm,
      openAddEntryModal,
      openEditEntryModal,
      closeEntryModal,
      handleSaveEntry,
      confirmDeleteEntry,
      handleDeleteEntry,
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

.related-sections section {
  margin-bottom: 2.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.section-header h3 {
   margin: 0;
   padding: 0;
   border: none;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.entry-list {
    margin-top: 1rem;
}

.item-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}

.item-list-item:last-child {
  border-bottom: none;
}

.item-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.item-info .entry-content {
  margin: 0.5rem 0;
  color: #333;
  white-space: pre-wrap;
  font-size: 1rem;
  line-height: 1.6;
}
.item-info .entry-meta {
    font-size: 0.8rem;
    color: #6c757d;
}

.item-actions {
    margin-left: 1rem; 
    white-space: nowrap; 
    display: flex;
    flex-direction: column;
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
  padding: 2rem;
  border-radius: 0.5rem;
  min-width: 450px;
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
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  box-sizing: border-box;
}

.form-group textarea {
    min-height: 120px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.confirmation-modal p {
    margin-bottom: 1rem;
}
.confirmation-modal p strong {
    margin-right: 0.5em;
}

.loading-message.small,
.error-message.small {
    padding: 0.5rem;
    font-size: 0.9rem;
    text-align: left;
    margin-top: 0.5rem;
}

.btn { padding: 0.5rem 1rem; border-radius: 0.3rem; cursor: pointer; border: none; font-weight: 500; text-decoration: none; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }

.journal-entries-section {
  margin-top: 2.5rem;
}
</style> 