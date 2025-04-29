<template>
  <div class="location-detail-view">
    <div v-if="loading" class="loading-message">Loading location details...</div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="location" class="location-content">
      <header class="view-header">
        <h1>{{ location.name }}</h1>
        <router-link v-if="backToWorldRoute.params?.worldId" :to="backToWorldRoute" class="btn btn-secondary">
          Back to World
        </router-link>
        <button @click="openEditModal" class="btn btn-primary">Edit Location</button>
      </header>

      <div class="details-section">
        <h2>Details</h2>
        <div class="description-section">
          <div class="description-header">
            <strong>Description:</strong>
            <v-btn 
              v-if="!isEditingDescription"
              icon="mdi-pencil" 
              variant="text" 
              size="x-small" 
              @click="startEditingDescription"
              class="ml-2"
              title="Edit Description"
            ></v-btn>
          </div>
          
          <!-- Display Mode -->
          <div v-if="!isEditingDescription" class="description-content mt-2" v-html="renderedDescription"></div>
          
          <!-- Edit Mode -->
          <div v-else class="description-editor mt-2">
            <MarkdownEditor v-model="editableDescription" />
            <div v-if="saveDescriptionError" class="error-message mt-2">{{ saveDescriptionError }}</div>
            <div class="editor-actions mt-2">
              <v-btn 
                size="small" 
                @click="cancelDescriptionEdit"
                :disabled="isSavingDescription"
              >Cancel</v-btn>
              <v-btn 
                color="primary" 
                size="small" 
                @click="saveDescription"
                :loading="isSavingDescription"
                :disabled="!isDescriptionChanged"
              >Save</v-btn>
            </div>
          </div>
        </div>
        
        <p v-if="location.parent_location_id" class="mt-4">
          <strong>Parent Location:</strong> 
          <span v-if="parentLocationName">{{ parentLocationName }} (ID: {{ location.parent_location_id }})</span>
          <span v-else>ID: {{ location.parent_location_id }}</span>
        </p>
        <p><strong>World ID:</strong> {{ worldId }}</p>
        <p><strong>Created:</strong> {{ formatDate(location.created_at) }}</p>
        <p><strong>Updated:</strong> {{ formatDate(location.updated_at) }}</p>
      </div>

      <div class="details-section tags-section">
        <h2>Tags</h2>
        <div v-if="location.tags && location.tags.length > 0" class="tags-container">
            <span
              v-for="tag in location.tags"
              :key="tag.id"
              class="tag-chip"
            >
              {{ tag.tag_type?.name || `Tag ID: ${tag.location_tag_type_id}` }}
            </span>
        </div>
        <p v-else>No tags assigned.</p>
        <button @click="openTagEditDialog" class="btn btn-secondary mt-2">Edit Tags</button>
      </div>

      <!-- Správa typů tagů -->
      <div class="details-section">
        <div class="section-header">
          <h2>Manage Location Tag Types</h2>
          <button @click="openAddTagTypeDialog" class="btn btn-primary">Add Tag Type</button>
        </div>

        <div v-if="tagTypesLoading" class="loading-state">Loading tag types...</div>
        <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
        <div v-else-if="availableTagTypes.length > 0" class="tag-types-list">
          <div v-for="tagType in availableTagTypes" :key="tagType.id" class="tag-type-item">
            <span class="tag-type-name">{{ tagType.name }}</span>
            <div class="tag-type-actions">
              <button @click="openEditTagTypeDialog(tagType)" class="btn-icon">✏️</button>
              <button @click="confirmDeleteTagType(tagType)" class="btn-icon">🗑️</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">No location tag types defined for this world yet.</div>
      </div>

      <!-- Edit Location Modal -->
      <div v-if="showEditModal" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Edit Location</h3>
            <button @click="closeEditModal" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="locationsLoading">Loading available parent locations...</div>
            <div v-else-if="locationsError">{{ locationsError }}</div>
            <CreateLocationForm
              v-else-if="numericWorldId && !locationsLoading" 
              :worldId="numericWorldId" 
              :locations="worldLocations" 
              :locationToEdit="location"
              @saved="handleLocationSaved"
              @cancel="closeEditModal"
            />
            <div v-else>Loading world context...</div>
          </div>
        </div>
      </div>

      <!-- Edit Tags Modal -->
      <div v-if="showTagEditDialog" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Edit Tags for {{ location.name }}</h3>
            <button @click="closeTagEditDialog" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="tagTypesLoading">Loading tag types...</div>
            <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
            <div v-else>
              <div class="form-group">
                <label>Select Tags:</label>
                <div class="tag-checkboxes">
                  <div v-for="tagType in availableTagTypes" :key="tagType.id" class="tag-checkbox">
                    <input 
                      type="checkbox" 
                      :id="'tag-' + tagType.id" 
                      :value="tagType.id" 
                      v-model="selectedTagTypeIds"
                    >
                    <label :for="'tag-' + tagType.id">{{ tagType.name }}</label>
                  </div>
                </div>
                <div v-if="availableTagTypes.length === 0" class="empty-tags-message">
                  No tag types available. Create some first.
                </div>
              </div>
              <div v-if="tagSyncError" class="error-message">{{ tagSyncError }}</div>
              <div class="form-actions">
                <button @click="closeTagEditDialog" class="btn btn-secondary">Cancel</button>
                <button 
                  @click="saveTags" 
                  class="btn btn-primary" 
                  :disabled="tagTypesLoading || isSavingTags"
                >
                  {{ isSavingTags ? 'Saving...' : 'Save Tags' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Tag Type Modal -->
      <div v-if="showTagTypeDialog" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ editingTagType ? 'Edit Tag Type' : 'Add Tag Type' }}</h3>
            <button @click="closeTagTypeDialog" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="tagTypeName">Tag Type Name:</label>
              <input 
                type="text" 
                id="tagTypeName" 
                v-model="tagTypeName" 
                class="form-control" 
                :class="{ 'error': tagTypeDialogError }"
                @keyup.enter="saveTagType"
              >
              <div v-if="tagTypeDialogError" class="error-message">{{ tagTypeDialogError }}</div>
            </div>
            <div class="form-actions">
              <button @click="closeTagTypeDialog" class="btn btn-secondary">Cancel</button>
              <button 
                @click="saveTagType" 
                class="btn btn-primary" 
                :disabled="!tagTypeName || isSavingTagType"
              >
                {{ isSavingTagType ? 'Saving...' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Tag Type Confirmation Modal -->
      <div v-if="showDeleteTagTypeConfirm" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Confirm Delete</h3>
            <button @click="cancelDeleteTagType" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete tag type "{{ tagTypeToDelete?.name }}"?</p>
            <div v-if="deleteTagTypeError" class="error-message">{{ deleteTagTypeError }}</div>
            <div class="form-actions">
              <button @click="cancelDeleteTagType" class="btn btn-secondary">Cancel</button>
              <button 
                @click="executeDeleteTagType" 
                class="btn btn-danger" 
                :disabled="isDeletingTagType"
              >
                {{ isDeletingTagType ? 'Deleting...' : 'Delete' }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, watch } from 'vue';
import type { Location, LocationUpdate } from '@/types/location';
import type { LocationTagType } from '@/types/locationTagType';
import * as locationsApi from '@/services/api/locations';
import * as locationTagTypeApi from '@/services/api/locationTagTypeService';
import CreateLocationForm from '@/components/worlds/CreateLocationForm.vue';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';
import MarkdownIt from 'markdown-it';
import { formatDate } from '@/utils/dateFormatter';

export default defineComponent({
  name: 'LocationDetailView',
  components: { 
    CreateLocationForm,
    MarkdownEditor
  },
  props: {
    locationId: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const location = ref<Location | null>(null);
    const loading = ref(true);
    const error = ref<string | null>(null);
    const worldId = ref<number | null>(null);
    const showEditModal = ref(false);
    const showTagEditDialog = ref(false);
    const availableTagTypes = ref<LocationTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]);
    const tagSyncError = ref<string | null>(null);
    const isSavingTags = ref(false);
    
    // Pro Add/Edit/Delete Tag Type Modal
    const showTagTypeDialog = ref(false);
    const editingTagType = ref<LocationTagType | null>(null);
    const tagTypeName = ref('');
    const tagTypeDialogError = ref<string | null>(null);
    const isSavingTagType = ref(false);
    const showDeleteTagTypeConfirm = ref(false);
    const tagTypeToDelete = ref<LocationTagType | null>(null);
    const isDeletingTagType = ref(false);
    const deleteTagTypeError = ref<string | null>(null);

    // Nový stav pro seznam lokací
    const worldLocations = ref<Location[]>([]);
    const locationsLoading = ref(false);
    const locationsError = ref<string | null>(null);

    // Stav pro editaci popisu
    const isEditingDescription = ref(false);
    const editableDescription = ref('');
    const isSavingDescription = ref(false);
    const saveDescriptionError = ref<string | null>(null);
    const md = new MarkdownIt();

    const numericLocationId = computed(() => props.locationId);
    const numericWorldId = computed(() => worldId.value);

    const isDescriptionChanged = computed(() => {
      const currentDesc = location.value?.description ?? '';
      return currentDesc !== editableDescription.value;
    });

    const renderedDescription = computed(() => {
      return location.value?.description ? md.render(location.value.description) : '<p><em>No description provided.</em></p>';
    });
    
    const backToWorldRoute = computed(() => {
      return worldId.value ? { name: 'WorldDetail', params: { worldId: worldId.value } } : { name: 'Dashboard' };
    });

    const parentLocationName = computed(() => {
      if (!location.value?.parent_location_id || worldLocations.value.length === 0) {
        return null;
      }
      const parent = worldLocations.value.find(loc => loc.id === location.value!.parent_location_id);
      return parent ? parent.name : null;
    });

    const fetchLocationDetails = async () => {
      loading.value = true;
      error.value = null;
      try {
        const data = await locationsApi.getLocation(numericLocationId.value);
        location.value = data;
        worldId.value = data.world_id; 
        selectedTagTypeIds.value = data.tags?.map(tag => tag.location_tag_type_id) || [];
        editableDescription.value = data.description || '';
      } catch (err: any) {
        console.error('Error fetching location details:', err);
        error.value = err.response?.data?.detail || err.message || 'Failed to load location details.';
        location.value = null;
        worldId.value = null;
      } finally {
        loading.value = false;
      }
    };

    const fetchWorldLocations = async (targetWorldId: number) => {
      if (!targetWorldId) return;
      locationsLoading.value = true;
      locationsError.value = null;
      try {
        worldLocations.value = await locationsApi.getLocationsByWorld(targetWorldId);
      } catch (err: any) {
        console.error('Error fetching world locations:', err);
        locationsError.value = err.message || 'Failed to load locations list for parent selection.';
        worldLocations.value = [];
      } finally {
        locationsLoading.value = false;
      }
    };

    const fetchTagTypes = async (targetWorldId: number) => {
      if (!targetWorldId) return;
      tagTypesLoading.value = true;
      tagTypesError.value = null;
      try {
        availableTagTypes.value = await locationTagTypeApi.getLocationTagTypes(targetWorldId);
      } catch (err: any) {
        console.error('Error fetching location tag types:', err);
        tagTypesError.value = err.message || 'Failed to load tag types.';
        availableTagTypes.value = [];
      } finally {
        tagTypesLoading.value = false;
      }
    };

    const loadInitialData = async () => {
      await fetchLocationDetails();
      if (worldId.value) {
        await Promise.all([
          fetchWorldLocations(worldId.value),
          fetchTagTypes(worldId.value)
        ]);
      }
    };

    onMounted(loadInitialData);

    watch(() => props.locationId, loadInitialData);

    const openEditModal = () => {
      if (!locationsLoading.value && locationsError.value && worldId.value) {
         fetchWorldLocations(worldId.value); 
      }
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
    };
    
    const handleLocationSaved = async (savedLocation: Location) => {
      location.value = savedLocation;
      editableDescription.value = savedLocation.description || '';
      if(worldId.value) {
        await fetchWorldLocations(worldId.value);
      }
      closeEditModal();
    };

    const startEditingDescription = () => {
      editableDescription.value = location.value?.description || '';
      isEditingDescription.value = true;
    };

    const cancelDescriptionEdit = () => {
      isEditingDescription.value = false;
      saveDescriptionError.value = null;
    };

    const saveDescription = async () => {
      if (!location.value || !isDescriptionChanged.value) return;
      isSavingDescription.value = true;
      saveDescriptionError.value = null;
      try {
        const updateData: LocationUpdate = { description: editableDescription.value };
        const updatedLocation = await locationsApi.updateLocation(location.value.id, updateData);
        location.value.description = updatedLocation.description;
        isEditingDescription.value = false;
      } catch (err: any) {
        console.error("Error saving description:", err);
        saveDescriptionError.value = err.response?.data?.detail || err.message || 'Failed to save description';
      } finally {
        isSavingDescription.value = false;
      }
    };

    const openTagEditDialog = () => {
      if (!location.value) return;
      selectedTagTypeIds.value = location.value.tags?.map(t => t.location_tag_type_id) || [];
      if (worldId.value && (availableTagTypes.value.length === 0 || tagTypesError.value)) {
        fetchTagTypes(worldId.value);
      }
      tagSyncError.value = null;
      showTagEditDialog.value = true;
    };

    const closeTagEditDialog = () => {
      showTagEditDialog.value = false;
    };

    const saveTags = async () => {
      if (!location.value) return;
      isSavingTags.value = true;
      tagSyncError.value = null;
      
      const originalTagTypeIds = location.value.tags?.map(t => t.location_tag_type_id) || [];
      const currentTagTypeIds = new Set(selectedTagTypeIds.value);
      const originalTagTypeIdsSet = new Set(originalTagTypeIds);

      const tagsToAdd = selectedTagTypeIds.value.filter(id => !originalTagTypeIdsSet.has(id));
      const tagsToRemove = originalTagTypeIds.filter(id => !currentTagTypeIds.has(id));

      const addPromises = tagsToAdd.map(tagTypeId => 
        locationsApi.addTagToLocation(location.value!.id, tagTypeId)
      );
      const removePromises = tagsToRemove.map(tagTypeId => 
        locationsApi.removeTagFromLocation(location.value!.id, tagTypeId)
      );

      try {
        await Promise.all([...addPromises, ...removePromises]);
        await fetchLocationDetails();
        closeTagEditDialog();
      } catch (err: any) {
        console.error("Error syncing tags:", err);
        tagSyncError.value = err.response?.data?.detail || err.message || 'Failed to sync tags';
      } finally {
        isSavingTags.value = false;
      }
    };

    const openAddTagTypeDialog = () => {
      editingTagType.value = null;
      tagTypeName.value = '';
      tagTypeDialogError.value = null;
      showTagTypeDialog.value = true;
    };

    const openEditTagTypeDialog = (tagType: LocationTagType) => {
      editingTagType.value = tagType;
      tagTypeName.value = tagType.name;
      tagTypeDialogError.value = null;
      showTagTypeDialog.value = true;
    };

    const closeTagTypeDialog = () => {
      showTagTypeDialog.value = false;
    };

    const saveTagType = async () => {
      if (!tagTypeName.value || !worldId.value) return;
      isSavingTagType.value = true;
      tagTypeDialogError.value = null;
      try {
        if (editingTagType.value) {
          await locationTagTypeApi.updateLocationTagType(worldId.value, editingTagType.value.id, { name: tagTypeName.value });
        } else {
          await locationTagTypeApi.createLocationTagType(worldId.value, { name: tagTypeName.value });
        }
        await fetchTagTypes(worldId.value);
        closeTagTypeDialog();
      } catch (err: any) {
        console.error("Error saving tag type:", err);
        tagTypeDialogError.value = err.response?.data?.detail || err.message || 'Failed to save tag type';
      } finally {
        isSavingTagType.value = false;
      }
    };

    const confirmDeleteTagType = (tagType: LocationTagType) => {
      tagTypeToDelete.value = tagType;
      deleteTagTypeError.value = null;
      showDeleteTagTypeConfirm.value = true;
    };

    const cancelDeleteTagType = () => {
      showDeleteTagTypeConfirm.value = false;
      tagTypeToDelete.value = null;
    };

    const executeDeleteTagType = async () => {
      if (!tagTypeToDelete.value || !worldId.value) return;
      isDeletingTagType.value = true;
      deleteTagTypeError.value = null;
      try {
        await locationTagTypeApi.deleteLocationTagType(worldId.value, tagTypeToDelete.value.id);
        await fetchTagTypes(worldId.value);
        await fetchLocationDetails();
        cancelDeleteTagType();
      } catch (err: any) {
        console.error("Error deleting tag type:", err);
        deleteTagTypeError.value = err.response?.data?.detail || err.message || 'Failed to delete tag type';
      } finally {
        isDeletingTagType.value = false;
      }
    };

    return {
      location,
      loading,
      error,
      worldId,
      numericWorldId,
      formatDate,
      showEditModal,
      openEditModal,
      closeEditModal,
      handleLocationSaved,
      backToWorldRoute,
      showTagEditDialog,
      openTagEditDialog,
      closeTagEditDialog,
      availableTagTypes,
      tagTypesLoading,
      tagTypesError,
      selectedTagTypeIds,
      saveTags,
      tagSyncError,
      isSavingTags,
      showTagTypeDialog,
      editingTagType,
      tagTypeName,
      tagTypeDialogError,
      isSavingTagType,
      openAddTagTypeDialog,
      openEditTagTypeDialog,
      closeTagTypeDialog,
      saveTagType,
      showDeleteTagTypeConfirm,
      tagTypeToDelete,
      isDeletingTagType,
      deleteTagTypeError,
      confirmDeleteTagType,
      cancelDeleteTagType,
      executeDeleteTagType,
      worldLocations,
      locationsLoading,
      locationsError,
      isEditingDescription,
      editableDescription,
      isSavingDescription,
      saveDescriptionError,
      isDescriptionChanged,
      renderedDescription,
      startEditingDescription,
      cancelDescriptionEdit,
      saveDescription,
      parentLocationName,
    };
  }
});
</script>

<style scoped>
.location-detail-view {
  padding: 1rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.view-header h1 {
  margin: 0;
  font-size: 2rem;
}

.details-section {
  margin-bottom: 2rem;
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.details-section h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  color: #333;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.loading-message,
.error-message,
.loading-state,
.empty-state {
  padding: 2rem;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-message {
  color: #dc3545;
  border: 1px solid #f5c6cb;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag-chip {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 0.875rem;
}

.tag-types-list {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.tag-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.tag-type-item:last-child {
  border-bottom: none;
}

.tag-type-name {
  font-weight: 500;
}

.tag-type-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
  border-radius: 4px;
}

.btn-icon:hover {
  background-color: #f0f0f0;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  text-decoration: none;
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

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mt-2 {
  margin-top: 0.5rem;
}

/* Modal styles */
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

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.close-btn:hover {
  color: #343a40;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
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
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.form-control.error {
  border-color: #dc3545;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

.tag-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.75rem;
}

.tag-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tag-checkbox input {
  margin: 0;
}

.empty-tags-message {
  padding: 1rem;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

/* Add styles for rendered markdown if needed */
.description-content :deep(p) {
  margin-bottom: 1em;
}
.description-content :deep(a) {
  color: var(--v-theme-primary);
  text-decoration: none;
}
.description-content :deep(a:hover) {
  text-decoration: underline;
}

.description-section {
  position: relative;
  margin-bottom: 1rem;
}

.description-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.description-header strong {
  margin-right: auto;
}

.description-editor {
  border: 1px solid #e0e0e0;
  padding: 1rem;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.mt-4 {
  margin-top: 1.5rem;
}
</style> 