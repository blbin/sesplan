<template>
  <v-container fluid>
    <!-- Loading and Error States -->
    <div v-if="loadingJournal">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <span class="ml-2">Loading journal details...</span>
    </div>
    <v-alert type="error" v-else-if="errorJournal" class="mb-4">{{ errorJournal }}</v-alert>

    <!-- Journal Content -->
    <div v-else-if="journal">
      <header class="view-header mb-4">
        <div>
          <h1>{{ journal.name }}</h1>
          <p class="text-caption">Character ID: {{ journal.character_id }}</p>
        </div>
        <v-btn color="primary" @click="openAddEntryModal" :disabled="loadingEntries">
          <v-icon left>mdi-plus</v-icon>
          Add Entry
        </v-btn>
      </header>
      <p v-if="journal.description" class="mb-4">{{ journal.description }}</p>
      <v-divider class="mb-4"></v-divider>

      <h2>Entries</h2>

      <!-- Entries Loading and Error States -->
      <div v-if="loadingEntries" class="text-center my-4">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
        <p>Loading entries...</p>
      </div>
      <v-alert type="error" v-else-if="errorEntries" class="mb-4">{{ errorEntries }}</v-alert>

      <!-- Entries List using v-list -->
      <v-list v-else-if="entries.length > 0" lines="two" density="compact" class="entries-list">
        <div v-for="entry in entries" :key="entry.id" class="entry-item-wrapper">
          <v-list-item
            :title="entry.title || 'Untitled Entry'"
            :subtitle="formatEntryDates(entry)"
          >
            <template v-slot:append>
              <v-btn 
                :icon="expandedEntryId === entry.id ? 'mdi-chevron-up' : 'mdi-chevron-down'" 
                variant="text" 
                @click="toggleEntryExpansion(entry.id)" 
                size="small"
                title="Show/Hide Content"
                class="mr-1"
              ></v-btn>
              <v-btn icon="mdi-pencil" variant="text" @click="openEditEntryModal(entry)" size="small" class="mr-1" title="Edit"></v-btn>
              <v-btn icon="mdi-delete" variant="text" @click="confirmDeleteEntry(entry)" size="small" color="error" title="Delete"></v-btn>
            </template>
          </v-list-item>

          <!-- Content Preview (always visible unless expanded) -->
          <v-list-item-subtitle v-if="expandedEntryId !== entry.id && entry.content" class="entry-preview ml-4 mb-2" v-html="renderMarkdownInline(entry.content, 150)">
          </v-list-item-subtitle>
          <v-list-item-subtitle v-if="expandedEntryId !== entry.id && !entry.content" class="entry-preview ml-4 mb-2 text-muted">
             <em>No content preview available.</em>
          </v-list-item-subtitle>
          
          <!-- Expanded Content -->
          <v-expand-transition>
            <div v-show="expandedEntryId === entry.id">
              <v-divider class="mx-4"></v-divider>
              <div class="entry-full-content pa-4" v-html="renderMarkdownBlock(entry.content)">
              </div>
            </div>
          </v-expand-transition>
          <v-divider v-if="entries.length > 1"></v-divider> <!-- Divider between entries -->
        </div>
      </v-list>
      <p v-else class="text-center text-muted my-4">No journal entries yet.</p>

    </div>

    <!-- Fallback if journal not found -->
    <div v-else class="text-center my-4">
      <p>Journal not found.</p>
    </div>

    <!-- Add/Edit Entry Dialog -->
    <v-dialog v-model="showEntryModal" max-width="800px" persistent>
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
        <!-- Actions are inside the form -->
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDeleteModal
      :show="!!entryToDelete"
      itemType="journal entry"
      :itemName="entryToDelete?.title || `Entry #${entryToDelete?.id}`"
      :isDeleting="isDeletingEntry"
      :error="deleteError"
      @confirm="handleDeleteEntry"
      @cancel="entryToDelete = null"
    />

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { getJournalById } from '@/services/api/journals';
import { getEntriesByJournal, deleteJournalEntry } from '@/services/api/journalEntries';
import type { Journal } from '@/types/journal';
import type { JournalEntry } from '@/types/journal_entry';
import { formatDateTime as formatDateUtil } from '@/utils/dateFormatter';
import JournalEntryForm from '@/components/dashboard/JournalEntryForm.vue';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
// Import Vuetify components used in template
import { 
  VContainer, VProgressCircular, VAlert, VBtn, VIcon, VDivider, 
  VDialog, VCard, VCardTitle, VCardText, // Keeping VCard for the dialog
  VList, VListItem, // Added back VList, VListItem
  VExpandTransition 
} from 'vuetify/components';
import MarkdownIt from 'markdown-it'; // Import markdown-it

// --- Markdown Rendering --- 
const md = new MarkdownIt({ html: false, linkify: true, typographer: true });

const renderMarkdownInline = (markdown: string | null | undefined, maxLength: number): string => {
  if (!markdown) { return ''; }
  // Basic truncation, might break markdown mid-tag, but ok for preview
  let truncatedMd = markdown.length > maxLength ? markdown.substring(0, maxLength) + '...' : markdown;
  return md.renderInline(truncatedMd);
};

const renderMarkdownBlock = (markdown: string | null | undefined): string => {
  if (!markdown) { return ''; }
  return md.render(markdown);
};

// --- Component State --- 
const route = useRoute();
const journal = ref<Journal | null>(null);
const entries = ref<JournalEntry[]>([]);

// Loading states
const loadingJournal = ref(false);
const loadingEntries = ref(false);
const isSavingEntry = ref(false); // For form submission
const isDeletingEntry = ref(false); // For delete confirmation

// Error states
const errorJournal = ref<string | null>(null);
const errorEntries = ref<string | null>(null);
const formError = ref<string | null>(null); // Error within the form
const deleteError = ref<string | null>(null); // Error during deletion

// Modal/Dialog states
const showEntryModal = ref(false);
const editingEntry = ref<JournalEntry | null>(null);
const entryToDelete = ref<JournalEntry | null>(null);

// State for expanded entry
const expandedEntryId = ref<number | null>(null);

const journalId = computed(() => Number(route.params.journalId));

// --- Data Loading --- 

const loadJournalDetails = async () => {
  if (!journalId.value || isNaN(journalId.value)) {
    errorJournal.value = "Invalid Journal ID.";
    return;
  }
  loadingJournal.value = true;
  errorJournal.value = null;
  try {
    journal.value = await getJournalById(journalId.value);
  } catch (err: any) {
    console.error("Failed to load journal details:", err);
    errorJournal.value = `Failed to load journal: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    journal.value = null; // Ensure journal is null on error
  } finally {
    loadingJournal.value = false;
  }
};

const loadJournalEntries = async () => {
  if (!journalId.value || isNaN(journalId.value)) return; // Don't load if journal ID is invalid
  loadingEntries.value = true;
  errorEntries.value = null;
  try {
    entries.value = await getEntriesByJournal(journalId.value);
  } catch (err: any) {
    console.error("Failed to load journal entries:", err);
    errorEntries.value = `Failed to load entries: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    entries.value = []; // Clear entries on error
  } finally {
    loadingEntries.value = false;
  }
};

// --- Modal/Dialog Actions --- 

const openAddEntryModal = () => {
  editingEntry.value = null; // Ensure we are in "add" mode
  formError.value = null;
  showEntryModal.value = true;
};

const openEditEntryModal = (entry: JournalEntry) => {
  editingEntry.value = { ...entry }; // Create a copy to edit
  formError.value = null;
  showEntryModal.value = true;
};

const closeEntryModal = () => {
  showEntryModal.value = false;
  editingEntry.value = null;
  formError.value = null;
  // isSavingEntry should be reset by the form component or the save handler
};

const handleEntrySaved = () => {
  // Potentially update or add the entry in the local list
  // For simplicity, just reload all entries for now
  closeEntryModal();
  loadJournalEntries(); 
};

// --- Delete Actions --- 

const confirmDeleteEntry = (entry: JournalEntry) => {
  entryToDelete.value = entry;
  deleteError.value = null; // Clear previous delete errors
};

const handleDeleteEntry = async () => {
  if (!entryToDelete.value) return;

  isDeletingEntry.value = true;
  deleteError.value = null;

  try {
    await deleteJournalEntry(entryToDelete.value.id);
    entryToDelete.value = null; // Close modal on success
    // Refresh the list after deletion
    await loadJournalEntries(); 
  } catch (err: any) {
    console.error("Failed to delete journal entry:", err);
    deleteError.value = `Delete failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    // Keep the modal open to show the error
  } finally {
    isDeletingEntry.value = false;
  }
};

// --- Expansion Toggle --- 
const toggleEntryExpansion = (entryId: number) => {
  expandedEntryId.value = expandedEntryId.value === entryId ? null : entryId;
};

// --- Helper to format entry dates --- 
const formatEntryDates = (entry: JournalEntry): string => {
  let createdDateStr = formatDateUtil(entry.created_at);
  let dates = `Created: ${createdDateStr}`;
  
  if (entry.updated_at && entry.updated_at !== entry.created_at) {
    try {
      const updatedAt = new Date(entry.updated_at);
      const updatedDateTimeStr = updatedAt.toLocaleString(); 
      dates += ` | Updated: ${updatedDateTimeStr}`;
    } catch (e) {
      console.error("Error formatting updated_at date:", e);
      dates += ` | Updated: ${entry.updated_at}`;
    }
  }
  return dates;
};

// --- Initial Load --- 
onMounted(async () => {
  await loadJournalDetails();
  // Only load entries if journal details loaded successfully
  if (journal.value) { 
    await loadJournalEntries();
  }
});

</script>

<style scoped>
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.my-4 {
  margin-top: 1rem;
  margin-bottom: 1rem;
}
.mb-4 {
  margin-bottom: 1rem;
}
.text-center {
  text-align: center;
}
.text-muted {
  color: #6c757d;
}
.mr-1 {
    margin-right: 0.25rem;
}
.entries-list {
  border: 1px solid rgba(0,0,0,0.12); /* Optional: add border to list */
  border-radius: 4px;
  background-color: white;
}

.entry-item-wrapper:last-child .v-divider {
  display: none; /* Hide last divider */
}

.entry-preview {
  font-style: italic;
  color: #555;
  /* max-height: 5em; Remove max-height or adjust if needed */
  overflow: hidden;
  /* padding needed? added ml-4 mb-2 */
}

.entry-full-content {
  background-color: #f9f9f9; /* Slightly different background for expanded content */
}

.entry-full-content :deep(p:last-child) {
  margin-bottom: 0;
}

/* Remove card-specific styles */
/*
.entry-card {
  transition: box-shadow 0.2s ease-in-out;
}
.entry-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.ml-1 {
    margin-left: 0.25rem;
}
*/
</style> 