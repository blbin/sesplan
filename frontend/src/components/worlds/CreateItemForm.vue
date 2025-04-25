<template>
  <div class="create-item-form">
    <h3>{{ isEditing ? 'Edit Item' : 'Add New Item' }}</h3>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="item-name">Item Name *</label>
        <input 
          id="item-name"
          v-model="formData.name" 
          type="text" 
          class="form-control"
          required
        >
      </div>
      
      <div class="form-group">
        <label for="item-description">Description</label>
        <textarea 
          id="item-description"
          v-model="formData.description" 
          class="form-control"
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="item-character">Character (Optional)</label>
        <select 
          id="item-character"
          v-model="formData.character_id" 
          class="form-control"
        >
          <option :value="null">-- Unassigned --</option>
          <option 
            v-for="character in characters" 
            :key="character.id" 
            :value="character.id"
          >
            {{ character.name }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="item-location">Location (Optional)</label>
        <select 
          id="item-location"
          v-model="formData.location_id" 
          class="form-control"
        >
          <option :value="null">-- Unassigned --</option>
          <option 
            v-for="location in locations" 
            :key="location.id" 
            :value="location.id"
          >
            {{ location.name }}
          </option>
        </select>
      </div>

      <!-- Item Tags Section -->
      <div class="form-group">
        <label>Tags</label>
        <div v-if="tagTypesLoading" class="loading-state-inline">Loading tags...</div>
        <div v-else-if="tagTypesError" class="error-message-inline">{{ tagTypesError }}</div>
        <div v-else-if="localAvailableTagTypes.length > 0" class="tag-checkboxes">
          <div v-for="tagType in localAvailableTagTypes" :key="tagType.id" class="tag-checkbox">
            <input 
              type="checkbox" 
              :id="'item-tag-' + tagType.id" 
              :value="tagType.id" 
              v-model="selectedTagTypeIds"
            >
            <label :for="'item-tag-' + tagType.id">{{ tagType.name }}</label>
          </div>
        </div>
        <div v-else class="empty-state-inline">No item tag types available for this world. Create them in Settings.</div>
      </div>
      
      <div v-if="error || tagSyncError" class="error-message">
        {{ error || tagSyncError }}
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Item') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, onMounted, watch } from 'vue';
import type { PropType } from 'vue';
import type { Item, ItemCreate, ItemUpdate } from '@/types/item';
import type { Character } from '@/types/character';
import type { Location } from '@/types/location';
import type { ItemTagType } from '@/types/itemTagType';
import type { ItemTag } from '@/types/itemTag';
import * as itemsApi from '@/services/api/items';
import * as itemTagTypeApi from '@/services/api/itemTagTypeService';
import * as itemTagApi from '@/services/api/itemTagService';

export default defineComponent({
  name: 'CreateItemForm',
  props: {
    worldId: {
      type: Number,
      required: true,
    },
    itemToEdit: {
      type: Object as PropType<Item | null>,
      default: null
    },
    characters: {
      type: Array as PropType<Character[]>,
      required: true
    },
    locations: {
      type: Array as PropType<Location[]>,
      required: true
    },
  },
  emits: ['saved', 'cancel'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const error = ref<string | null>(null);
    const tagSyncError = ref<string | null>(null);
    const localAvailableTagTypes = ref<ItemTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]);
    
    const formData = reactive({
      name: '',
      description: '',
      character_id: null as number | null,
      location_id: null as number | null,
    });
    
    const isEditing = !!props.itemToEdit;

    const fetchTagTypes = async () => {
      tagTypesLoading.value = true;
      tagTypesError.value = null;
      try {
        localAvailableTagTypes.value = await itemTagTypeApi.getItemTagTypes(props.worldId);
      } catch (err: any) {
        console.error('Error fetching item tag types:', err);
        tagTypesError.value = err.message || 'Failed to load item tags';
        localAvailableTagTypes.value = [];
      } finally {
        tagTypesLoading.value = false;
      }
    };
    
    const initializeForm = () => {
       if (props.itemToEdit) {
        formData.name = props.itemToEdit.name;
        formData.description = props.itemToEdit.description || '';
        formData.character_id = props.itemToEdit.character_id || null;
        formData.location_id = props.itemToEdit.location_id || null;
        selectedTagTypeIds.value = props.itemToEdit.tags?.map((tag: ItemTag) => tag.item_tag_type_id) || [];
      } else {
        formData.name = '';
        formData.description = '';
        formData.character_id = null;
        formData.location_id = null;
        selectedTagTypeIds.value = [];
      }
    };

    onMounted(() => {
        fetchTagTypes();
        initializeForm();
    });

    watch(() => props.itemToEdit, () => {
        fetchTagTypes();
        initializeForm();
    });

    const syncTags = async (itemId: number) => {
        tagSyncError.value = null;
        const originalTagTypeIds = props.itemToEdit?.tags?.map((t: ItemTag) => t.item_tag_type_id) || [];
        const currentTagTypeIdsSet = new Set(selectedTagTypeIds.value);
        const originalTagTypeIdsSet = new Set(originalTagTypeIds);

        const tagsToAdd = selectedTagTypeIds.value.filter((id: number) => !originalTagTypeIdsSet.has(id));
        const tagsToRemove = originalTagTypeIds.filter((id: number) => !currentTagTypeIdsSet.has(id));

        const addPromises = tagsToAdd.map((tagTypeId: number) => 
            itemTagApi.addItemTagToItem(itemId, tagTypeId)
        );
        const removePromises = tagsToRemove.map((tagTypeId: number) => 
            itemTagApi.removeItemTagFromItem(itemId, tagTypeId)
        );

        try {
            await Promise.all([...addPromises, ...removePromises]);
        } catch (err: any) {
            console.error("Error syncing item tags:", err);
            tagSyncError.value = `Item saved, but failed to sync tags: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
    };
    
    const handleSubmit = async () => {
      error.value = null;
      tagSyncError.value = null;
      isSubmitting.value = true;
      let savedItemId: number | null = null;
      
      try {
        if (isEditing && props.itemToEdit) {
          const updateData: ItemUpdate = {
            name: formData.name || undefined,
            description: formData.description || null,
            character_id: formData.character_id,
            location_id: formData.location_id
          };
          if (!formData.name) delete updateData.name; 
          const updatedItem = await itemsApi.updateItem(props.itemToEdit.id, updateData);
          savedItemId = updatedItem.id;
        } else {
          if (!formData.name) {
             error.value = 'Item name is required.';
             isSubmitting.value = false;
             return;
          }
          const createData: ItemCreate = {
            name: formData.name,
            description: formData.description || null,
            character_id: formData.character_id,
            location_id: formData.location_id,
            world_id: props.worldId
          };
          const newItem = await itemsApi.createItem(createData);
          savedItemId = newItem.id;
        }
        
        if (savedItemId) {
          await syncTags(savedItemId);
        }

        emit('saved');
      } catch (err: any) {
        console.error('Error saving item:', err);
        if (!tagSyncError.value) {
          error.value = err.response?.data?.detail || err.message || 'Failed to save item';
        }
      } finally {
        isSubmitting.value = false;
      }
    };
    
    return {
      formData,
      isSubmitting,
      error,
      isEditing,
      handleSubmit,
      localAvailableTagTypes,
      tagTypesLoading,
      tagTypesError,
      selectedTagTypeIds,
      tagSyncError,
    };
  }
});
</script>

<style scoped>
.create-item-form {
  padding: 1.5rem;
}

.create-item-form h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  line-height: 1.5;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  transition: border-color .15s ease-in-out,box-shadow .15s ease-in-out;
}

.form-control:focus {
    border-color: #86b7fe;
    outline: 0;
    box-shadow: 0 0 0 0.25rem rgba(13,110,253,.25);
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

select.form-control {
    appearance: none;
}

.error-message {
  margin: 1rem 0;
  padding: 0.75rem;
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 0.25rem;
}

.form-actions {
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

.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover:not(:disabled) {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.tag-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.5rem;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.tag-checkbox input[type="checkbox"] {
  margin-right: 5px;
}

.loading-state-inline,
.empty-state-inline,
.error-message-inline {
  font-size: 0.9em;
  color: #666;
  padding: 0.2rem 0;
}

.error-message-inline {
  color: #dc3545;
}
</style> 