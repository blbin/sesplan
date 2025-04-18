<template>
  <section class="item-list-section detail-section">
    <div class="section-header">
      <h2>Items</h2>
      <button v-if="canManage" @click="$emit('open-add-item')" class="btn btn-primary btn-sm">
        Add Item
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">Loading items...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="items.length > 0">
      <ul class="item-list">
        <li v-for="item in items" :key="item.id" class="item-list-item">
          <div class="item-info">
            <span class="item-name">{{ item.name }}</span>
            <div class="item-details">
              <span v-if="item.description" class="item-description">{{ item.description }}</span>
              <span v-if="item.character_id" class="item-relation">Character: {{ getCharacterName(item.character_id) }}</span>
              <span v-if="item.location_id" class="item-relation">Location: {{ getLocationName(item.location_id) }}</span>
              <span class="item-date">Created: {{ formatDateTime(item.created_at) }}</span>
            </div>
          </div>
          <div class="item-actions">
            <button v-if="canManage" @click="$emit('edit-item', item)" class="btn-small btn-secondary">
              Edit
            </button>
            <button v-if="canManage" @click="confirmDelete(item)" class="btn-small btn-danger">
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
    <div v-else class="empty-state">No items found for this world yet.</div>

    <!-- Confirmation Dialog for Delete -->
    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal-content confirmation-modal">
        <h3>Confirm Deletion</h3>
        <p>Are you sure you want to delete the item "{{ itemToDelete?.name }}"?</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="cancelDelete">Cancel</button>
          <button class="btn btn-danger" @click="handleDelete" :disabled="isDeleting">
            {{ isDeleting ? "Deleting..." : "Delete" }}
          </button>
        </div>
        <div v-if="deleteError" class="error-message mt-3">{{ deleteError }}</div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import type { PropType } from 'vue';
import type { Item } from '@/types/item';
import type { Character } from '@/types/character';
import type { Location } from '@/types/location';
import * as itemsApi from '@/services/api/items';

export default defineComponent({
  name: 'WorldItemList',
  props: {
    items: {
      type: Array as PropType<Item[]>,
      required: true,
    },
    characters: {
      type: Array as PropType<Character[]>,
      required: true,
    },
    locations: {
      type: Array as PropType<Location[]>,
      required: true,
    },
    worldId: {
      type: Number,
      required: true,
    },
    canManage: {
      type: Boolean,
      default: false,
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
  emits: ['items-updated', 'open-add-item', 'edit-item'],
  setup(props, { emit }) {
    const showDeleteConfirm = ref(false);
    const itemToDelete = ref<Item | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    const getCharacterName = (characterId: number | null): string => {
      if (!characterId) return 'Unassigned';
      const character = props.characters.find(c => c.id === characterId);
      return character ? character.name : `Unknown Character (ID: ${characterId})`;
    };

    const getLocationName = (locationId: number | null): string => {
      if (!locationId) return 'Unassigned';
      const location = props.locations.find(l => l.id === locationId);
      return location ? location.name : `Unknown Location (ID: ${locationId})`;
    };
    
    const formatDateTime = (dateTimeString: string | null): string => {
      if (!dateTimeString) return 'Unknown date';
      try {
        return new Date(dateTimeString).toLocaleDateString();
      } catch (e) {
        return dateTimeString;
      }
    };

    const confirmDelete = (item: Item) => {
      itemToDelete.value = item;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      itemToDelete.value = null;
      deleteError.value = null;
    };

    const handleDelete = async () => {
      if (!itemToDelete.value) return;
      
      isDeleting.value = true;
      deleteError.value = null;
      
      try {
        await itemsApi.deleteItem(itemToDelete.value.id);
        emit('items-updated');
        showDeleteConfirm.value = false;
        itemToDelete.value = null;
      } catch (err: any) {
        console.error('Error deleting item:', err);
        deleteError.value = err.response?.data?.detail || err.message || 'Failed to delete item';
      } finally {
        isDeleting.value = false;
      }
    };

    return {
      showDeleteConfirm,
      itemToDelete,
      isDeleting,
      deleteError,
      getCharacterName,
      getLocationName,
      formatDateTime,
      confirmDelete,
      cancelDelete,
      handleDelete,
    };
  },
});
</script>

<style scoped>
/* Použijeme velmi podobné styly jako WorldLocationList */
.item-list-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.detail-section h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
}

.item-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s ease;
}

.item-list-item:hover {
  background-color: #f8f9fa;
}

.item-list-item:last-child {
  border-bottom: none;
}

.item-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 1rem; /* Space before actions */
}

.item-name {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #212529;
  font-size: 1.1rem;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.item-description {
  font-size: 0.9rem;
  color: #6c757d;
}

.item-relation {
  font-size: 0.85rem;
  color: #6c757d;
  font-style: italic;
}

.item-date {
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 0.25rem;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
  align-self: flex-start;
}

.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
}

.loading-state,
.error-message,
.empty-state {
  padding: 1.5rem;
  text-align: center;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.loading-state {
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}

.error-message {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.empty-state {
  color: #6c757d;
  font-style: italic;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}

/* Modal styles - stejné jako u WorldLocationList */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.confirmation-modal h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #212529;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 0.3rem;
  cursor: pointer;
  border: none;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mt-3 {
  margin-top: 1rem;
}
</style> 