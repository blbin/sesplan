<template>
  <div class="create-location-form">
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
        <MarkdownEditor 
          id="location-description"
          v-model="formData.description" 
          class="form-control"
        />
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
      
      <div class="form-group">
        <label for="location-tags">Tags</label>
        <v-select
          id="location-tags"
          v-model="selectedTagTypeIds" 
          :items="availableTagTypes"
          item-title="name"
          item-value="id"
          label="Select tags"
          multiple
          chips
          closable-chips
          :loading="tagTypesLoading"
          :error-messages="tagTypesError ? [tagTypesError] : []"
          variant="outlined"
          density="compact"
        ></v-select>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting || tagTypesLoading">
          {{ isSubmitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Location') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, computed, onMounted } from 'vue';
import type { PropType } from 'vue';
import type { Location, LocationCreate, LocationUpdate } from '@/types/location';
import type { LocationTagType } from '@/types/locationTagType';
import * as locationsApi from '@/services/api/locations';
import * as locationTagTypeApi from '@/services/api/locationTagTypeService';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';

export default defineComponent({
  name: 'CreateLocationForm',
  components: {
    MarkdownEditor
  },
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
    const availableTagTypes = ref<LocationTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]);
    
    const formData = reactive({
      name: '',
      description: '',
      parent_location_id: null as number | null
    });
    
    const isEditing = !!props.locationToEdit;
    
    if (props.locationToEdit) {
      formData.name = props.locationToEdit.name;
      formData.description = props.locationToEdit.description || '';
      formData.parent_location_id = props.locationToEdit.parent_location_id || null;
      selectedTagTypeIds.value = props.locationToEdit.tags?.map(tag => tag.location_tag_type_id) || [];
    }
    
    const parentLocationOptions = computed(() => {
      return props.locations
        .filter(loc => loc.id !== props.locationToEdit?.id)
        .map(loc => ({ id: loc.id, name: loc.name }));
    });

    const fetchTagTypes = async () => {
      tagTypesLoading.value = true;
      tagTypesError.value = null;
      try {
        availableTagTypes.value = await locationTagTypeApi.getLocationTagTypes(props.worldId);
      } catch (err: any) {
        console.error('Error fetching location tag types:', err);
        tagTypesError.value = err.message || 'Failed to load tags';
      } finally {
        tagTypesLoading.value = false;
      }
    };

    onMounted(fetchTagTypes);

    const syncTags = async (locationId: number) => {
      const originalTagTypeIds = props.locationToEdit?.tags?.map(t => t.location_tag_type_id) || [];
      const currentTagTypeIds = new Set(selectedTagTypeIds.value);
      const originalTagTypeIdsSet = new Set(originalTagTypeIds);

      const tagsToAdd = selectedTagTypeIds.value.filter(id => !originalTagTypeIdsSet.has(id));
      const tagsToRemove = originalTagTypeIds.filter(id => !currentTagTypeIds.has(id));

      const addPromises = tagsToAdd.map(tagTypeId => 
        locationsApi.addTagToLocation(locationId, tagTypeId)
      );
      const removePromises = tagsToRemove.map(tagTypeId => 
        locationsApi.removeTagFromLocation(locationId, tagTypeId)
      );

      try {
        await Promise.all([...addPromises, ...removePromises]);
      } catch (err: any) {
        console.error("Error syncing tags:", err);
        error.value = `Location saved, but failed to sync tags: ${err.message}`;
      }
    };
    
    const handleSubmit = async () => {
      error.value = null;
      isSubmitting.value = true;
      let savedLocationId: number | null = null;
      
      try {
        if (isEditing && props.locationToEdit) {
          const updateData: LocationUpdate = {
            name: formData.name,
            description: formData.description || null,
            parent_location_id: formData.parent_location_id
          };
          const updatedLocation = await locationsApi.updateLocation(props.locationToEdit.id, updateData);
          savedLocationId = updatedLocation.id;
        } else {
          const createData: LocationCreate = {
            name: formData.name,
            description: formData.description || null,
            parent_location_id: formData.parent_location_id,
            world_id: props.worldId
          };
          const newLocation = await locationsApi.createLocation(createData);
          savedLocationId = newLocation.id;
        }

        if (savedLocationId) {
          await syncTags(savedLocationId);
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
      availableTagTypes,
      tagTypesLoading,
      tagTypesError,
      selectedTagTypeIds,
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

.form-group + .form-group {
  /* margin-top: 1rem; */
}
</style> 