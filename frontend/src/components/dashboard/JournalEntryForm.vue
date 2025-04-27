<template>
  <form @submit.prevent="saveEntry" class="journal-entry-form">
    <div class="form-group">
      <label for="entryTitle">Title (Optional)</label>
      <v-text-field 
        v-model="formData.title"
        variant="outlined"
        density="compact"
        id="entryTitle"
        placeholder="e.g., Session 5 Recap, Clue Found"
      />
    </div>
    <div class="form-group">
      <label for="entryContent">Content *</label>
      <MarkdownEditor 
        v-model="formData.content"
        id="entryContent"
        label="Journal Entry Content"
        :rules="[rules.requiredContent]" 
      /> 
    </div>

    <v-alert v-if="localError" type="error" variant="tonal" density="compact" class="mb-4">
      {{ localError }}
    </v-alert>

    <div class="form-actions">
      <v-btn variant="text" @click="onCancel" :disabled="isSaving">Cancel</v-btn>
      <v-btn 
        color="primary" 
        type="submit" 
        :loading="isSaving"
        :disabled="!formData.content.trim()" 
       >
        {{ isSaving ? 'Saving...' : (isEditing ? 'Save Changes' : 'Add Entry') }}
      </v-btn>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, defineProps, defineEmits } from 'vue';
import type { PropType } from 'vue';
import * as journalEntriesApi from '@/services/api/journalEntries';
import type { JournalEntry, JournalEntryCreate, JournalEntryUpdate } from '@/types/journal_entry';
import { VTextField, VBtn, VAlert } from 'vuetify/components';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';

interface EntryFormData {
  title: string | null;
  content: string;
}

// Define props
const props = defineProps({
  journalId: {
    type: Number,
    required: true,
  },
  entryToEdit: {
    type: Object as PropType<JournalEntry | null>,
    default: null,
  },
  isSaving: { // Prop to indicate saving state (controlled by parent)
    type: Boolean,
    default: false,
  },
  error: { // Prop for error message from parent
      type: String as PropType<string | null>,
      default: null,
  }
});

// Define emits
const emit = defineEmits(['saved', 'cancel']);

const localError = ref<string | null>(null); // Internal form validation errors

// Basic required rule for content
const rules = {
    requiredContent: (value: string) => !!value || 'Content cannot be empty.',
};

const formData = reactive<EntryFormData>({
  title: null,
  content: '',
});

const isEditing = computed(() => !!props.entryToEdit);

// Watch for external error prop
watch(() => props.error, (newError) => {
    localError.value = newError;
});

// Initialize form data when entryToEdit changes
watch(
  () => props.entryToEdit,
  (entry) => {
    if (entry) {
      formData.title = entry.title;
      formData.content = entry.content || '';
    } else {
      // Reset for new entry
      formData.title = null;
      formData.content = '';
    }
    localError.value = null; // Clear errors when form data changes
  },
  { immediate: true }
);

const onCancel = () => {
  emit('cancel');
};

const saveEntry = async () => {
  localError.value = null;
  // Validate content
  const contentCheckResult = rules.requiredContent(formData.content);
  if (contentCheckResult !== true) { // Check if validation failed
    localError.value = contentCheckResult; // Assign the error message
    return;
  }

  // Indicate saving started (parent handles actual API call, but good practice)
  // We don't set isSaving prop here, parent controls it
  
  try {
    let savedEntry: JournalEntry;
    if (isEditing.value && props.entryToEdit) {
      const updateData: JournalEntryUpdate = {};
      if (formData.title !== props.entryToEdit.title) updateData.title = formData.title;
      if (formData.content !== (props.entryToEdit.content || '')) updateData.content = formData.content;
      
      if (Object.keys(updateData).length > 0) {
         savedEntry = await journalEntriesApi.updateJournalEntry(props.entryToEdit.id, updateData);
      } else {
          console.log("No changes detected for journal entry update.");
          emit('cancel'); // Close if no changes
          return;
      }
    } else {
      // Create new entry
      const createData: JournalEntryCreate = {
        journal_id: props.journalId,
        title: formData.title,
        content: formData.content,
      };
      savedEntry = await journalEntriesApi.createJournalEntry(createData);
    }
    emit('saved', savedEntry);
  } catch (err: any) {
    localError.value = `Save failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    console.error("Save Journal Entry Error:", err);
    // No need to emit error, parent will handle via prop if needed
  } finally {
    // Parent should set isSaving back to false
  }
};

</script>

<style scoped>
.journal-entry-form {
  padding: 1rem 0; /* Padding adjusted as it's inside v-card-text */
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group:last-of-type {
    margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
  color: #495057;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

/* Style MarkdownEditor specifically if needed */
:deep(.markdown-editor) { 
    /* Example: Add border */
    /* border: 1px solid #ccc; 
    border-radius: 4px; */
}
</style> 