<template>
  <div class="journal-tab">
    <div class="journal-header">
      <h3>Character Journal</h3>
      <v-btn 
        color="primary"
        @click="openAddEntryModal"
        :disabled="!journalId"
        size="small"
      >
        <v-icon left>mdi-plus</v-icon>
        Add Entry
      </v-btn>
    </div>

    <div v-if="loadingJournal || loadingEntries" class="loading-section">
      <v-progress-circular indeterminate color="primary" size="small"></v-progress-circular>
      <span class="ml-2">Loading journal data...</span>
    </div>
    <v-alert v-else-if="journalError || entriesError" type="error" variant="tonal" density="compact">
      {{ journalError || entriesError }}
    </v-alert>
    <div v-else-if="!journalId" class="info-message">
      This character does not have a journal yet. (This shouldn't normally happen)
    </div>
    <div v-else-if="entries.length === 0" class="info-message">
      No journal entries yet.
    </div>

    <v-list v-else lines="two" density="compact" class="entry-list">
      <v-list-item 
        v-for="entry in entries" 
        :key="entry.id"
        :title="entry.title || `Entry on ${formatDate(entry.created_at)}`"
        class="entry-item"
      >
         <template v-slot:subtitle>
           <div v-html="renderMarkdownInline(entry.content, 150)"></div>
         </template>

        <template v-slot:append>
          <v-btn icon="mdi-pencil" variant="text" size="small" @click="openEditEntryModal(entry)" class="mr-1"></v-btn>
          <v-btn icon="mdi-delete" variant="text" size="small" @click="confirmDeleteEntry(entry)"></v-btn>
        </template>
      </v-list-item>
    </v-list>

    <!-- Modal for Add/Edit Entry -->
    <v-dialog v-model="showEntryModal" max-width="700px" persistent>
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editingEntry ? 'Edit Journal Entry' : 'Add New Journal Entry' }}</span>
        </v-card-title>
        <v-card-text>
          <JournalEntryForm
            v-if="journalId" 
            :journal-id="journalId"
            :entry-to-edit="editingEntry"
            :is-saving="isSavingEntry"
            :error="formError"
            @saved="handleEntrySaved"
            @cancel="closeEntryModal"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeEntryModal">Cancel</v-btn>
          <!-- Save button is inside the form -->
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Modal -->
    <ConfirmDeleteModal
        :show="!!entryToDelete"
        itemType="journal entry"
        :itemName="entryToDelete?.title || `Entry on ${formatDate(entryToDelete?.created_at)}`" 
        :isDeleting="isDeletingEntry"
        :error="deleteError"
        @confirm="handleDeleteEntry"
        @cancel="entryToDelete = null"
     />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import * as charactersApi from '@/services/api/characters';
import * as journalEntriesApi from '@/services/api/journalEntries';
import type { Character } from '@/types/character';
import type { JournalEntry } from '@/types/journal_entry';
import { formatDate } from '@/utils/dateFormatter';
import JournalEntryForm from './JournalEntryForm.vue';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
// Import Vuetify components used
import { VBtn, VIcon, VList, VListItem, VProgressCircular, VAlert, VDialog, VCard, VCardTitle, VCardText, VCardActions, VSpacer } from 'vuetify/components';
import MarkdownIt from 'markdown-it';

// Add local markdown renderer
const md = new MarkdownIt({ html: false, linkify: true, typographer: true });
const renderMarkdownInline = (markdown: string | null | undefined, maxLength: number): string => {
  if (!markdown) { return '' }
  let truncatedMd = markdown.length > maxLength ? markdown.substring(0, maxLength) + '...' : markdown;
  return md.renderInline(truncatedMd);
};

const props = defineProps({
  characterId: {
    type: Number,
    required: true,
  },
});

const character = ref<Character | null>(null);
const entries = ref<JournalEntry[]>([]);
const loadingJournal = ref(true);
const loadingEntries = ref(false);
const journalError = ref<string | null>(null);
const entriesError = ref<string | null>(null);
const formError = ref<string | null>(null);
const deleteError = ref<string | null>(null);
const isSavingEntry = ref(false);
const isDeletingEntry = ref(false);

const showEntryModal = ref(false);
const editingEntry = ref<JournalEntry | null>(null);
const entryToDelete = ref<JournalEntry | null>(null);

// Get the journal ID from the character data
const journalId = computed(() => character.value?.journal?.id);

// Fetch character details (including journal info)
const fetchCharacterJournal = async () => {
  if (!props.characterId) return;
  loadingJournal.value = true;
  journalError.value = null;
  character.value = null;
  try {
    // Assuming getCharacterById returns the nested journal object
    character.value = await charactersApi.getCharacterById(props.characterId);
  } catch (err: any) {
    journalError.value = `Failed to load character/journal data: ${err.response?.data?.detail || err.message}`;
    console.error("Fetch Character/Journal Error:", err);
  } finally {
    loadingJournal.value = false;
  }
};

// Fetch journal entries if journalId is available
const fetchJournalEntries = async () => {
  const jId = journalId.value;
  if (!jId) {
    entries.value = []; // No journal, no entries
    entriesError.value = null;
    return;
  }
  loadingEntries.value = true;
  entriesError.value = null;
  try {
    entries.value = await journalEntriesApi.getEntriesByJournal(jId);
  } catch (err: any) {
    entriesError.value = `Failed to load journal entries: ${err.response?.data?.detail || err.message}`;
    console.error("Fetch Journal Entries Error:", err);
  } finally {
    loadingEntries.value = false;
  }
};

// Modal Controls
const openAddEntryModal = () => {
  editingEntry.value = null;
  formError.value = null;
  showEntryModal.value = true;
};

const openEditEntryModal = (entry: JournalEntry) => {
  editingEntry.value = { ...entry }; // Clone entry to avoid modifying original directly
  formError.value = null;
  showEntryModal.value = true;
};

const closeEntryModal = () => {
  showEntryModal.value = false;
  editingEntry.value = null;
  formError.value = null;
};

// CRUD Handlers
const handleEntrySaved = () => {
  closeEntryModal();
  fetchJournalEntries(); // Refresh entries list
};

const confirmDeleteEntry = (entry: JournalEntry) => {
  entryToDelete.value = entry;
  deleteError.value = null;
};

const handleDeleteEntry = async () => {
  if (!entryToDelete.value) return;
  const idToDelete = entryToDelete.value.id;
  isDeletingEntry.value = true;
  deleteError.value = null;
  try {
    await journalEntriesApi.deleteJournalEntry(idToDelete);
    entryToDelete.value = null;
    fetchJournalEntries(); // Refresh entries list
  } catch (err: any) {
    deleteError.value = `Failed to delete entry: ${err.response?.data?.detail || err.message}`;
    console.error("Delete Entry Error:", err);
  } finally {
    isDeletingEntry.value = false;
  }
};

// Initial data fetch
onMounted(() => {
  fetchCharacterJournal();
});

// Fetch entries when character/journal data is loaded
watch(journalId, (newJournalId, oldJournalId) => {
  if (newJournalId && newJournalId !== oldJournalId) {
    fetchJournalEntries();
  }
});

</script>

<style scoped>
.journal-tab {
  padding: 1rem 0; /* Add some padding */
}

.journal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.journal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  color: #495057;
}

.loading-section,
.info-message {
  padding: 1rem;
  text-align: center;
  color: #6c757d;
}

.entry-list {
    background-color: transparent; /* Remove default list background */
}

.entry-item {
  border-bottom: 1px solid #f0f0f0;
}

.entry-item:last-child {
    border-bottom: none;
}

/* Limit subtitle height and add ellipsis if needed */
:deep(.v-list-item-subtitle div) { 
    /* Assuming renderMarkdownInline doesn't add extra block elements */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%; /* Ensure it doesn't overflow container */
    font-size: 0.875rem;
    color: #555;
}

</style> 