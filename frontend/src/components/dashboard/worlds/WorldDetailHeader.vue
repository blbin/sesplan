<template>
  <header class="view-header">
    <div class="d-flex align-center flex-grow-1">
      <div v-if="!isEditingName" class="d-flex align-center">
        <!-- Display World Name (handle loading state) -->
        <h1 v-if="!worldLoading && world" class="text-h5">{{ world.name }}</h1>
        <h1 v-else-if="worldLoading" class="text-h5 text-disabled">Loading...</h1>
        <v-btn 
          v-if="!worldLoading && isCurrentUserOwner"
          icon="mdi-pencil" 
          variant="text" 
          size="x-small" 
          @click="startEditingName"
          title="Edit name"
          class="ml-2"
        ></v-btn>
      </div>
      <div v-else class="d-flex align-center flex-grow-1">
        <!-- Edit World Name -->
        <v-text-field
          v-model="editedName"
          label="World Name"
          variant="outlined"
          density="compact"
          hide-details
          class="mr-2 flex-grow-1"
          autofocus
          @keyup.enter="saveName"
          @keyup.esc="cancelEditingName"
        ></v-text-field>
        <v-btn 
          color="primary" 
          @click="saveName" 
          :loading="isSavingName"
          size="small"
          :disabled="!editedName || (world && editedName === world.name) || false" 
        >
          Save
        </v-btn>
        <v-btn 
          variant="text" 
          @click="cancelEditingName" 
          :disabled="isSavingName"
          size="small"
        >
          Cancel
        </v-btn>
      </div>
    </div>
    <!-- Back Button -->
    <router-link :to="{ name: 'Worlds' }" class="btn btn-secondary ml-4">Back to List</router-link>
  </header>
</template>

<script setup lang="ts">
import { toRef } from 'vue';
import { useWorldDetail } from '@/composables/useWorldDetail';
import { VBtn, VTextField } from 'vuetify/components'; // Explicit imports for Vuetify components
import { RouterLink } from 'vue-router';

// Props
const props = defineProps<{ 
  worldId: string | number | undefined;
}>();

// Use the composable
const {
  world,
  worldLoading,
  isCurrentUserOwner,
  isEditingName,
  editedName,
  isSavingName,
  startEditingName,
  cancelEditingName,
  saveName,
} = useWorldDetail(toRef(props, 'worldId'));

</script>

<style scoped>
/* Styles specific to the header, can be copied or adjusted from WorldDetailView */
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem; /* Adjusted margin */
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.view-header h1 {
  margin: 0;
  color: #343a40;
}

.text-disabled {
  color: #adb5bd;
}

.btn {
  /* Basic button styling - ensure it matches the project's style */
  display: inline-block;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  text-decoration: none;
  border: 1px solid transparent;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  color: #fff;
  background-color: #5a6268;
  border-color: #545b62;
}

/* Responsive adjustments if needed */
@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .view-header .btn {
    margin-top: 1rem;
    align-self: flex-start; /* Align button left */
  }
}
</style> 