<template>
  <section class="location-list-section detail-section">
    <div class="section-header">
      <h2>Locations</h2>
      <button v-if="canManage" @click="$emit('open-add-location')" class="btn btn-primary btn-sm">
        Add Location
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">Loading locations...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="locations.length > 0">
      <ul class="location-list">
        <li v-for="location in locations" :key="location.id" class="location-item">
          <div class="location-info">
            <span @click="goToLocationDetail(location.id)" class="location-name-link">
              <span class="location-name">{{ location.name }}</span>
            </span>
            <div class="location-details">
              <span v-if="location.description" class="location-description">{{ location.description }}</span>
              <span v-if="isChildLocation(location)" class="parent-info">
                Parent: {{ getParentName(location) }}
              </span>
              <div v-if="location.tags && location.tags.length" class="tags-container">
                <v-chip
                  v-for="tag in location.tags"
                  :key="tag.id"
                  size="small"
                  label
                  class="mr-1 mb-1"
                  density="compact" 
                  >
                  {{ tag.tag_type?.name || `Tag ID: ${tag.location_tag_type_id}` }}
                </v-chip>
              </div>
              <span class="location-date">Created: {{ formatDateTime(location.created_at) }}</span>
            </div>
          </div>
          <div class="location-actions">
            <button v-if="canManage" @click="$emit('edit-location', location)" class="btn-small btn-secondary">
              Edit
            </button>
            <button v-if="canManage" @click="requestDeleteConfirmation(location)" class="btn-small btn-danger">
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
    <div v-else class="empty-state">No locations found for this world yet.</div>

    <!-- Use the reusable Confirmation Dialog -->
    <ConfirmDeleteModal
      :show="showDeleteConfirm"
      itemType="location"
      :itemName="locationToDelete?.name"
      :isDeleting="isDeleting"
      :error="deleteError"
      @confirm="executeDelete"
      @cancel="cancelDelete"
    >
      <!-- Add specific warning for locations with children -->
      <template #additional-warning>
        <p v-if="hasChildren(locationToDelete)" class="warning-text">
          Warning: This location has child locations that will be orphaned (their parent will be set to null).
        </p>
      </template>
    </ConfirmDeleteModal>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, type PropType } from 'vue';
import { useRouter } from 'vue-router';
import type { Location } from '@/types/location';
import * as locationsApi from '@/services/api/locations';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue'; // Import the reusable modal

export default defineComponent({
  name: 'WorldLocationList',
  components: {
      ConfirmDeleteModal, // Register the modal component
  },
  props: {
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
  emits: ['locations-updated', 'open-add-location', 'edit-location'],
  setup(props, { emit }) {
    const router = useRouter();
    const showDeleteConfirm = ref(false);
    const locationToDelete = ref<Location | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    const isChildLocation = (location: Location): boolean => {
      return location.parent_location_id !== null;
    };

    const getParentName = (location: Location): string => {
      if (!location.parent_location_id) return '';
      
      const parent = props.locations.find(loc => loc.id === location.parent_location_id);
      return parent ? parent.name : `Unknown (ID: ${location.parent_location_id})`;
    };

    const hasChildren = (location: Location | null): boolean => {
      if (!location) return false;
      return props.locations.some(loc => loc.parent_location_id === location.id);
    };
    
    const formatDateTime = (dateTimeString: string | null): string => {
      if (!dateTimeString) return 'Unknown date';
      try {
        return new Date(dateTimeString).toLocaleDateString();
      } catch (e) {
        return dateTimeString;
      }
    };

    const requestDeleteConfirmation = (location: Location) => {
      locationToDelete.value = location;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      locationToDelete.value = null;
      deleteError.value = null;
    };

    const executeDelete = async () => {
      if (!locationToDelete.value) return;
      
      isDeleting.value = true;
      deleteError.value = null;
      
      try {
        await locationsApi.deleteLocation(locationToDelete.value.id);
        emit('locations-updated');
        showDeleteConfirm.value = false;
        locationToDelete.value = null;
      } catch (err: any) {
        console.error('Error deleting location:', err);
        deleteError.value = err.response?.data?.detail || err.message || 'Failed to delete location';
      } finally {
        isDeleting.value = false;
      }
    };

    const goToLocationDetail = (locationId: number) => {
      console.log(`Navigating to location detail: worldId=${props.worldId}, locationId=${locationId}`);
      router.push({ 
        name: 'LocationDetail',
        params: { locationId: locationId },
      });
    };

    return {
      showDeleteConfirm,
      locationToDelete,
      isDeleting,
      deleteError,
      isChildLocation,
      getParentName,
      hasChildren,
      formatDateTime,
      requestDeleteConfirmation,
      cancelDelete,
      executeDelete,
      goToLocationDetail,
    };
  },
});
</script>

<style scoped>
.location-list-section {
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

.location-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.location-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s ease;
}

.location-item:hover {
  background-color: #f8f9fa;
}

.location-item:last-child {
  border-bottom: none;
}

.location-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 1rem;
}

.location-name-link {
    cursor: pointer;
    text-decoration: none;
    color: inherit;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.5rem;
}
.location-name-link:hover .location-name {
    text-decoration: underline;
    color: #5f3f87;
}
.location-name {
  color: #212529;
  font-size: 1.1rem;
}

.location-details {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.location-description {
  font-size: 0.9rem;
  color: #6c757d;
  line-height: 1.4;
}

.parent-info {
  font-size: 0.85rem;
  color: #495057;
}

.location-date {
  font-size: 0.8rem;
  color: #adb5bd;
}

.tags-container {
  margin-top: 0.5rem;
}

.location-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-small {
  padding: 0.25rem 0.6rem;
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
  background-color: #7851a9;
  color: white;
}

.btn-sm.btn-primary:hover {
  background-color: #5f3f87;
}

.loading-state,
.error-message,
.empty-state {
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

.warning-text {
  color: #ffc107;
  font-size: 0.9em;
  margin-top: 0.5em;
}
</style> 