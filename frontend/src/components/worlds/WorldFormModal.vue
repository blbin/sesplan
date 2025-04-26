<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('cancel')">
    <div class="modal">
      <h2>{{ isEditing ? 'Edit World' : 'Add New World' }}</h2>
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label for="worldName">Name:</label>
          <input type="text" id="worldName" v-model="form.name" required>
        </div>
        <div class="form-group">
          <label for="worldDescription">Description:</label>
          <MarkdownEditor id="worldDescription" :model-value="descriptionForEditor" @update:model-value="updateDescription" />
        </div>
        <div class="modal-actions">
          <button type="button" @click="$emit('cancel')" class="btn btn-secondary">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="isSaving || !form.name.trim()">
            {{ isSaving ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create World') }}
          </button>
        </div>
        <p v-if="error" class="error-message">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, defineProps, defineEmits, computed } from 'vue';
import type { World, WorldCreate, WorldUpdate } from '@/types/world';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';

interface WorldFormData {
  name: string;
  description: string | null;
}

const props = defineProps<{
  show: boolean;
  worldToEdit: World | null;
  isSaving: boolean; // To disable button during save
  error: string | null;
}>();

const emit = defineEmits<{
  (e: 'save', data: WorldCreate | WorldUpdate): void;
  (e: 'cancel'): void;
}>();

const isEditing = computed(() => !!props.worldToEdit);

const form = reactive<WorldFormData>({
  name: '',
  description: null,
});

// Computed property to handle null -> '' for editor
const descriptionForEditor = computed(() => form.description ?? '');

// Function to handle update from editor, converting '' -> null if needed
const updateDescription = (newValue: string) => {
  form.description = newValue.trim() === '' ? null : newValue;
};

// Watch for changes in the worldToEdit prop to populate the form
watch(() => props.worldToEdit, (newWorld) => {
  if (newWorld) {
    form.name = newWorld.name;
    form.description = newWorld.description;
  } else {
    // Reset form if no world is being edited (i.e., adding new)
    form.name = '';
    form.description = null;
  }
}, { immediate: true }); // immediate ensures the form is populated on initial load if editing

// Watch for the modal becoming hidden to reset the form (optional)
watch(() => props.show, (newVal) => {
    if (!newVal && !props.worldToEdit) { // Reset only if closing the 'add' modal
        form.name = '';
        form.description = null;
    }
});

const submitForm = () => {
  if (!form.name.trim()) {
    // Basic validation, although covered by :disabled
    return;
  }

  let saveData: WorldCreate | WorldUpdate;

  if (isEditing.value && props.worldToEdit) {
    // Prepare update payload (only send changed fields)
    const updatePayload: WorldUpdate = {};
    if (form.name !== props.worldToEdit.name) {
      updatePayload.name = form.name;
    }
    // Use the potentially null-converted value from form.description
    if (form.description !== props.worldToEdit.description) {
      updatePayload.description = form.description;
    }
    // Only emit if there are actual changes
    if (Object.keys(updatePayload).length > 0) {
        saveData = updatePayload;
        emit('save', saveData);
    } else {
        // No changes detected, just close the modal
        emit('cancel');
    }
  } else {
    // Prepare create payload
    // Use the potentially null-converted value from form.description
    saveData = { ...form };
    emit('save', saveData);
  }
};
</script>

<style scoped>
/* Styles for Modal and Form */
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
  padding: 2rem 2.5rem; /* Slightly larger padding */
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #343a40;
  font-size: 1.4rem;
}

.form-group {
  margin-bottom: 1.25rem; /* Increased spacing */
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 0.6rem 0.75rem; /* Adjusted padding */
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  box-sizing: border-box;
  font-size: 1rem;
}
.form-group input:focus,
.form-group textarea:focus {
    border-color: #80bdff;
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}


.form-group textarea {
  min-height: 100px; /* Slightly taller */
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem; /* Increased gap */
  margin-top: 2rem; /* More space before actions */
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.error-message {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 1rem;
  text-align: left; /* Align error message left */
  padding: 0.5rem 0; /* Padding for spacing */
}

/* Button styles (assuming these might not be global) */
.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  text-decoration: none;
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

</style> 