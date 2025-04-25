<template>
  <section class="organization-list-section detail-section">
    <div class="section-header">
      <h2>Organizations</h2>
      <button v-if="canManage" @click="$emit('open-add-organization')" class="btn btn-primary btn-sm">
        Add Organization
      </button>
    </div>
    
    <div v-if="loading" class="loading-state">Loading organizations...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="organizations.length > 0">
      <ul class="organization-list">
        <li v-for="organization in organizations" :key="organization.id" class="organization-item">
          <div class="organization-info">
            <span @click="goToOrganizationDetail(organization.id)" class="organization-name-link">
              <span class="organization-name">{{ organization.name }}</span>
            </span>
            <div class="organization-details">
              <span v-if="organization.description" class="organization-description">{{ organization.description }}</span>
              <span v-if="isChildOrganization(organization)" class="parent-info">
                Parent: {{ getParentName(organization) }}
              </span>
              <!-- Add tag display here if needed later -->
              <span class="organization-date">Created: {{ formatDateTime(organization.created_at) }}</span>
            </div>
          </div>
          <div class="organization-actions">
            <button v-if="canManage" @click="$emit('edit-organization', organization)" class="btn-small btn-secondary">
              Edit
            </button>
            <button v-if="canManage" @click="requestDeleteConfirmation(organization)" class="btn-small btn-danger">
              Delete
            </button>
          </div>
        </li>
      </ul>
    </div>
    <div v-else class="empty-state">No organizations found for this world yet.</div>

    <ConfirmDeleteModal
      :show="showDeleteConfirm"
      itemType="organization"
      :itemName="organizationToDelete?.name"
      :isDeleting="isDeleting"
      :error="deleteError"
      @confirm="executeDelete"
      @cancel="cancelDelete"
    >
      <template #additional-warning>
        <p v-if="hasChildren(organizationToDelete)" class="warning-text">
          Warning: Deleting this organization will set child organizations' parent to null.
        </p>
      </template>
    </ConfirmDeleteModal>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref, type PropType } from 'vue';
import { useRouter } from 'vue-router';
import type { Organization } from '@/types/organization';
import * as organizationsApi from '@/services/api/organizations';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
import { formatDateTime } from '@/utils/dateFormatter'; // Assuming a utility function for date formatting

export default defineComponent({
  name: 'WorldOrganizationList',
  components: {
      ConfirmDeleteModal,
  },
  props: {
    organizations: {
      type: Array as PropType<Organization[]>,
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
  emits: ['organizations-updated', 'open-add-organization', 'edit-organization'],
  setup(props, { emit }) {
    const router = useRouter();
    const showDeleteConfirm = ref(false);
    const organizationToDelete = ref<Organization | null>(null);
    const isDeleting = ref(false);
    const deleteError = ref<string | null>(null);

    const isChildOrganization = (org: Organization): boolean => {
      return org.parent_organization_id !== null && org.parent_organization_id !== undefined;
    };

    const getParentName = (org: Organization): string => {
      if (!org.parent_organization_id) return '';
      const parent = props.organizations.find(o => o.id === org.parent_organization_id);
      return parent ? parent.name : `Unknown (ID: ${org.parent_organization_id})`;
    };

    const hasChildren = (org: Organization | null): boolean => {
      if (!org) return false;
      return props.organizations.some(o => o.parent_organization_id === org.id);
    };
    
    const requestDeleteConfirmation = (org: Organization) => {
      organizationToDelete.value = org;
      deleteError.value = null;
      showDeleteConfirm.value = true;
    };

    const cancelDelete = () => {
      showDeleteConfirm.value = false;
      organizationToDelete.value = null;
      deleteError.value = null;
    };

    const executeDelete = async () => {
      if (!organizationToDelete.value) return;
      
      isDeleting.value = true;
      deleteError.value = null;
      
      try {
        await organizationsApi.deleteOrganization(organizationToDelete.value.id);
        emit('organizations-updated');
        showDeleteConfirm.value = false;
        organizationToDelete.value = null;
      } catch (err: any) {
        console.error('Error deleting organization:', err);
        deleteError.value = err.response?.data?.detail || err.message || 'Failed to delete organization';
      } finally {
        isDeleting.value = false;
      }
    };

    const goToOrganizationDetail = (organizationId: number) => {
      // Assuming a route named 'OrganizationDetail' exists or will be created
      router.push({ 
        name: 'OrganizationDetail', 
        params: { organizationId: organizationId },
      });
    };

    return {
      showDeleteConfirm,
      organizationToDelete,
      isDeleting,
      deleteError,
      isChildOrganization,
      getParentName,
      hasChildren,
      formatDateTime, // Use the imported formatter
      requestDeleteConfirmation,
      cancelDelete,
      executeDelete,
      goToOrganizationDetail,
    };
  },
});
</script>

<style scoped>
/* Reuse or adapt styles from WorldLocationList.vue */
.organization-list-section {
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

.organization-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.organization-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s ease;
}

.organization-item:hover {
  background-color: #f8f9fa;
}

.organization-item:last-child {
  border-bottom: none;
}

.organization-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 1rem;
}

.organization-name-link {
    cursor: pointer;
    color: var(--primary-color, #007bff); /* Use primary color variable */
    text-decoration: none;
    font-weight: 600;
}

.organization-name-link:hover {
    text-decoration: underline;
}

.organization-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.organization-details {
  font-size: 0.9rem;
  color: #555;
}

.organization-description {
  display: block;
  margin-bottom: 0.25rem;
  color: #6c757d;
}

.parent-info {
  display: block;
  font-style: italic;
  color: #888;
  margin-bottom: 0.25rem;
}

.organization-date {
  display: block;
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.5rem;
}

.organization-actions {
  display: flex;
  flex-direction: column; /* Stack buttons vertically */
  align-items: flex-end;
  gap: 0.5rem; /* Add space between buttons */
}

.btn-small {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
  /* Inherit general button styles */
}

.btn-secondary {
  /* Define secondary button styles */
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger {
  /* Define danger button styles */
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger:hover {
  background-color: #c82333;
}

.loading-state,
.empty-state,
.error-message {
  padding: 1rem;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.error-message {
  color: #dc3545; /* Danger color for errors */
  background-color: #f8d7da;
  border-color: #f5c6cb;
}

.warning-text {
  color: #ffc107; /* Warning color */
  font-weight: bold;
  margin-top: 0.5rem;
}
</style> 