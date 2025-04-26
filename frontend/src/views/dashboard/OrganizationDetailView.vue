<template>
  <div class="organization-detail-view">
    <div v-if="loading" class="loading-message">Loading organization details...</div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <router-link v-if="worldId" :to="{ name: 'dashboard-world-detail', params: { worldId: worldId } }" class="btn btn-secondary">Back to World</router-link>
      <router-link v-else :to="{ name: 'dashboard-worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>
    <div v-else-if="organization" class="organization-content">
      <header class="view-header">
        <h1>{{ organization.name }}</h1>
        <div>
          <button 
             v-if="canManageWorld"
             @click="showTagManagerModal = true"
             class="btn btn-outline-secondary btn-sm mr-2"
             title="Manage Tag Types for this World"
           >
            Manage Tag Types
          </button>
          <router-link :to="{ name: 'dashboard-world-detail', params: { worldId: organization.world_id } }" class="btn btn-secondary">
            Back to World
          </router-link>
        </div>
      </header>

      <div class="details-section">
        <h2>Details</h2>
        <div class="description-section">
          <div class="description-header">
            <strong>Description:</strong>
            <v-btn 
              v-if="!isEditingDescription && canManageWorld" 
              icon="mdi-pencil" 
              variant="text" 
              size="x-small" 
              @click="startEditingDescription"
              class="ml-2"
              title="Edit Description"
            ></v-btn>
          </div>
          
          <div v-if="!isEditingDescription" class="description-content mt-2" v-html="renderedDescription"></div>
          
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
        <p v-if="parentOrganization" class="mt-4"><strong>Parent Organization:</strong> 
          <router-link :to="{ name: 'OrganizationDetail', params: { organizationId: organization.parent_organization_id } }">
            {{ parentOrganization.name }}
           </router-link>
        </p>
        <p v-else-if="organization.parent_organization_id"><strong>Parent Organization:</strong> ID {{ organization.parent_organization_id }} (Not loaded)</p>
        <p><strong>Created:</strong> {{ formatDateTime(organization.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDateTime(organization.updated_at) }}</p>
      </div>
      
      <!-- Tag Assignment Section -->
      <div class="related-section tags-section">
         <OrganizationTagAssignment 
           v-if="!tagTypesLoading && organization && organization.tags"
           :organizationId="organization.id"
           :assignedTags="organization.tags || []" 
           :availableTagTypes="availableTagTypes"
           :canManage="canManageWorld" 
           @tags-updated="refreshOrganizationDetails" 
         />
         <div v-if="tagTypesLoading">Loading available tags...</div>
         <div v-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
      </div>
      
      <!-- Placeholder for child organizations, tags, members, etc. -->
      <div class="related-section">
        <h3>Child Organizations</h3>
        <p>...</p> 
      </div>
      <div class="related-section">
        <h3>Tags</h3>
        <p>...</p> 
      </div>
       <div class="related-section">
        <h3>Members</h3>
        <p>...</p> 
      </div>

    </div>
    <div v-else>
       <p>Organization not found.</p>
       <router-link :to="{ name: 'dashboard-worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>

    <!-- Tag Type Manager Modal -->
     <div v-if="showTagManagerModal && organization" class="modal-overlay" @click.self="showTagManagerModal = false">
        <div class="modal-content tag-manager-modal">
           <button @click="showTagManagerModal = false" class="close-modal-btn" title="Close">&times;</button>
           <OrganizationTagTypeManager
             :worldId="organization.world_id" 
             :initialTagTypes="availableTagTypes"
             :loading="tagTypesLoading"
             :error="tagTypesError"
             @tag-types-updated="handleTagTypesUpdated"
           />
        </div>
      </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue';
import * as organizationsApi from '@/services/api/organizations';
import * as organizationTagTypeApi from '@/services/api/organizationTagTypeService';
import type { Organization, OrganizationUpdate } from '@/types/organization';
import type { OrganizationTagType } from '@/types/organizationTagType';
import { formatDateTime } from '@/utils/dateFormatter';
import OrganizationTagAssignment from '@/components/organization/OrganizationTagAssignment.vue';
import OrganizationTagTypeManager from '@/components/organization/OrganizationTagTypeManager.vue';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';
import MarkdownIt from 'markdown-it';
import { useAuthStore } from '@/store/auth.store';

export default defineComponent({
  name: 'OrganizationDetailView',
  components: {
      OrganizationTagAssignment,
      OrganizationTagTypeManager,
      MarkdownEditor
  },
  props: {
    organizationId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const authStore = useAuthStore();
    const organization = ref<Organization | null>(null);
    const parentOrganization = ref<Organization | null>(null);
    const availableTagTypes = ref<OrganizationTagType[]>([]);
    const loading = ref(true);
    const error = ref<string | undefined>(undefined);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | undefined>(undefined);
    const worldId = ref<number | null>(null);
    const showTagManagerModal = ref(false);

    const isEditingDescription = ref(false);
    const editableDescription = ref('');
    const isSavingDescription = ref(false);
    const saveDescriptionError = ref<string | null>(null);

    const canManageWorld = computed(() => {
        if (!worldId.value || !authStore.user) return false;
        return authStore.isLoggedIn;
    });

    const md = new MarkdownIt({
      html: false, 
      linkify: true,
      typographer: true,
    });

    const renderedDescription = computed(() => {
      if (organization.value?.description) {
        return md.render(organization.value.description);
      }
      return '<p><em>No description provided.</em></p>';
    });

    const isDescriptionChanged = computed(() => {
      const currentDesc = organization.value?.description ?? '';
      const editedDesc = editableDescription.value.trim() === '' ? '' : editableDescription.value;
      return currentDesc !== editedDesc;
    });

    const fetchAvailableTagTypes = async (currentWorldId: number) => {
        tagTypesLoading.value = true;
        tagTypesError.value = undefined;
        availableTagTypes.value = [];
        try {
            availableTagTypes.value = await organizationTagTypeApi.getOrganizationTagTypes(currentWorldId);
        } catch (tagErr: any) {
            console.error("Fetch Org Tag Types Error:", tagErr);
            tagTypesError.value = `Failed to load available tag types: ${tagErr.response?.data?.detail || tagErr.message || 'Unknown error'}`;
        } finally {
            tagTypesLoading.value = false;
        }
    };

    const fetchOrganizationDetails = async (id: number) => {
      loading.value = true;
      error.value = undefined;
      organization.value = null;
      parentOrganization.value = null;
      availableTagTypes.value = [];
      tagTypesError.value = undefined;
      tagTypesLoading.value = false;
      worldId.value = null;

      try {
        organization.value = await organizationsApi.getOrganizationById(id);
        worldId.value = organization.value.world_id;

        if (organization.value.parent_organization_id) {
          try {
            parentOrganization.value = await organizationsApi.getOrganizationById(organization.value.parent_organization_id);
          } catch (parentErr: any) {
            console.warn(`Could not load parent organization (ID: ${organization.value.parent_organization_id}):`, parentErr);
          }
        }

        if (worldId.value) {
            await fetchAvailableTagTypes(worldId.value);
        } else {
             tagTypesError.value = "Could not determine world ID to fetch tag types.";
        }

      } catch (err: any) {
        console.error("Fetch Organization Error:", err);
        if (err.response?.status === 404) {
          error.value = 'Organization not found.';
        } else if (err.response?.status === 403) {
          error.value = 'You do not have permission to view this organization.';
        } else {
          error.value = `Failed to load organization: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
        availableTagTypes.value = [];
        tagTypesError.value = undefined;
      } finally {
        loading.value = false;
      }
    };

    const refreshOrganizationDetails = () => {
        if (props.organizationId) {
            fetchOrganizationDetails(Number(props.organizationId));
        }
    };

    const handleTagTypesUpdated = () => {
        if (worldId.value) {
            fetchAvailableTagTypes(worldId.value);
        }
    };

    const startEditingDescription = () => {
      if (!organization.value) return;
      editableDescription.value = organization.value.description ?? '';
      saveDescriptionError.value = null;
      isEditingDescription.value = true;
    };

    const cancelDescriptionEdit = () => {
      isEditingDescription.value = false;
      saveDescriptionError.value = null;
    };

    const saveDescription = async () => {
      if (!organization.value || !isDescriptionChanged.value) return;

      isSavingDescription.value = true;
      saveDescriptionError.value = null;
      const newDescription = editableDescription.value.trim() === '' ? null : editableDescription.value;
      
      try {
        const updatePayload: OrganizationUpdate = { 
          description: newDescription
        };
        const updatedOrg = await organizationsApi.updateOrganization(Number(props.organizationId), updatePayload);
        
        organization.value = updatedOrg;
        isEditingDescription.value = false;
        
      } catch (err: any) {
        console.error("Error saving description:", err);
        saveDescriptionError.value = err.response?.data?.detail || err.message || 'Failed to save description.';
      } finally {
        isSavingDescription.value = false;
        }
    };

    watch(
      () => props.organizationId,
      (newId) => {
        if (newId) {
          fetchOrganizationDetails(Number(newId));
        }
      },
      { immediate: true }
    );

    return {
      organization,
      parentOrganization,
      availableTagTypes,
      loading,
      error,
      tagTypesLoading,
      tagTypesError,
      worldId,
      canManageWorld,
      showTagManagerModal,
      formatDateTime,
      refreshOrganizationDetails,
      handleTagTypesUpdated,
      renderedDescription,
      isEditingDescription,
      editableDescription,
      isSavingDescription,
      saveDescriptionError,
      startEditingDescription,
      cancelDescriptionEdit,
      saveDescription,
      isDescriptionChanged,
    };
  },
});
</script>

<style scoped>
.organization-detail-view {
  padding: 1rem;
}

.loading-message,
.error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 0.25rem;
}


.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.view-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.details-section,
.related-section {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.details-section h2,
.related-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.4rem;
  font-weight: 500;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.details-section p {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.details-section strong {
  color: #343a40;
}

/* Basic button styling (adjust as needed) */
.btn {
  display: inline-block;
  font-weight: 400;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  border: 1px solid transparent;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  text-decoration: none;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}

.btn-secondary:hover {
  color: #fff;
  background-color: #5a6268;
  border-color: #545b62;
}

.tags-section {
    border-top: 1px solid #eee;
    padding-top: 1.5rem;
    margin-top: 1.5rem;
}



.btn-outline-secondary {
    color: #6c757d;
    border-color: #6c757d;
}
.btn-outline-secondary:hover {
    color: #fff;
    background-color: #6c757d;
    border-color: #6c757d;
}
.mr-2 { margin-right: 0.5rem; }

/* Modal specific styles */
.modal-overlay {
  position: fixed; 
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0,0,0,0.6);
  display: flex; 
  justify-content: center; 
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white; 
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  width: 90%;
  max-width: 700px;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}
.close-modal-btn {
    position: absolute;
    top: 10px;
    right: 15px;
    background: none;
    border: none;
    font-size: 1.8rem;
    font-weight: bold;
    color: #aaa;
    cursor: pointer;
    line-height: 1;
}
.close-modal-btn:hover {
    color: #333;
}

/* Add styles similar to LocationDetailView */
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