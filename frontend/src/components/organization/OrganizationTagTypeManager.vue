<template>
  <div class="tag-type-manager">
    <h3>Manage Organization Tag Types</h3>

    <!-- Loading and Error States -->
    <div v-if="loading" class="loading-state">Loading tag types...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <!-- Tag Type List -->
    <ul v-else-if="tagTypes.length > 0" class="tag-type-list">
      <li v-for="tagType in tagTypes" :key="tagType.id" class="tag-type-item">
        <span v-if="!editingTagTypeId || editingTagTypeId !== tagType.id">
          {{ tagType.name }}
        </span>
        <!-- Edit Input -->
        <input 
          v-else 
          type="text" 
          v-model="editingTagName" 
          @keyup.enter="saveEdit(tagType.id)"
          @keyup.esc="cancelEdit"
          ref="editInput"
          class="edit-input"
        />
        <div class="actions">
          <button v-if="!editingTagTypeId || editingTagTypeId !== tagType.id" @click="startEdit(tagType)" class="btn-small btn-secondary">Edit</button>
          <button v-if="editingTagTypeId === tagType.id" @click="saveEdit(tagType.id)" class="btn-small btn-primary">Save</button>
          <button v-if="editingTagTypeId === tagType.id" @click="cancelEdit" class="btn-small btn-secondary">Cancel</button>
          <button @click="requestDeleteConfirmation(tagType)" class="btn-small btn-danger">Delete</button>
        </div>
      </li>
    </ul>
    <div v-else class="empty-state">No organization tag types defined for this world yet.</div>

    <!-- Add New Tag Type Form -->
    <div class="add-form">
      <h4>Add New Tag Type</h4>
      <input 
        type="text" 
        v-model.trim="newTagName" 
        placeholder="New tag type name"
        @keyup.enter="addTagType"
        maxlength="100"
        class="add-input"
      />
      <button @click="addTagType" :disabled="!newTagName || isAdding" class="btn btn-primary">
        {{ isAdding ? 'Adding...' : 'Add' }}
      </button>
      <div v-if="addError" class="error-message add-error">{{ addError }}</div>
    </div>

    <!-- Delete Confirmation Modal -->
    <ConfirmDeleteModal
      :show="showDeleteConfirm"
      itemType="organization tag type"
      :itemName="tagTypeToDelete?.name"
      :isDeleting="isDeleting"
      :error="deleteError"
      @confirm="executeDelete"
      @cancel="cancelDelete"
    >
     <template #additional-warning>
        <p class="warning-text">
          Warning: Deleting this tag type will also remove it from all organizations it's assigned to.
        </p>
      </template>
    </ConfirmDeleteModal>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, type PropType, nextTick, watch } from 'vue'; // Remove computed
import type { OrganizationTagType } from '@/types/organizationTagType';
import * as tagTypeApi from '@/services/api/organizationTagTypeService'; // Use the correct service
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';

export default defineComponent({
  name: 'OrganizationTagTypeManager',
  components: { ConfirmDeleteModal },
  props: {
    worldId: {
      type: Number,
      required: true,
    },
    initialTagTypes: {
      type: Array as PropType<OrganizationTagType[]>,
      required: true,
    },
    loading: {
        type: Boolean,
        default: false,
    },
    error: {
        type: String,
        default: '',
    },
  },
  emits: ['tag-types-updated'],
  setup(props, { emit }) {
    const tagTypes = ref<OrganizationTagType[]>([...props.initialTagTypes]);
    const newTagName = ref('');
    const isAdding = ref(false);
    const addError = ref<string | null>(null);
    
    const editingTagTypeId = ref<number | null>(null);
    const editingTagName = ref('');
    const editInput = ref<HTMLInputElement | null>(null); // Ref for the edit input element

    const showDeleteConfirm = ref(false);
    const tagTypeToDelete = ref<OrganizationTagType | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    // Update internal list when initial prop changes
    watch(() => props.initialTagTypes, (newVal) => {
        tagTypes.value = [...newVal];
    }, { deep: true });

    const addTagType = async () => {
      if (!newTagName.value || isAdding.value) return;
      isAdding.value = true;
      addError.value = null;
      try {
        // worldId is passed as first argument
        await tagTypeApi.createOrganizationTagType(props.worldId, { name: newTagName.value });
        newTagName.value = '';
        emit('tag-types-updated'); // Notify parent to refetch
      } catch (err: any) {
        console.error("Error adding organization tag type:", err);
        addError.value = err.response?.data?.detail || err.message || 'Failed to add tag type';
      } finally {
        isAdding.value = false;
      }
    };

    const startEdit = (tagType: OrganizationTagType) => {
      editingTagTypeId.value = tagType.id;
      editingTagName.value = tagType.name;
      nextTick(() => {
        editInput.value?.focus(); // Focus the input field
      });
    };

    const cancelEdit = () => {
      editingTagTypeId.value = null;
      editingTagName.value = '';
    };

    const saveEdit = async (tagTypeId: number) => {
       if (!editingTagName.value || editingTagTypeId.value !== tagTypeId) return;
       // Optionally add loading state for editing
       try {
         await tagTypeApi.updateOrganizationTagType(props.worldId, tagTypeId, { name: editingTagName.value });
         cancelEdit();
         emit('tag-types-updated');
       } catch (err: any) {
          console.error("Error updating organization tag type:", err);
          // Handle error display, maybe near the input
          alert(`Failed to update tag type: ${err.response?.data?.detail || err.message}`); 
       }
    };

    const requestDeleteConfirmation = (tagType: OrganizationTagType) => {
      tagTypeToDelete.value = tagType;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      tagTypeToDelete.value = null;
    };

    const executeDelete = async () => {
      if (!tagTypeToDelete.value) return;
      isDeleting.value = true;
      deleteError.value = null;
      try {
        await tagTypeApi.deleteOrganizationTagType(props.worldId, tagTypeToDelete.value.id);
        emit('tag-types-updated');
        cancelDelete(); // Close modal on success
      } catch (err: any) {
        console.error("Error deleting organization tag type:", err);
        deleteError.value = err.response?.data?.detail || err.message || 'Failed to delete tag type';
        // Keep modal open on error to show message
      } finally {
        isDeleting.value = false;
      }
    };

    return {
      tagTypes,
      newTagName,
      isAdding,
      addError,
      addTagType,
      editingTagTypeId,
      editingTagName,
      editInput,
      startEdit,
      cancelEdit,
      saveEdit,
      showDeleteConfirm,
      tagTypeToDelete,
      isDeleting,
      deleteError,
      requestDeleteConfirmation,
      cancelDelete,
      executeDelete,
    };
  },
});
</script>

<style scoped>
.tag-type-manager {
  padding: 1rem;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.3rem;
}

h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

h4 {
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
    font-size: 1.1rem;
}

.tag-type-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem 0;
}

.tag-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.8rem;
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.add-form {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
}

.add-input, .edit-input {
  flex-grow: 1;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

.btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    /* ... other button styles ... */
}

.btn-small {
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
}

/* Basic button colors (ensure these classes exist globally or define here) */
.btn-primary {
    background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;
}
.btn-secondary {
    background-color: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;
}
.btn-danger {
    background-color: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;
}
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger:hover { background-color: #c82333; }
.btn:disabled {
    opacity: 0.65; cursor: not-allowed;
}

.loading-state,
.empty-state,
.error-message {
  padding: 1rem;
  text-align: center;
  color: #6c757d;
  background-color: #e9ecef;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #721c24; /* Dark red */
  background-color: #f8d7da; /* Light red */
  border-color: #f5c6cb; /* Red border */
}

.add-error {
    width: 100%; /* Make error message span full width below input/button */
    margin-top: 0.5rem;
    text-align: left;
}

.warning-text {
  color: #856404; /* Dark yellow */
  background-color: #fff3cd; /* Light yellow */
  border: 1px solid #ffeeba; /* Yellow border */
  padding: 0.75rem;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}
</style> 