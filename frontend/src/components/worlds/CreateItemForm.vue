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
      
      <div v-if="error" class="error-message">
        {{ error }}
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
import { defineComponent, reactive, ref } from 'vue';
import type { PropType } from 'vue';
import type { Item, ItemCreate, ItemUpdate } from '@/types/item';
import type { Character } from '@/types/character';
import type { Location } from '@/types/location';
import * as itemsApi from '@/services/api/items';

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
    }
  },
  emits: ['saved', 'cancel'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const error = ref<string | null>(null);
    
    const formData = reactive({
      name: '',
      description: '',
      character_id: null as number | null,
      location_id: null as number | null,
    });
    
    const isEditing = !!props.itemToEdit;
    
    // Initialize form if editing
    if (props.itemToEdit) {
      formData.name = props.itemToEdit.name;
      formData.description = props.itemToEdit.description || '';
      formData.character_id = props.itemToEdit.character_id || null;
      formData.location_id = props.itemToEdit.location_id || null;
    }
    
    const handleSubmit = async () => {
      error.value = null;
      isSubmitting.value = true;
      
      try {
        if (isEditing && props.itemToEdit) {
          // Update existing item
          const updateData: ItemUpdate = {
            name: formData.name || undefined,
            description: formData.description || null,
            character_id: formData.character_id,
            location_id: formData.location_id
          };
          if (!formData.name) delete updateData.name; 

          await itemsApi.updateItem(props.itemToEdit.id, updateData);
        } else {
          // Create new item
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
          await itemsApi.createItem(createData);
        }
        
        emit('saved');
      } catch (err: any) {
        console.error('Error saving item:', err);
        error.value = err.response?.data?.detail || err.message || 'Failed to save item';
      } finally {
        isSubmitting.value = false;
      }
    };
    
    return {
      formData,
      isSubmitting,
      error,
      isEditing,
      handleSubmit
    };
  }
});
</script>

<style scoped>
/* Styly jsou velmi podobné CreateLocationForm */
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
    appearance: none; /* Optional: for custom arrow styling */
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
</style> 