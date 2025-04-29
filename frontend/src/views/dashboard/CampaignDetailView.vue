<template>
  <div class="campaign-detail-view">
    <!-- Use the new header component -->
    <CampaignDetailHeader 
      :campaign="campaign"
      :loading="loading"
      :error="error"
      :is-current-user-g-m="isCurrentUserGM"
      :is-editing-name="isEditingName" 
      v-model:edited-name="editedName" 
      :is-saving-name="isSavingName"
      @start-editing-name="startEditingName"
      @cancel-editing-name="cancelEditingName"
      @save-name="saveName"
    />

    <!-- Display content only when not loading initial data and no critical error -->
    <div v-if="!loading && campaign" class="campaign-content">

      <!-- Tabs for sections -->
      <v-tabs v-model="currentTab" background-color="transparent" color="primary" grow>
        <v-tab value="details">Details</v-tab>
        <v-tab value="session">Session</v-tab>
        <v-tab value="members">Members</v-tab>
        <v-tab value="invites">Invites</v-tab>
      </v-tabs>

      <v-window v-model="currentTab" class="mt-5">
        <!-- Details Tab - Use the new component -->
        <v-window-item value="details" eager>
          <CampaignDetailsTab
            :campaign="campaign"
            :world="world"
            :owner="owner" 
            :loading="loading" 
            :loading-world="loadingWorld"
            :loading-owner="membersLoading"  
            :can-edit="isCurrentUserGM" 
          />
        </v-window-item>

        <!-- Session Tab Content -->
        <v-window-item value="session" eager>
           <v-card flat>
             <v-card-text>
                <CampaignSessionManager
                  v-if="campaignId !== null && isCurrentUserGM !== null"
                  :campaign-id="campaignId"
                  :is-current-user-g-m="isCurrentUserGM"
                />
                <!-- Loading/Info state for Session Manager -->
                <div v-else-if="membersLoading" class="text-center pa-4">
                    <v-progress-circular indeterminate color="primary" size="small"></v-progress-circular>
                    <p class="mt-2 text-caption">Loading session permissions...</p>
                </div>
                <v-alert v-else type="info" border="start" density="compact">
                   Session management requires membership data.
                </v-alert>
             </v-card-text>
           </v-card>
        </v-window-item>

        <!-- Members Tab Content -->
        <v-window-item value="members" eager>
          <v-card flat>
             <v-card-text>
              <CampaignMemberList
                v-if="campaignId !== null && currentUserId !== undefined"
                :members="members" 
                :campaignId="campaignId"
                :canManage="isCurrentUserGM" 
                :currentUserId="currentUserId" 
                :loading="membersLoading" 
                :error="membersError" 
                @members-updated="handleMembersUpdated" 
              />
             </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Invites Tab Content -->
        <v-window-item value="invites" eager>
           <v-card flat>
             <v-card-text>
              <template v-if="membersLoading"> <!-- Check general member loading -->
                <p class="text-center text-caption">Loading invite permissions...</p>
              </template>
              <template v-else-if="isCurrentUserGM"> 
                 <div class="d-flex justify-space-between align-center mb-4">
                   <h2>Pending Invites</h2>
                   <v-btn @click="openInviteModal" color="primary" small :disabled="invitesLoading">Invite User</v-btn>
                 </div>
                <CampaignInviteList
                  v-if="campaignId !== null"
                  :invites="invites" 
                  :campaignId="campaignId"
                  :canManage="isCurrentUserGM" 
                  :loading="invitesLoading"
                  :error="invitesError" 
                  @invites-updated="handleInvitesUpdated" 
                />
                <div v-if="!invitesLoading && !invitesError && invites.length === 0" class="mt-3 text-caption">
                  No pending invites.
                </div>
              </template>
              <template v-else>
                <v-alert type="info" border="start" density="compact">
                  Only the Game Master (GM) can manage invites.
                </v-alert>
              </template>
             </v-card-text>
           </v-card>
        </v-window-item>

      </v-window>

    </div>
    <!-- Optional: Show a specific message if campaign is null after loading without error -->
    <div v-else-if="!loading && !error && !campaign" class="not-found pa-5 text-center">
      <v-alert type="warning" border="start">
        Campaign not found or could not be loaded.
      </v-alert>
       <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary mt-4">
        &larr; Back to Campaigns
      </router-link>
    </div>
    <!-- Loading and Error states are handled by CampaignDetailHeader -->

    <!-- Invite Modal -->
    <v-dialog v-model="showInviteModal" max-width="500px">
       <v-card>
         <v-card-title>
           <span class="text-h5">Invite User to Campaign</span>
           <v-spacer></v-spacer>
            <v-btn icon="mdi-close" variant="text" @click="closeInviteModal"></v-btn>
         </v-card-title>
         <v-card-text>
            <CreateCampaignInviteForm
              v-if="campaignId !== null" 
              :campaignId="campaignId"
              @invite-sent="handleInviteSent"
              @cancel="closeInviteModal"
            />
         </v-card-text>
       </v-card>
     </v-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, provide } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth.store';
import * as campaignInvitesApi from '@/services/api/campaignInvites';
import type { CampaignInvite } from '@/types/campaign_invite';

// Import Composables
import { useCampaignDetail } from '@/composables/useCampaignDetail';

// Import Components
import CampaignDetailHeader from '@/components/campaign/CampaignDetailHeader.vue';
import CampaignDetailsTab from '@/components/campaign/CampaignDetailsTab.vue';
import CampaignMemberList from '@/components/campaign/CampaignMemberList.vue';
import CampaignInviteList from '@/components/campaign/CampaignInviteList.vue';
import CreateCampaignInviteForm from '@/components/campaign/CreateCampaignInviteForm.vue';
import CampaignSessionManager from '@/components/campaign/CampaignSessionManager.vue';

// Import Vuetify components explicitly used in this template
import {
  VTabs, VTab, VWindow, VWindowItem, VCard, VCardText, VDialog, VCardTitle,
  VSpacer, VBtn, VAlert, VProgressCircular 
} from 'vuetify/components';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// --- Campaign ID from Route --- 
const campaignId = computed<number | null>(() => {
  const id = Number(route.params.campaignId);
  return isNaN(id) ? null : id;
});

// --- Core Campaign Data via Composable --- 
const {
  campaign,
  world,
  members,
  loading, // Main loading state
  error,   // Main error state
  loadingWorld,
  membersLoading,
  membersError,
  isCurrentUserGM,
  owner,
  reloadMembers, // Function to reload members
  // Name Editing State & Functions
  isEditingName,
  editedName, 
  isSavingName,
  startEditingName,
  cancelEditingName,
  saveName
} = useCampaignDetail(campaignId);

const currentUserId = computed(() => authStore.user?.id);

// --- Tab Management --- 
const currentTab = ref('details');
const validTabs = ['details', 'session', 'members', 'invites'];

// Watch route query to set the tab
watch(
  () => route.query.tab,
  (newTab) => {
    if (typeof newTab === 'string' && validTabs.includes(newTab)) {
      if (currentTab.value !== newTab) {
        currentTab.value = newTab;
      }
    } else if (!newTab && currentTab.value !== 'details') {
       currentTab.value = 'details'; // Default to details if invalid/missing
    }
  },
  { immediate: true } 
);

// Watch currentTab state to update the URL query parameter
watch(currentTab, (newTabValue) => {
  if (route.query.tab !== newTabValue) {
    // Use replace to avoid adding history entries for tab changes
    router.replace({ query: { ...route.query, tab: newTabValue } }); 
  }
});

// --- Invites Data --- 
const invites = ref<CampaignInvite[]>([]);
const invitesLoading = ref(false);
const invitesError = ref<string | undefined>(undefined);

const loadInvites = async (id: number | null) => {
  // Only load invites if the user is GM and ID is valid
  if (id === null || isCurrentUserGM.value === null) { // Also wait for GM status
    console.log('Skipping invite load: Invalid ID or GM status unknown');
    invites.value = [];
    invitesLoading.value = false;
    return;
  }
  // If not GM, clear invites and don't load
  if (isCurrentUserGM.value === false) {
      invites.value = [];
      invitesLoading.value = false;
      return;
  }
  
  invitesLoading.value = true;
  invitesError.value = undefined;
  invites.value = []; 
  try {
    invites.value = await campaignInvitesApi.getCampaignInvites(id);
  } catch (err: any) {
    if (err.response?.status === 403) {
         invitesError.value = 'You do not have permission to view invites.';
    } else {
        invitesError.value = `Failed to load invites: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    }
    console.error("Load Invites Error:", err);
  } finally {
    invitesLoading.value = false;
  }
};

// Watch for GM status to become available AND campaignId to load invites
watch([isCurrentUserGM, campaignId], ([isGM, id]) => {
    if (isGM === true && id !== null) {
        loadInvites(id);
    } else {
        // Reset invites if user is not GM or ID is invalid
        invites.value = [];
        invitesLoading.value = false;
        invitesError.value = undefined;
    }
}, { immediate: true }); // Check immediately on component setup

// --- Invite Modal --- 
const showInviteModal = ref(false);
const openInviteModal = () => { showInviteModal.value = true; };
const closeInviteModal = () => { showInviteModal.value = false; };

// --- Event Handlers --- 

// Called when CampaignMemberList emits 'members-updated'
const handleMembersUpdated = () => {
  console.log('Members updated, reloading via composable...');
  reloadMembers(); // Use the reload function from the composable
  // No need to reload invites here, the watcher on isCurrentUserGM handles it
};

// Called when CampaignInviteList emits 'invites-updated'
const handleInvitesUpdated = () => {
  console.log('Invites updated, reloading...');
  if (isCurrentUserGM.value && campaignId.value !== null) {
     loadInvites(campaignId.value);
  }
};

// Called when CreateCampaignInviteForm emits 'invite-sent'
const handleInviteSent = () => {
  closeInviteModal();
  if (isCurrentUserGM.value && campaignId.value !== null) {
     loadInvites(campaignId.value); // Reload invites after sending
  }
};

// --- Provide campaignId and GM status for deeper children if needed ---
provide('campaignId', campaignId); 
provide('isCurrentUserGM', isCurrentUserGM); 

</script>

<style scoped>
/* Reuse styles from the original component */
.campaign-detail-view {
  max-width: 1200px; 
  margin: 0 auto;
  padding: 1rem;
}

.not-found {
  text-align: center;
}

/* Copied from original */
.loading-state,
.error-message {
  text-align: center;
  padding: 2rem;
}

.v-tabs {
    border-bottom: 1px solid #e0e0e0;
}

.v-window-item {
    padding-top: 1rem; 
}

.btn {
    text-decoration: none; 
}

.btn-secondary {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  cursor: pointer;
  border: none;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  transition: background-color 0.2s ease;
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

</style> 