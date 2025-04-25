<template>
  <section class="item-tag-type-manager detail-section">
    <div class="section-header">
      <h3>Manage Item Tag Types</h3>
      <v-btn color="primary" @click="openAddDialog" size="small">
        Add Tag Type
      </v-btn>
    </div>

    <div v-if="isLoading" class="loading-state">Loading item tag types...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <v-list v-else-if="tagTypes.length > 0" lines="one" density="compact">
      <v-list-item
        v-for="tagType in tagTypes"
        :key="tagType.id"
        :title="tagType.name"
      >
        <template v-slot:append>
          <v-btn icon="mdi-pencil" variant="text" size="small" @click="openEditDialog(tagType)" class="mr-2"></v-btn>
          <v-btn icon="mdi-delete" variant="text" size="small" @click="confirmDelete(tagType)"></v-btn>
        </template>
      </v-list-item>
    </v-list>
    <div v-else class="empty-state">No item tag types defined for this world yet.</div>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showDialog" persistent max-width="500px">
      <v-card :loading="isSaving">
        <v-card-title>
          <span class="headline">{{ editingTagType ? 'Edit Item Tag Type' : 'Add Item Tag Type' }}</span>
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
      itemType="item tag type"
      :itemName="tagTypeToDelete?.name"
      :isDeleting="isDeleting"
      :error="deleteError"
      @confirm="executeDelete"
      @cancel="cancelDelete"
    />

  </section>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import type { ItemTagType, ItemTagTypeCreate, ItemTagTypeUpdate } from '@/types/itemTagType';
import * as itemTagTypeApi from '@/services/api/itemTagTypeService';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
// Assume Vuetify components (v-btn, v-list, v-dialog etc.) are globally available or imported elsewhere

export default defineComponent({
  name: 'ItemTagTypeManager',
  components: { ConfirmDeleteModal },
  props: {
    worldId: {
      type: Number,
      required: true,
    },
  },
  emits: ['tagTypesUpdated'], // Emit event when tag types change
  setup(props, { emit }) {
    const tagTypes = ref<ItemTagType[]>([]);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    const showDialog = ref(false);
    const editingTagType = ref<ItemTagType | null>(null);
    const tagTypeName = ref('');
    const isSaving = ref(false);
    const dialogError = ref<string | null>(null);

    const showDeleteConfirm = ref(false);
    const tagTypeToDelete = ref<ItemTagType | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    // Fetch available tag types for the world
    const fetchTagTypes = async (id: number) => {
      if (!id) {
        tagTypes.value = [];
        error.value = 'World ID is required to fetch item tag types.';
        return;
      }
      isLoading.value = true;
      error.value = null;
      tagTypes.value = [];
      try {
        tagTypes.value = await itemTagTypeApi.getItemTagTypes(id);
        emit('tagTypesUpdated', tagTypes.value); // Emit the fetched types
      } catch (err: any) {
        console.error('Error fetching item tag types:', err);
        error.value = err.message || 'Failed to load item tag types';
      } finally {
        isLoading.value = false;
      }
    };

    // Fetch tag types when component mounts or worldId changes
    onMounted(() => {
      fetchTagTypes(props.worldId);
    });

    watch(() => props.worldId, (newWorldId) => {
      fetchTagTypes(newWorldId);
    });

    const openAddDialog = () => {
      editingTagType.value = null;
      tagTypeName.value = '';
      dialogError.value = null;
      showDialog.value = true;
    };

    const openEditDialog = (tagType: ItemTagType) => {
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
      if (!tagTypeName.value || !props.worldId) return;
      isSaving.value = true;
      dialogError.value = null;
      try {
        let savedTagType;
        if (editingTagType.value) {
          const updateData: ItemTagTypeUpdate = { name: tagTypeName.value };
          savedTagType = await itemTagTypeApi.updateItemTagType(props.worldId, editingTagType.value.id, updateData);
          // Update in local list
          const index = tagTypes.value.findIndex(t => t.id === editingTagType.value!.id);
          if (index !== -1) {
            tagTypes.value[index] = savedTagType;
          }
        } else {
          const createData: ItemTagTypeCreate = { name: tagTypeName.value };
          savedTagType = await itemTagTypeApi.createItemTagType(props.worldId, createData);
          // Add to local list
          tagTypes.value.push(savedTagType);
        }
        emit('tagTypesUpdated', tagTypes.value); // Emit updated list
        closeDialog();
      } catch (err: any) {
        console.error('Error saving item tag type:', err);
        dialogError.value = err.response?.data?.detail || err.message || 'Failed to save tag type';
      } finally {
        isSaving.value = false;
      }
    };

    const confirmDelete = (tagType: ItemTagType) => {
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
      if (!tagTypeToDelete.value || !props.worldId) return;
      isDeleting.value = true;
      deleteError.value = null;
      try {
        await itemTagTypeApi.deleteItemTagType(props.worldId, tagTypeToDelete.value.id);
        tagTypes.value = tagTypes.value.filter(t => t.id !== tagTypeToDelete.value!.id);
        emit('tagTypesUpdated', tagTypes.value); // Emit updated list
        cancelDelete(); // Close confirmation dialog
      } catch (err: any) {
        console.error('Error deleting item tag type:', err);
        deleteError.value = err.response?.data?.detail || err.message || 'Failed to delete tag type';
      } finally {
        isDeleting.value = false;
      }
    };

    return {
      tagTypes,
      isLoading,
      error,
      showDialog,
      editingTagType,
      tagTypeName,
      isSaving,
      dialogError,
      showDeleteConfirm,
      tagTypeToDelete,
      isDeleting,
      deleteError,
      fetchTagTypes, // Expose if needed externally, maybe not necessary
      openAddDialog,
      openEditDialog,
      closeDialog,
      saveTagType,
      confirmDelete,
      cancelDelete,
      executeDelete,
    };
  },
});
</script>

<style scoped>
/* Add specific styles for ItemTagTypeManager if needed */
/* Reuse styles from LocationTagTypeManager or global styles */
.detail-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: #f9f9f9; /* Light background for the section */
  border-radius: 8px;
  border: 1px solid #eee;
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
  font-size: 1.2rem;
  font-weight: 500;
}

.loading-state, .empty-state, .error-message {
  padding: 1rem;
  text-align: center;
  color: #666;
}

.error-message {
  color: red; /* Or use Vuetify's error color */
  border: 1px solid red;
  background-color: #ffebee;
  border-radius: 4px;
}



.v-list-item .v-btn {
  color: #666; /* Icon button color */
}

/* Adjust dialog styles if necessary */
.v-card-title .headline {
  font-size: 1.25rem;
}

</style> 