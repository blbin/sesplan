<template>
  <section class="organization-list-section detail-section">
    <div v-if="loading" class="loading-state">Loading organizations...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="organizations.length > 0">
      <ul class="entity-list">
        <li v-for="organization in organizations" :key="organization.id" class="entity-list-item">
          <div class="entity-info">
            <router-link :to="{ name: 'OrganizationDetail', params: { organizationId: organization.id } }" class="entity-name-link">
              <span class="entity-name">{{ organization.name }}</span>
            </router-link>
            <div class="entity-details">
              <div 
                v-if="organization.description"
                class="entity-description-preview" 
                v-html="renderDescriptionPreview(organization.description)"
              ></div>
              <span v-else class="entity-description-preview text-muted"><em>No description</em></span>
              <span v-if="isChildOrganization(organization)" class="parent-info">
                Parent: {{ getParentName(organization) }}
              </span>
              <!-- Add tag display here if needed later -->
              <span class="entity-date">Created: {{ formatDateTime(organization.created_at) }}</span>
            </div>
          </div>
          <div class="entity-actions">
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
import type { Organization } from '@/types/organization';
import * as organizationsApi from '@/services/api/organizations';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';
import { formatDateTime } from '@/utils/dateFormatter'; // Assuming a utility function for date formatting
import MarkdownIt from 'markdown-it'; // Import markdown-it

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
    const showDeleteConfirm = ref(false);
    const organizationToDelete = ref<Organization | null>(null);
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
      renderDescriptionPreview, // Expose the method
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

.entity-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.entity-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.2s ease;
}

.entity-list-item:hover {
  background-color: #f8f9fa;
}

.entity-list-item:last-child {
  border-bottom: none;
}

.entity-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  margin-right: 1rem;
}

.entity-name-link {
    cursor: pointer;
    color: var(--primary-color, #007bff); /* Use primary color variable */
    text-decoration: none;
    font-weight: 600;
}

.entity-name-link:hover {
    text-decoration: underline;
}

.entity-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.entity-details {
  font-size: 0.9rem;
  color: #555;
}

.entity-description-preview {
  font-size: 0.9em;
  color: #6c757d; 
  margin-top: 0.25rem;
  line-height: 1.4;
}

.entity-description-preview :deep(p) {
    margin: 0;
    display: inline;
}
.entity-description-preview :deep(a) {
    color: var(--v-theme-primary);
}

.text-muted {
  color: #6c757d;
    font-style: italic;
}

.parent-info {
  display: block;
  font-style: italic;
  color: #888;
  margin-bottom: 0.25rem;
}

.entity-date {
  display: block;
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.5rem;
}

.entity-actions {
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