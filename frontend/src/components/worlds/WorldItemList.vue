<template>
  <section class="item-list-section detail-section">
    <!-- Remove the internal section header -->
    <!-- 
    <div class="section-header">
      <h2>Items</h2>
      <button v-if="canManage" @click="$emit('open-add-item')" class="btn btn-primary btn-sm">
        Add Item
      </button>
    </div>
    -->
    
    <div v-if="loading" class="loading-state">Loading items...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="items.length > 0">
      <ul class="entity-list">
        <li v-for="item in items" :key="item.id" class="entity-list-item">
          <div class="entity-info">
            <router-link :to="{ name: 'ItemDetail', params: { itemId: item.id } }" class="entity-name-link">
              <span class="entity-name">{{ item.name }}</span>
            </router-link>
            <div class="entity-details">
              <div 
                v-if="item.description"
                class="entity-description-preview" 
                v-html="renderDescriptionPreview(item.description)"
              ></div>
              <span v-else class="entity-description-preview text-muted"><em>No description</em></span>
              <span v-if="item.character_id" class="item-relation">Character: {{ getCharacterName(item.character_id) }}</span>
              <span v-if="item.location_id" class="item-relation">Location: {{ getLocationName(item.location_id) }}</span>
              <div v-if="item.tags && item.tags.length > 0" class="item-tags">
                <strong>Tags:</strong>
                <span v-for="tag in item.tags" :key="tag.id" class="tag-chip">
                  {{ tag.tag_type?.name || 'Unknown Tag' }} 
                </span>
              </div>
              <span class="entity-date">Created: {{ formatDateTime(item.created_at) }}</span>
            </div>
          </div>
          <div class="entity-actions">
            <button v-if="canManage" @click="$emit('edit-item', item)" class="btn-small btn-secondary">
              Edit
            </button>
            <button v-if="canManage" @click="requestDeleteConfirmation(item)" class="btn-small btn-danger">
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
    <div v-else class="empty-state">No items found for this world yet.</div>

    <!-- Use the reusable Confirmation Dialog -->
    <ConfirmDeleteModal
       :show="showDeleteConfirm"
       itemType="item"
       :itemName="itemToDelete?.name"
       :isDeleting="isDeleting"
       :error="deleteError"
       @confirm="executeDelete"
       @cancel="cancelDelete"
    />
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, type PropType } from 'vue';
import type { Item } from '@/types/item';
import type { Character } from '@/types/character';
import type { Location } from '@/types/location';
import * as itemsApi from '@/services/api/items';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue'; // Import the reusable modal
import MarkdownIt from 'markdown-it'; // Import markdown-it

export default defineComponent({
  name: 'WorldItemList',
  components: {
      ConfirmDeleteModal, // Register the modal component
  },
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
  setup(_props, { emit }) {
    const showDeleteConfirm = ref(false);
    const itemToDelete = ref<Item | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    // Initialize markdown-it
    const md = new MarkdownIt({ html: false, linkify: true });

    // Method to render description preview
    const renderDescriptionPreview = (markdown: string | null): string => {
      if (!markdown) {
        return '';
      }
      const maxLength = 100;
      let truncatedMd = markdown.length > maxLength 
        ? markdown.substring(0, maxLength) + '...' 
        : markdown;
      return md.render(truncatedMd);
    };

    const getCharacterName = (characterId: number | null): string => {
      if (!characterId) return 'Unassigned';
      // Access props via _props argument in setup
      const character = _props.characters.find(c => c.id === characterId);
      return character ? character.name : `Unknown (ID: ${characterId})`;
    };

    const getLocationName = (locationId: number | null): string => {
      if (!locationId) return 'Unassigned';
      const location = _props.locations.find(l => l.id === locationId);
      return location ? location.name : `Unknown (ID: ${locationId})`;
    };
    
    const formatDateTime = (dateTimeString: string | null): string => {
      if (!dateTimeString) return 'Unknown date';
      try {
        return new Date(dateTimeString).toLocaleDateString();
      } catch (e) {
        return dateTimeString;
      }
    };

    // Renamed function to open the confirmation modal
    const requestDeleteConfirmation = (item: Item) => {
      itemToDelete.value = item;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      itemToDelete.value = null;
      deleteError.value = null;
    };

    // Renamed function that executes the delete after confirmation
    const executeDelete = async () => {
      if (!itemToDelete.value) return;

      isDeleting.value = true;
      deleteError.value = null;

      try {
        await itemsApi.deleteItem(itemToDelete.value.id);
        emit('items-updated');
        showDeleteConfirm.value = false; // Close modal on success
        itemToDelete.value = null;
      } catch (err: any) {
        console.error('Error deleting item:', err);
        // Propagate error to the modal
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
      requestDeleteConfirmation, // Expose the renamed function
      cancelDelete,
      executeDelete, // Expose the renamed function
      renderDescriptionPreview, // Expose the method
    };
  },
});
</script>

<style scoped>
/* Adopt styles from WorldLocationList */
.detail-section { /* Renamed from .item-list-section */
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
}

.entity-list { /* Renamed from .item-list */
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.entity-list-item { /* Renamed from .item-list-item */
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e9ecef;
}

.entity-list-item:last-child {
  border-bottom: none;
}

.entity-info { /* Renamed from .item-info */
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 1rem;
}

/* Style for the clickable name link */
.entity-name-link { /* Applied to router-link */
    text-decoration: none;
    color: var(--v-theme-primary, #7851a9);
    font-weight: 600;
    cursor: pointer;
    display: inline-block;
    margin-bottom: 0.25rem;
}

.entity-name-link:hover .entity-name {
    text-decoration: underline;
}

.entity-name { /* Applied to span inside link */
  font-size: 1.1rem;
}

.entity-details { /* Renamed from .item-details */
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.entity-description-preview { /* Renamed from .item-description-preview */
  line-height: 1.4;
}

.entity-description-preview :deep(p) {
    margin: 0;
    display: inline;
}

.text-muted {
    color: #6c757d;
    font-style: italic;
}

.item-relation { /* Keep specific name for clarity */
  font-size: 0.85rem;
  font-style: italic;
}

.item-tags { /* Keep specific name */
  margin-top: 0.4rem;
  font-size: 0.85rem;
}

.item-tags strong {
  margin-right: 0.5rem;
}

.tag-chip {
  display: inline-block;
  background-color: #e0e0e0;
  color: #333;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  margin-right: 0.3rem;
  margin-bottom: 0.3rem;
  white-space: nowrap;
}

.entity-date { /* Renamed from .item-date */
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 0.25rem;
}

.entity-actions { /* Renamed from .item-actions */
  display: flex;
  gap: 0.5rem;
  align-items: flex-start; /* Align with top of info */
}

/* Consistent button styles */
.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.8rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
}
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0069d9; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.875rem; }

/* Loading/Error/Empty states */
.loading-state,
.error-message,
.empty-state {
  padding: 1rem;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dee2e6;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.error-message {
  color: #dc3545;
  border-color: #f5c6cb;
  background-color: #f8d7da;
}
</style> 