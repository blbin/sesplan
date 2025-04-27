<template>
  <v-card flat>
    <v-card-text>
      <!-- Description Section -->
      <section class="detail-section mb-4">
        <h2>Description</h2>
        <div v-if="!isEditingDescription" class="description-display">
          <div 
            v-if="campaign && campaign.description"
            class="description-content mb-2" 
            v-html="renderedDescription"
          ></div>
          <div v-else-if="campaign" class="text-muted description-content mb-2">
            <em>No description provided. Click the pencil to add one.</em>
          </div>
          <div v-else-if="loading">Loading description...</div> <!-- Show loading state from props -->
          
          <v-btn 
            v-if="canEdit"
            icon="mdi-pencil" 
            variant="text" 
            size="small" 
            @click="startEditingDescription"
            title="Edit description"
            class="edit-button"
            :disabled="loading || isSavingDescription" 
          ></v-btn>
        </div>
        <div v-else class="description-edit">
          <MarkdownEditor
            v-model="editedDescription"
            class="mb-2"
            :label="'Campaign Description'" 
          />
          <div class="edit-actions">
            <v-btn 
              color="primary" 
              @click="saveDescription"
              :loading="isSavingDescription"
              size="small"
              :disabled="!campaign || editedDescription === (campaign.description || '')"
            >
              Save
            </v-btn>
            <v-btn 
              variant="text" 
              @click="cancelEditingDescription" 
              :disabled="isSavingDescription"
              size="small"
            >
              Cancel
            </v-btn>
          </div>
          <v-alert v-if="saveError" type="error" density="compact" class="mt-2">
            {{ saveError }}
          </v-alert>
        </div>
      </section>

      <v-divider class="my-4"></v-divider>

      <!-- Details Section -->
      <section class="detail-section">
        <h2>Details</h2>
        <ul v-if="campaign">
          <li><strong>World:</strong> {{ worldName }} <span v-if="loadingWorld">(Loading world name...)</span></li>
          <li><strong>Created:</strong> {{ formatDate(campaign.created_at) }}</li>
          <li><strong>Last Updated:</strong> {{ formatDate(campaign.updated_at) }}</li>
          <li><strong>Owner (GM):</strong> {{ ownerName }} <span v-if="loadingOwner">(Loading...)</span></li>
        </ul>
         <ul v-else-if="loading">
            <li>Loading details...</li>
         </ul>
         <ul v-else>
            <li>Could not load campaign details.</li>
         </ul>
      </section>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed, toRefs } from 'vue';
import type { Campaign } from '@/types/campaign';
import type { World } from '@/types/world';
import type { UserCampaignRead } from '@/types/user_campaign';
import MarkdownEditor from '@/components/common/MarkdownEditor.vue';
import { useCampaignDetailDescription } from '@/composables/useCampaignDetailDescription';
// Import Vuetify components used explicitly
import { VCard, VCardText, VBtn, VAlert, VDivider } from 'vuetify/components'; 

// Props from the parent view (passed down from useCampaignDetail)
const props = defineProps<{
  campaign: Campaign | null;
  world: World | null;
  owner: UserCampaignRead | null; // Pass the owner object directly
  loading: boolean;
  loadingWorld: boolean;
  loadingOwner: boolean; // Add a specific loading state for the owner
  canEdit: boolean | null; // Use the GM status to determine edit rights
}>();

// Make props reactive for use in computed properties and templates
const { campaign, world, owner, loading, loadingWorld, loadingOwner } = toRefs(props);

// Description Editing Logic (using the composable)
const {
  isEditingDescription,
  editedDescription,
  isSavingDescription,
  saveError,
  renderedDescription,
  startEditingDescription,
  cancelEditingDescription,
  saveDescription,
} = useCampaignDetailDescription(campaign, computed(() => props.canEdit)); // Wrap props.canEdit in computed()

// Computed properties for display
const worldName = computed(() => world.value?.name || 'N/A');
const ownerName = computed(() => owner.value?.user?.username || 'Unknown');

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return 'Invalid Date';
  }
};
</script>

<style scoped>
/* Scoped styles from CampaignDetailView related to description and details */
.detail-section h2 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #333; /* Use Vuetify theme colors if possible */
}

.detail-section ul {
  list-style: none;
  padding: 0;
}

.detail-section li {
  margin-bottom: 0.3rem;
}

.description-display {
  position: relative; 
  padding-bottom: 2.5rem; 
}

.description-content {
  line-height: 1.7;
}

.description-content :deep(p:last-child) {
  margin-bottom: 0; 
}

.description-content :deep(a) {
  color: var(--v-primary-base, #1976D2);
  text-decoration: none;
}
.description-content :deep(a:hover) {
  text-decoration: underline;
}

.edit-button {
  position: absolute;
  bottom: 0;
  right: 0;
  opacity: 0.7;
  transition: opacity 0.2s ease-in-out;
}

.description-display:hover .edit-button {
  opacity: 1;
}

.description-edit {
  margin-bottom: 1rem;
}

.edit-actions {
  display: flex;
  gap: 0.5rem; 
  margin-top: 0.5rem;
}

.text-muted {
  color: #6c757d; /* Use Vuetify muted color if available */
}

/* Ensure cards have appropriate styling */
/* Removed empty .v-card rule */
</style> 