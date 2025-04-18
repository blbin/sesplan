<template>
  <div class="create-location-form">
    <h3>{{ isEditing ? 'Edit Location' : 'Add Location' }}</h3>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="location-name">Location Name *</label>
        <input 
          id="location-name"
          v-model="formData.name" 
          type="text" 
          class="form-control"
          required
        >
      </div>
      
      <div class="form-group">
        <label for="location-description">Description</label>
        <textarea 
          id="location-description"
          v-model="formData.description" 
          class="form-control"
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="parent-location">Parent Location</label>
        <select 
          id="parent-location"
          v-model="formData.parent_location_id" 
          class="form-control"
        >
          <option :value="null">None</option>
          <option 
            v-for="option in parentLocationOptions" 
            :key="option.id" 
            :value="option.id"
          >
            {{ option.name }}
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
          {{ isSubmitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Location') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed } from 'vue';
import type { PropType } from 'vue';
import type { Location, LocationCreate, LocationUpdate } from '@/types/location';
import * as locationsApi from '@/services/api/locations';

export default defineComponent({
  name: 'CreateLocationForm',
  props: {
    worldId: {
      type: Number,
      required: true,
    },
    locationToEdit: {
      type: Object as PropType<Location | null>,
      default: null
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
      parent_location_id: null as number | null
    });
    
    // Initialize form if editing
    if (props.locationToEdit) {
      formData.name = props.locationToEdit.name;
      formData.description = props.locationToEdit.description || '';
      formData.parent_location_id = props.locationToEdit.parent_location_id || null;
    }
    
    const isEditing = !!props.locationToEdit;
    
    // Filter out the current location from parent options to prevent circular references
    const parentLocationOptions = computed(() => {
      return props.locations
        .filter(loc => loc.id !== props.locationToEdit?.id)
        .map(loc => ({ id: loc.id, name: loc.name }));
    });
    
    const handleSubmit = async () => {
      error.value = null;
      isSubmitting.value = true;
      
      try {
        if (isEditing && props.locationToEdit) {
          // Update existing location
          const updateData: LocationUpdate = {
            name: formData.name,
            description: formData.description || null,
            parent_location_id: formData.parent_location_id
          };
          await locationsApi.updateLocation(props.locationToEdit.id, updateData);
        } else {
          // Create new location
          const createData: LocationCreate = {
            name: formData.name,
            description: formData.description || null,
            parent_location_id: formData.parent_location_id,
            world_id: props.worldId
          };
          await locationsApi.createLocation(createData);
        }
        
        emit('saved');
      } catch (err: any) {
        console.error('Error saving location:', err);
        error.value = err.response?.data?.detail || err.message || 'Failed to save location';
      } finally {
        isSubmitting.value = false;
      }
    };
    
    return {
      formData,
      isSubmitting,
      error,
      isEditing,
      parentLocationOptions,
      handleSubmit
    };
  }
});
</script>

<style scoped>
.create-location-form {
  padding: 1.5rem;
}

.create-location-form h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
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
}

textarea.form-control {
  resize: vertical;
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