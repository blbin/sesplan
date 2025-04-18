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
            <span class="location-name">{{ location.name }}</span>
            <div class="location-details">
              <span v-if="location.description" class="location-description">{{ location.description }}</span>
              <span v-if="isChildLocation(location)" class="parent-info">
                Parent: {{ getParentName(location) }}
              </span>
              <span class="location-date">Created: {{ formatDateTime(location.created_at) }}</span>
            </div>
          </div>
          <div class="location-actions">
            <button v-if="canManage" @click="$emit('edit-location', location)" class="btn-small btn-secondary">
              Edit
            </button>
            <button v-if="canManage" @click="confirmDelete(location)" class="btn-small btn-danger">
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
    <div v-else class="empty-state">No locations found for this world yet.</div>

    <!-- Confirmation Dialog for Delete -->
    <div v-if="showDeleteConfirm" class="modal-overlay">
      <div class="modal-content confirmation-modal">
        <h3>Confirm Deletion</h3>
        <p>Are you sure you want to delete the location "{{ locationToDelete?.name }}"?</p>
        <p v-if="hasChildren(locationToDelete)" class="warning-text">
          Warning: This location has child locations that will be orphaned.
        </p>
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
import type { Location } from '@/types/location';
import * as locationsApi from '@/services/api/locations';

export default defineComponent({
  name: 'WorldLocationList',
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

    const confirmDelete = (location: Location) => {
      locationToDelete.value = location;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      locationToDelete.value = null;
      deleteError.value = null;
    };

    const handleDelete = async () => {
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

    return {
      showDeleteConfirm,
      locationToDelete,
      isDeleting,
      deleteError,
      isChildLocation,
      getParentName,
      hasChildren,
      formatDateTime,
      confirmDelete,
      cancelDelete,
      handleDelete,
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
}

.location-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
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
}

.location-name {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #212529;
  font-size: 1.1rem;
}

.location-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.location-description {
  font-size: 0.9rem;
  color: #6c757d;
}

.parent-info {
  font-size: 0.85rem;
  color: #6c757d;
  font-style: italic;
}

.location-date {
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 0.25rem;
}

.location-actions {
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

.warning-text {
  color: #856404;
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  padding: 0.75rem;
  border-radius: 0.25rem;
  margin: 0.75rem 0;
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