<template>
  <div class="campaign-detail-view">
    <!-- Header - Remains similar, potentially extracted to a component later -->
    <header v-if="campaign && !loading && !error" class="view-header mb-4 d-flex justify-space-between align-center">
      <h1>{{ campaign.name }}</h1>
      <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary">
        &larr; Back to Campaigns
      </router-link>
    </header>

    <div v-if="loading" class="loading-state d-flex justify-center align-center flex-column pa-5">
       <v-progress-circular indeterminate color="primary"></v-progress-circular>
       <p class="mt-4">Loading campaign details...</p>
    </div>
    <div v-else-if="error" class="error-message pa-5">
      <v-alert type="error" prominent border="start">
        Error loading campaign: {{ error }}
      </v-alert>
      <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary mt-4">
        &larr; Back to Campaigns
      </router-link>
    </div>
    <div v-else-if="campaign" class="campaign-content">

      <!-- Tabs for sections -->
      <v-tabs v-model="currentTab" background-color="transparent" color="primary" grow>
        <v-tab value="details">Details</v-tab>
        <v-tab value="session">Session</v-tab>
        <v-tab value="members">Members</v-tab>
        <v-tab value="invites">Invites</v-tab>
      </v-tabs>

      <v-window v-model="currentTab" class="mt-5">
        <!-- Details Tab Content -->
        <v-window-item value="details" eager>
          <v-card flat>
            <v-card-text>
              <section class="detail-section mb-4">
                <h2>Description</h2>
                <p>{{ campaign.description || 'No description provided.' }}</p>
              </section>
              <section class="detail-section">
                <h2>Details</h2>
                <ul>
                  <li><strong>World:</strong> {{ worldName }} <span v-if="loadingWorld">(Loading world name...)</span></li>
                  <li><strong>Created:</strong> {{ formatDate(campaign.created_at) }}</li>
                  <li><strong>Last Updated:</strong> {{ formatDate(campaign.updated_at) }}</li>
                  <li><strong>Owner (GM):</strong> {{ ownerName }} <span v-if="membersLoading">(Loading...)</span></li>
                </ul>
              </section>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Session Tab Content -->
        <v-window-item value="session" eager>
           <v-card flat>
             <v-card-text>
                <!-- Display loading/error specifically for sessions if needed -->
                <CampaignSessionManager
                  v-if="campaign && isCurrentUserGM !== null"
                  :campaign-id="campaign.id"
                  :is-current-user-g-m="isCurrentUserGM"
                />
                <div v-else-if="isCurrentUserGM === null && membersLoading">Loading session data...</div>
                <div v-else>
                    <v-alert type="info" border="start" dense>
                        Session management requires GM privileges or membership data to be loaded.
                    </v-alert>
                </div>
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
              <template v-if="isCurrentUserGM === null && membersLoading">
                <p>Loading invite permissions...</p>
              </template>
              <template v-else-if="isCurrentUserGM">
                 <div class="d-flex justify-space-between align-center mb-4">
                   <h2>Pending Invites</h2>
                   <v-btn @click="openInviteModal" color="primary" small>Invite User</v-btn>
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
                <div v-if="!invitesLoading && !invitesError && invites.length === 0" class="mt-3">
                  No pending invites.
                </div>
              </template>
              <template v-else>
                <v-alert type="info" border="start" dense>
                  Only the Game Master (GM) can manage invites.
                </v-alert>
              </template>
             </v-card-text>
           </v-card>
        </v-window-item>

      </v-window>

    </div>
    <div v-else class="not-found pa-5">
      <v-alert type="warning" border="start">
        Campaign not found.
      </v-alert>
       <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary mt-4">
        &larr; Back to Campaigns
      </router-link>
    </div>

    <!-- Invite Modal - Keep it outside the tabs for now -->
    <v-dialog v-model="showInviteModal" max-width="500px">
       <v-card>
         <v-card-title>
           <span class="text-h5">Invite User to Campaign</span>
           <v-spacer></v-spacer>
            <v-btn icon @click="closeInviteModal">
               <v-icon>mdi-close</v-icon>
            </v-btn>
         </v-card-title>
         <v-card-text>
            <CreateCampaignInviteForm
              v-if="campaign"
              :campaignId="campaign.id"
              @invite-sent="handleInviteSent"
              @cancel="closeInviteModal"
            />
         </v-card-text>
         <!-- Actions are usually within the form component now -->
       </v-card>
     </v-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, provide } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import * as campaignsApi from '@/services/api/campaigns';
import * as worldsApi from '@/services/api/worlds';
import * as campaignMembersApi from '@/services/api/campaignMembers';
import * as campaignInvitesApi from '@/services/api/campaignInvites';
import type { Campaign } from '@/types/campaign';
import type { World } from '@/types/world';
import { useAuthStore } from '@/store/auth.store';
import CampaignMemberList from '@/components/campaign/CampaignMemberList.vue';
import CampaignInviteList from '@/components/campaign/CampaignInviteList.vue';
import CreateCampaignInviteForm from '@/components/campaign/CreateCampaignInviteForm.vue';
import CampaignSessionManager from '@/components/campaign/CampaignSessionManager.vue';
import type { UserCampaignRead } from '@/types/user_campaign';
import type { CampaignInvite } from '@/types/campaign_invite';
import { CampaignRoleEnum } from '@/types/campaign_role';
// Vuetify components are typically globally registered or auto-imported in newer Vuetify setups
// If not, they would need to be imported here as well.
// import { VTabs, VTab, VWindow, ... } from 'vuetify/components';

// No props needed as ID comes from route
// defineProps<{}>(); // Use defineProps if props were needed

// All setup logic now at the top level
const route = useRoute();
const router = useRouter();
const campaignId = computed<number | null>(() => {
  const id = Number(route.params.campaignId);
  return isNaN(id) ? null : id; // Return null if NaN
});

const campaign = ref<Campaign | null>(null);
const world = ref<World | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const loadingWorld = ref(false);
const currentTab = ref('details');

const authStore = useAuthStore();
const currentUserId = computed(() => authStore.user?.id);

const members = ref<UserCampaignRead[]>([]);
const membersLoading = ref(true);
const membersError = ref<string | undefined>(undefined);

const invites = ref<CampaignInvite[]>([]);
const invitesLoading = ref(false);
const invitesError = ref<string | undefined>(undefined);

const showInviteModal = ref(false);

const currentUserMembership = computed(() => {
  if (!currentUserId.value || !members.value) return null;
  return members.value.find(m => m.user_id === currentUserId.value) || null;
});

const isCurrentUserGM = computed<boolean | null>(() => {
  if (membersLoading.value) return null;
  if (!currentUserMembership.value) return false;
  return currentUserMembership.value?.role === CampaignRoleEnum.GM;
});

const ownerName = computed(() => {
    if (membersLoading.value) return 'Loading...';
    const gm = members.value.find(m => m.role === CampaignRoleEnum.GM);
    return gm?.user?.username || 'Unknown';
});

// --- Data Fetching ---

const loadCampaignDetails = async (id: number | null) => {
  // Check if ID is valid before proceeding
  if (id === null) { // Use strict null check
      error.value = "Invalid Campaign ID provided.";
      loading.value = false;
      membersLoading.value = false;
      invitesLoading.value = false;
      campaign.value = null;
      members.value = [];
      invites.value = [];
      return;
  }

  loading.value = true;
  error.value = null;
  campaign.value = null;
  world.value = null;
  membersLoading.value = true;
  invitesLoading.value = false;
  members.value = [];
  invites.value = [];

  try {
    campaign.value = await campaignsApi.getCampaignById(id);
    console.log('Campaign Loaded:', campaign.value);

    if (campaign.value?.world_id) {
      await loadWorldDetail(campaign.value.world_id);
    }

    await loadMembers(id);

    if (isCurrentUserGM.value === true) {
         await loadInvites(id);
    }

  } catch (err: any) {
    console.error("Load Campaign Detail Error:", err);
    error.value = `Failed to load campaign: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    campaign.value = null;
  } finally {
    loading.value = false;
    if (membersLoading.value) membersLoading.value = false; // Ensure it becomes false
    // Ensure invites loading reflects reality
    if (invitesLoading.value && isCurrentUserGM.value !== true) invitesLoading.value = false;
  }
};

const loadWorldDetail = async (worldId: number) => {
  loadingWorld.value = true;
  try {
    world.value = await worldsApi.getWorldById(worldId);
    console.log('World Loaded:', world.value);
  } catch (err: any) {
    console.error("Load World Detail Error:", err);
  } finally {
    loadingWorld.value = false;
  }
};

const loadMembers = async (id: number | null) => {
   if (id === null) return; // Don't load if ID is invalid (null)
  membersLoading.value = true;
  membersError.value = undefined;
  members.value = [];
  try {
    members.value = await campaignMembersApi.getCampaignMembers(id);
    console.log('Members Loaded:', members.value);
  } catch (err: any) {
    membersError.value = `Failed to load members: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    console.error("Load Members Error:", err);
  } finally {
    membersLoading.value = false;
  }
};

const loadInvites = async (id: number | null) => {
   if (id === null || isCurrentUserGM.value !== true) { // Check for null ID
      console.log('Skipping invite load: Invalid ID or Not GM');
      invites.value = [];
      invitesLoading.value = false;
      return;
  }
  invitesLoading.value = true;
  invitesError.value = undefined;
  invites.value = [];
  try {
    invites.value = await campaignInvitesApi.getCampaignInvites(id);
    console.log('Invites Loaded:', invites.value);
  } catch (err: any) {
    if (err.response?.status === 403) {
         invitesError.value = 'You do not have permission to view invites.';
         console.warn("Load Invites Forbidden:", err);
    } else {
        invitesError.value = `Failed to load invites: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Load Invites Error:", err);
    }
  } finally {
    invitesLoading.value = false;
  }
};

// --- Event Handlers ---

const handleMembersUpdated = () => {
  console.log('Members updated, reloading...');
  if (campaignId.value !== null) { // Check for non-null ID
    loadMembers(campaignId.value);
  }
};

const handleInvitesUpdated = () => {
  console.log('Invites updated, reloading...');
  if (isCurrentUserGM.value && campaignId.value !== null) { // Check for non-null ID
     loadInvites(campaignId.value);
  }
};

const openInviteModal = () => {
  showInviteModal.value = true;
};

const closeInviteModal = () => {
  showInviteModal.value = false;
};

const handleInviteSent = () => {
  closeInviteModal();
  if (isCurrentUserGM.value && campaignId.value !== null) { // Check for non-null ID
     loadInvites(campaignId.value);
  }
};


// --- Computed Properties for Display ---

const worldName = computed(() => world.value?.name || 'N/A');

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return 'Invalid Date';
  }
};

// --- Lifecycle Hooks and Watchers ---

onMounted(() => {
  console.log('CampaignDetailView mounted, campaignId from route:', campaignId.value);
  loadCampaignDetails(campaignId.value);
});

watch(() => route.params.campaignId, (newIdRaw) => {
  console.log('Route campaignId changed:', newIdRaw);
  const newCampaignId = Number(newIdRaw);
  const currentId = campaignId.value;
  const potentialNewId = isNaN(newCampaignId) ? null : newCampaignId;

  if (potentialNewId !== currentId) {
    // Reset tab to details when navigating to a different campaign
    currentTab.value = 'details';
    // Ensure URL is updated if we reset the tab visually
    router.replace({ query: { ...route.query, tab: undefined } }); // Remove tab query param
    loadCampaignDetails(potentialNewId);
  }
});

// Watch route query to set the tab on initial load or direct navigation
watch(
  () => route.query.tab,
  (newTab) => {
    // Convert valid string tabs from query param, default to 'details'
    const validTabs = ['details', 'session', 'members', 'invites'];
    if (typeof newTab === 'string' && validTabs.includes(newTab)) {
      // Only update if the currentTab is different to avoid loop with the next watcher
      if (currentTab.value !== newTab) {
         currentTab.value = newTab;
      }
    } else if (!newTab && currentTab.value !== 'details') {
        // If tab query is removed or invalid, default to 'details'
        currentTab.value = 'details';
    }
    // If newTab is already the currentTab, do nothing
  },
  { immediate: true } // Run on component load
);

// Watch currentTab state to update the URL query parameter
watch(
  currentTab,
  (newTabValue) => {
    // Only update the route if the query parameter doesn't match the new tab value
    // Prevents unnecessary route updates and potential watcher loops
    if (route.query.tab !== newTabValue) {
      router.replace({ query: { ...route.query, tab: newTabValue } });
    }
  }
  // No immediate: true here, we only want to update URL on user interaction
);

// Provide campaignId and GM status for potential use in child components
provide('campaignId', campaignId);
provide('isCurrentUserGM', isCurrentUserGM);

// No return needed in <script setup>
</script>

<style scoped>
.campaign-detail-view {
  max-width: 1200px; /* Or your preferred max width */
  margin: 0 auto;
  padding: 1rem;
}

.view-header {
  /* Styles for the header section */
  /* Example: */
   /* margin-bottom: 1.5rem; */
   /* border-bottom: 1px solid #eee; */
   /* padding-bottom: 1rem; */
}

.loading-state, .error-message, .not-found {
  text-align: center;
  padding: 2rem;
}

.campaign-content {
  /* Styles for the main content area after loading */
}

.detail-section h2 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.detail-section ul {
  list-style: none;
  padding: 0;
}

.detail-section li {
  margin-bottom: 0.3rem;
}

/* Vuetify overrides or custom styles if needed */
.v-card {
    border: 1px solid #e0e0e0; /* Subtle border for cards */
}

.v-tabs {
    border-bottom: 1px solid #e0e0e0;
}

.v-window-item {
    padding-top: 1rem; /* Add some space above window content */
}

/* Ensure buttons have some margin if needed */
.btn {
    /* Add base button styling if not using Vuetify globally or need overrides */
    text-decoration: none; /* For router-links styled as buttons */
}

.btn-secondary {
    /* Specific styles for secondary button */
}

.btn-primary {
     /* Specific styles for primary button */
}

/* Style for the invite button positioning */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem; /* Adjust as needed */
}

/* Modal styles - Consider moving to a global style or dedicated component */
/* Basic modal styling using v-dialog is usually sufficient */

</style> 