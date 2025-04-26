<template>
  <div class="details-tab-content">
    <!-- Loading State -->
    <div v-if="worldLoading">
      <p>Loading details...</p>
      <!-- Optional: Add a v-progress-circular or similar -->
    </div>

    <!-- Error State -->
    <div v-else-if="worldError" class="error-message">
      <p>Error loading world details: {{ worldError }}</p>
    </div>

    <!-- Content State -->
    <div v-else-if="world" class="details-section">
      <h2>World Details</h2>

      <!-- Description Editing Block -->
      <div v-if="!isEditingDescription" class="description-display">
        <div 
          v-if="world.description" 
          class="description-content mb-2" 
          v-html="renderedDescription"
        ></div>
        <div v-else class="text-muted description-content mb-2">
          <em>No description provided. Click the pencil to add one.</em>
        </div>
        <v-btn 
          v-if="isCurrentUserOwner"
          icon="mdi-pencil" 
          variant="text" 
          size="small" 
          @click="startEditingDescription"
          title="Edit description"
          class="edit-button"
        ></v-btn>
      </div>
      <div v-else class="description-edit">
        <MarkdownEditor
          v-model="editedDescription"
          class="mb-2"
          :label="'World Description'" 
        />
        <div class="edit-actions">
          <v-btn 
            color="primary" 
            @click="saveDescription" 
            :loading="isSavingDescription"
            size="small"
            :disabled="world && editedDescription === (world.description || '')"
          >
            Save
          </v-btn>
          <v-btn 
            variant="text" 
            @click="cancelEditingDescription" 
            :disabled="isSavingDescription"
            size="small"
          >
            Cancel
          </v-btn>
        </div>
      </div>
      <!-- End Description Editing Block -->

      <v-divider class="my-4"></v-divider>

      <!-- Additional Details -->
      <p><strong>Public:</strong> {{ world.is_public ? 'Yes' : 'No' }}</p>
      <p><strong>Created:</strong> {{ formatDate(world.created_at) }}</p>
      <p><strong>Last Updated:</strong> {{ formatDate(world.updated_at) }}</p>

    </div>

    <!-- Fallback if world is null after loading without error -->
    <div v-else>
        <p>World details could not be loaded.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { toRef } from 'vue';
import { useWorldDetail } from '@/composables/useWorldDetail';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';
import { VBtn, VDivider } from 'vuetify/components'; // Import necessary Vuetify components

// Props
const props = defineProps<{ 
  worldId: string | number | undefined;
}>();

// Use the composable
const {
  world,
  worldLoading,
  worldError,
  isCurrentUserOwner,
  isEditingDescription,
  editedDescription,
  isSavingDescription,
  renderedDescription,
  startEditingDescription,
  cancelEditingDescription,
  saveDescription,
  formatDate, // Get formatDate from the composable
} = useWorldDetail(toRef(props, 'worldId'));

</script>

<style scoped>
.details-tab-content {
  padding: 1rem 0; /* Add some vertical padding */
}

.details-section h2 {
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
  font-size: 1.2rem;
  color: #495057;
}

.details-section p {
  margin: 0.5rem 0;
  line-height: 1.6;
  color: #555;
}

.details-section p strong {
  margin-right: 0.5em;
  color: #333;
}

.description-display {
  position: relative; /* Needed for positioning the edit button */
  padding-bottom: 2.5rem; /* Space for the button */
}

.description-content {
  /* Style for rendered markdown */
  line-height: 1.7;
}

.description-content :deep(p:last-child) {
  margin-bottom: 0; 
}

.description-content :deep(a) {
  color: var(--v-primary-base, #1976D2); /* Use Vuetify primary color */
  text-decoration: none;
}
.description-content :deep(a:hover) {
  text-decoration: underline;
}

.edit-button {
  position: absolute;
  bottom: 0;
  right: 0;
  opacity: 0.7;
  transition: opacity 0.2s ease-in-out;
}

.description-display:hover .edit-button {
    opacity: 1;
}

.description-edit {
  margin-bottom: 1rem;
}

.edit-actions {
  display: flex;
  gap: 0.5rem; /* Add space between buttons */
  margin-top: 0.5rem;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 0.25rem;
  margin: 1rem 0;
}

.text-muted {
  color: #6c757d;
}
</style> 