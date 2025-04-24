<template>
  <div class="campaign-detail-view">
    <div v-if="loading" class="loading-state">Loading campaign details...</div>
    <div v-else-if="error" class="error-message">
      Error loading campaign: {{ error }}
    </div>
    <div v-else-if="campaign" class="campaign-content">
      <header class="view-header">
        <h1>{{ campaign.name }}</h1>
        <!-- Tlačítko Zpět (volitelné) -->
        <router-link :to="{ name: 'Campaigns' }" class="btn btn-secondary">
          &larr; Back to Campaigns
        </router-link>
      </header>

      <div class="campaign-details">
        <section class="detail-section">
          <h2>Description</h2>
          <p>{{ campaign.description || 'No description provided.' }}</p>
        </section>

        <section class="detail-section">
          <h2>Details</h2>
          <ul>
            <li><strong>World:</strong> {{ worldName }}</li>
            <li><strong>Created:</strong> {{ formatDate(campaign.created_at) }}</li>
            <li><strong>Last Updated:</strong> {{ formatDate(campaign.updated_at) }}</li>
          </ul>
        </section>

        <!-- Správa členů a pozvánek -->
        <div v-if="!loading && campaign && currentUserId" class="management-section">
          <CampaignMemberList
            :members="members"
            :campaignId="campaign.id"
            :canManage="isCurrentUserGM"
            :currentUserId="currentUserId"
            :loading="membersLoading"
            :error="membersError"
            @members-updated="handleMembersUpdated"
          />

          <template v-if="isCurrentUserGM">
            <!-- Tlačítko pro otevření modálu -->
            <div class="section-header">
              <h2>Invites</h2>
              <button @click="openInviteModal" class="btn btn-primary btn-sm">Invite User</button>
            </div>
            <CampaignInviteList
              :invites="invites"
              :campaignId="campaign.id"
              :canManage="isCurrentUserGM"
              :loading="invitesLoading"
              :error="invitesError"
              @invites-updated="handleInvitesUpdated"
            />
          </template>
          <div v-else-if="membersLoading && !membersError">
            <!-- Placeholder or indicator if needed -->
          </div>
        </div>

        <!-- Sessions Section - Replaced with component -->
        <CampaignSessionManager
          v-if="campaign && isCurrentUserGM !== null" 
          :campaign-id="campaign.id"
          :is-current-user-g-m="isCurrentUserGM"
        />

      </div>
    </div>
    <div v-else class="not-found">
      Campaign not found.
    </div>

    <!-- Invite Modal Remains Here (or could be refactored later) -->
    <div v-if="showInviteModal" class="modal-backdrop">
      <div class="modal">
        <h2>Invite User to Campaign</h2>
        <CreateCampaignInviteForm
          v-if="campaign"
          :campaignId="campaign.id"
          @invite-sent="handleInviteSent"
          @cancel="closeInviteModal"
        />
        <div class="modal-actions" v-if="!campaign">
          <button type="button" @click="closeInviteModal" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
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

export default defineComponent({
  name: 'CampaignDetailView',
  components: {
    CampaignMemberList,
    CampaignInviteList,
    CreateCampaignInviteForm,
    CampaignSessionManager,
  },
  props: {
    campaignId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const campaign = ref<Campaign | null>(null);
    const world = ref<World | null>(null);
    const loading = ref(true);
    const error = ref<string | null>(null);
    const loadingWorld = ref(false);

    const authStore = useAuthStore();
    const currentUserId = computed(() => authStore.user?.id);

    const members = ref<UserCampaignRead[]>([]);
    const membersLoading = ref(false);
    const membersError = ref<string | undefined>(undefined);

    const invites = ref<CampaignInvite[]>([]);
    const invitesLoading = ref(false);
    const invitesError = ref<string | undefined>(undefined);

    // Computed property for the current user's full membership object
    const currentUserMembership = computed(() => {
      if (!currentUserId.value || !members.value) return null;
      return members.value.find(m => m.user_id === currentUserId.value) || null;
    });

    // Use currentUserMembership in isCurrentUserGM
    const isCurrentUserGM = computed(() => {
      // Make sure members are loaded before determining GM status
      if (membersLoading.value) return null; // Or some indeterminate state
      return currentUserMembership.value?.role === CampaignRoleEnum.GM;
    });

    const loadMembers = async (id: number) => {
      if (!id) return;
      membersLoading.value = true;
      membersError.value = undefined;
      members.value = [];
      try {
        members.value = await campaignMembersApi.getCampaignMembers(id);
      } catch (err: any) {
        membersError.value = `Failed to load members: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Load Members Error:", err);
      } finally {
        membersLoading.value = false;
      }
    };

    const loadInvites = async (id: number) => {
      if (!id) return;
      invitesLoading.value = true;
      invitesError.value = undefined;
      invites.value = [];
      try {
        invites.value = await campaignInvitesApi.getCampaignInvites(id);
      } catch (err: any) {
        invitesError.value = `Failed to load invites: ${err.response?.data?.detail || err.message || 'Forbidden?'}`;
        console.warn("Load Invites Error:", err);
      } finally {
        invitesLoading.value = false;
      }
    };

    const loadWorldDetail = async (worldId: number) => {
      loadingWorld.value = true;
      try {
        world.value = await worldsApi.getWorldById(worldId);
      } catch (err: any) {
        console.error("Load World Detail Error:", err);
      } finally {
        loadingWorld.value = false;
      }
    };

    // Simple formatDate remains if needed elsewhere, or import from utils
    const formatDate = (dateString: string | null | undefined) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString();
        } catch (e) {
            return String(dateString); // Fallback
        }
    };

    const worldName = computed(() => {
      if (loadingWorld.value) return 'Loading world...';
      return world.value ? world.value.name : `ID: ${campaign.value?.world_id}`;
    });

    const loadCampaignDetail = async (id: number) => {
      loading.value = true;
      error.value = null;
      campaign.value = null;
      world.value = null;
      loadingWorld.value = false;
      members.value = [];
      invites.value = [];
      membersLoading.value = false;
      membersError.value = undefined;
      invitesLoading.value = false;
      invitesError.value = undefined;

      try {
        campaign.value = await campaignsApi.getCampaignById(id);
        if (campaign.value) {
          // Load members first to determine GM status
          await loadMembers(campaign.value.id);
          // Now we know GM status, can load invites if GM (handled by watcher)
          await loadWorldDetail(campaign.value.world_id);
          // Sessions are loaded by CampaignSessionManager component itself
        }
      } catch (err: any) {
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load campaign details.');
        console.error("Load Campaign Detail Error:", err);
      } finally {
        loading.value = false;
      }
    };

    // --- State for Invite Modal ---
    const showInviteModal = ref(false);

    // --- Invite Modal Logic ---
    const openInviteModal = () => {
      showInviteModal.value = true;
    };

    const closeInviteModal = () => {
      showInviteModal.value = false;
    };

    const handleInviteSent = () => {
      closeInviteModal();
      handleInvitesUpdated();
    };

    // --- Watchers and event handlers ---
    watch(isCurrentUserGM, (isGM) => {
      // Load invites only if GM and campaign is loaded
      if (isGM === true && campaign.value && !invitesLoading.value) {
          loadInvites(campaign.value.id);
      }
       // Reset invites if user is no longer GM or becomes indeterminate
       else if (isGM === false || isGM === null) {
           invites.value = [];
           invitesError.value = undefined;
           invitesLoading.value = false;
       }
    });

    watch(
      () => props.campaignId,
      (newId) => {
        if (newId) {
          loadCampaignDetail(Number(newId));
        } else {
            // Reset state if campaignId becomes invalid
            campaign.value = null;
            world.value = null;
            members.value = [];
            invites.value = [];
            error.value = "Invalid campaign ID provided.";
            loading.value = false;
        }
      },
      { immediate: true }
    );

    const handleMembersUpdated = () => {
      // Re-load members (e.g., after role change or kick)
      if (campaign.value) loadMembers(campaign.value.id);
    };
    const handleInvitesUpdated = () => {
      // Re-load invites if user is GM
      if (campaign.value && isCurrentUserGM.value) loadInvites(campaign.value.id);
    };

    return {
      campaign,
      loading,
      error,
      worldName,
      formatDate,
      members,
      membersLoading,
      membersError,
      invites,
      invitesLoading,
      invitesError,
      isCurrentUserGM,
      currentUserId,
      handleMembersUpdated,
      handleInvitesUpdated,

      // --- Invite Modal properties/methods ---
      showInviteModal,
      openInviteModal,
      closeInviteModal,
      handleInviteSent,
    };
  },
});
</script>

<style scoped>
.campaign-detail-view {
  padding: 2rem;
}

.campaign-content {
  background-color: #fff;
  padding: 1.5rem 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.view-header h1 {
  margin: 0;
  color: #343a40;
}

.detail-section {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.detail-section:last-of-type {
   margin-bottom: 0;
   padding-bottom: 0;
   border-bottom: none;
}

.detail-section h2 {
  font-size: 1.2rem;
  color: #495057;
  margin-bottom: 0.75rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #e9ecef;
}

.detail-section p,
.detail-section ul {
  font-size: 0.95rem;
  color: #6c757d;
  line-height: 1.6;
}

.detail-section ul {
  list-style: none;
  padding: 0;
}
.detail-section li {
  margin-bottom: 0.5rem;
}
.detail-section li strong {
  color: #495057;
  margin-right: 0.5rem;
}

.loading-state,
.not-found {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.management-section {
    border-bottom: 1px solid #eee;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
   margin: 0;
   font-size: 1.2rem;
   color: #495057;
   padding-bottom: 0.25rem;
   border-bottom: 1px solid #e9ecef;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 2rem 2.5rem;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  color: #333;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn { padding: 0.6rem 1.2rem; border-radius: 0.3rem; cursor: pointer; border: none; font-weight: 500; text-decoration: none; transition: background-color 0.2s ease, box-shadow 0.2s ease; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; line-height: 1; }
.btn:disabled { opacity: 0.65; cursor: not-allowed; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:not(:disabled):hover { background-color: #0056b3; }
.btn-primary:focus { box-shadow: 0 0 0 0.2rem rgba(38,143,255,.5); outline: none; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:not(:disabled):hover { background-color: #5a6268; }
.btn-secondary:focus { box-shadow: 0 0 0 0.2rem rgba(130,138,145,.5); outline: none; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; border-radius: 0.2rem; }
</style> 