<template>
  <section class="character-tag-type-manager detail-section">
    <div class="section-header">
      <h3>Manage Character Tag Types</h3>
      <v-btn color="primary" @click="openAddDialog" size="small">
        Add Tag Type
      </v-btn>
    </div>

    <div v-if="tagTypesLoading" class="loading-state">Loading character tag types...</div>
    <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
    <v-list v-else-if="availableTagTypes.length > 0" lines="one" density="compact">
      <v-list-item
        v-for="tagType in availableTagTypes"
        :key="tagType.id"
        :title="tagType.name"
      >
        <template v-slot:append>
          <v-btn icon="mdi-pencil" variant="text" size="small" @click="openEditDialog(tagType)" class="mr-2"></v-btn>
          <v-btn icon="mdi-delete" variant="text" size="small" @click="confirmDelete(tagType)"></v-btn>
        </template>
      </v-list-item>
    </v-list>
    <div v-else class="empty-state">No character tag types defined for this world yet.</div>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showDialog" persistent max-width="500px">
      <v-card :loading="isSaving">
        <v-card-title>
          <span class="headline">{{ editingTagType ? 'Edit Character Tag Type' : 'Add Character Tag Type' }}</span>
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="tagTypeName"
            label="Tag Type Name *"
            required
            :error-messages="dialogError ? [dialogError] : []"
            variant="outlined"
            density="compact"
            autofocus
            @keyup.enter="saveTagType"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDialog">Cancel</v-btn>
          <v-btn color="blue darken-1" :disabled="!tagTypeName || isSaving" @click="saveTagType">
            {{ isSaving ? 'Saving...' : 'Save' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDeleteModal
      :show="showDeleteConfirm"
      itemType="character tag type"
      :itemName="tagTypeToDelete?.name"
      :isDeleting="isDeleting"
      :error="deleteError"
      @confirm="executeDelete"
      @cancel="cancelDelete"
    />

  </section>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import type { CharacterTagType, CharacterTagTypeCreate, CharacterTagTypeUpdate } from '@/types/characterTagType';
import * as characterTagTypeApi from '@/services/api/characterTagTypeService';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
// Assume Vuetify components are globally available or imported elsewhere

export default defineComponent({
  name: 'CharacterTagTypeManager',
  components: { ConfirmDeleteModal },
  props: {
    worldId: {
      type: Number,
      required: true,
    },
    // Můžeme přijímat tagy jako prop, nebo je načítat zde
    // Pro jednoduchost je načteme zde
  },
  emits: ['tagsUpdated'], // Deklarace emitovaných událostí
  setup(props, { emit }) { // Získáme emit z kontextu
    const availableTagTypes = ref<CharacterTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);

    const showDialog = ref(false);
    const editingTagType = ref<CharacterTagType | null>(null);
    const tagTypeName = ref('');
    const isSaving = ref(false);
    const dialogError = ref<string | null>(null);

    const showDeleteConfirm = ref(false);
    const tagTypeToDelete = ref<CharacterTagType | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    // Fetch available tag types for the world
    const fetchTagTypes = async () => {
      tagTypesLoading.value = true;
      tagTypesError.value = null;
      availableTagTypes.value = [];
      try {
        availableTagTypes.value = await characterTagTypeApi.getCharacterTagTypes(props.worldId);
      } catch (err: any) {
        console.error('Error fetching character tag types:', err);
        tagTypesError.value = err.message || 'Failed to load character tags';
      } finally {
        tagTypesLoading.value = false;
      }
    };

    onMounted(fetchTagTypes);

    const openAddDialog = () => {
      editingTagType.value = null;
      tagTypeName.value = '';
      dialogError.value = null;
      showDialog.value = true;
    };

    const openEditDialog = (tagType: CharacterTagType) => {
      editingTagType.value = { ...tagType };
      tagTypeName.value = tagType.name;
      dialogError.value = null;
      showDialog.value = true;
    };

    const closeDialog = () => {
      showDialog.value = false;
      editingTagType.value = null;
      tagTypeName.value = '';
      dialogError.value = null;
    };

    const saveTagType = async () => {
      if (!tagTypeName.value) return;
      isSaving.value = true;
      dialogError.value = null;

      try {
        if (editingTagType.value) {
          // Update
          const updateData: CharacterTagTypeUpdate = { name: tagTypeName.value };
          const updated = await characterTagTypeApi.updateCharacterTagType(props.worldId, editingTagType.value.id, updateData);
          // Update in local list
          const index = availableTagTypes.value.findIndex(t => t.id === updated.id);
          if (index !== -1) availableTagTypes.value[index] = updated;
        } else {
          // Create
          const createData: CharacterTagTypeCreate = { name: tagTypeName.value };
          const created = await characterTagTypeApi.createCharacterTagType(props.worldId, createData);
          availableTagTypes.value.push(created);
        }
        // Emitujeme událost o změně tagů
        emit('tagsUpdated');
        closeDialog();
      } catch (err: any) {
        console.error('Error saving character tag type:', err);
        dialogError.value = err.response?.data?.detail || err.message || 'Failed to save character tag type';
      } finally {
        isSaving.value = false;
      }
    };

    const confirmDelete = (tagType: CharacterTagType) => {
      tagTypeToDelete.value = tagType;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      tagTypeToDelete.value = null;
      deleteError.value = null;
    };

    const executeDelete = async () => {
      if (!tagTypeToDelete.value) return;
      isDeleting.value = true;
      deleteError.value = null;
      try {
        await characterTagTypeApi.deleteCharacterTagType(props.worldId, tagTypeToDelete.value.id);
        availableTagTypes.value = availableTagTypes.value.filter(t => t.id !== tagTypeToDelete.value?.id);
        // Emitujeme událost o změně tagů
        emit('tagsUpdated');
        cancelDelete(); // Close modal on success
      } catch (err: any) {
         console.error('Error deleting character tag type:', err);
         deleteError.value = err.response?.data?.detail || err.message || 'Failed to delete character tag type';
      } finally {
        isDeleting.value = false;
      }
    };

    return {
      availableTagTypes,
      tagTypesLoading,
      tagTypesError,
      showDialog,
      editingTagType,
      tagTypeName,
      isSaving,
      dialogError,
      showDeleteConfirm,
      tagTypeToDelete,
      isDeleting,
      deleteError,
      openAddDialog,
      openEditDialog,
      closeDialog,
      saveTagType,
      confirmDelete,
      cancelDelete,
      executeDelete,
    };
  }
});
</script>

<style scoped>
/* Using styles similar to WorldLocationList for consistency */
.character-tag-type-manager {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.detail-section h3 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #333;
}

.loading-state, .error-message, .empty-state {
  padding: 2rem;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

/* Simple styling for the list */
.v-list {
  padding: 0;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.v-list-item {
  border-bottom: 1px solid #e0e0e0;
}

.v-list-item:last-child {
  border-bottom: none;
}

</style> 