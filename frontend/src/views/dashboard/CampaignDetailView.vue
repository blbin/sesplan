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
        <router-link to="/dashboard/campaigns" class="btn btn-secondary">
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
              <CreateCampaignInviteForm
                :campaignId="campaign.id"
                @invites-updated="handleInvitesUpdated"
              />

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
                <!-- Zobrazit jen pokud se načítají členové a není chyba -->
                <!-- Může být nahrazeno lepším indikátorem -->
            </div>

        </div>
      </div>
    </div>
    <div v-else class="not-found">
      Campaign not found.
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import * as campaignsApi from '@/services/api/campaigns';
import * as worldsApi from '@/services/api/worlds'; // Pro načtení jména světa
import type { Campaign } from '@/types/campaign';
import type { World } from '@/types/world';
import { useAuthStore } from '@/store/auth.store'; // Správný název souboru
import CampaignMemberList from '@/components/campaign/CampaignMemberList.vue';
import CampaignInviteList from '@/components/campaign/CampaignInviteList.vue';
import CreateCampaignInviteForm from '@/components/campaign/CreateCampaignInviteForm.vue';
import * as campaignMembersApi from '@/services/api/campaignMembers';
import * as campaignInvitesApi from '@/services/api/campaignInvites';
import type { UserCampaignRead } from '@/types/user_campaign';
import type { CampaignInvite } from '@/types/campaign_invite';
import { CampaignRoleEnum } from '@/types/campaign_role';

export default defineComponent({
  name: 'CampaignDetailView',
  components: {
      CampaignMemberList,
      CampaignInviteList,
      CreateCampaignInviteForm
  },
  props: {
    // Díky props: true v routeru můžeme přijmout ID jako prop
    campaignId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const campaign = ref<Campaign | null>(null);
    const world = ref<World | null>(null); // Pro uložení informací o světě
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

    const isCurrentUserGM = computed(() => {
      if (!currentUserId.value || membersLoading.value || members.value.length === 0) {
        return false;
      }
      const currentUserMembership = members.value.find(m => m.user_id === currentUserId.value);
      return currentUserMembership?.role === CampaignRoleEnum.GM;
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
        // Nepovažujeme za chybu stránky, pokud se nepodaří načíst pozvánky (může být 403)
        invitesError.value = `Failed to load invites: ${err.response?.data?.detail || err.message || 'Forbidden?'}`;
        console.warn("Load Invites Error:", err);
      } finally {
        invitesLoading.value = false;
      }
    };

    const loadCampaignDetail = async (id: number) => {
      loading.value = true;
      error.value = null;
      campaign.value = null;
      world.value = null;
      loadingWorld.value = false;
      members.value = []; // Reset members on campaign change
      invites.value = []; // Reset invites on campaign change
      membersLoading.value = false;
      membersError.value = undefined;
      invitesLoading.value = false;
      invitesError.value = undefined;

      try {
        campaign.value = await campaignsApi.getCampaignById(id);
        if (campaign.value) {
          await loadWorldDetail(campaign.value.world_id);
          // Načteme členy hned po načtení kampaně
          await loadMembers(campaign.value.id);
        }
      } catch (err: any) {
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load campaign details.');
        console.error("Load Campaign Detail Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const loadWorldDetail = async (worldId: number) => {
        loadingWorld.value = true;
         try {
            world.value = await worldsApi.getWorldById(worldId);
         } catch (err: any) {
             console.error("Load World Detail Error:", err);
             // Chybu světa nemusíme nutně zobrazovat jako hlavní chybu stránky
             // Můžeme zobrazit jen ID světa jako fallback
         } finally {
            loadingWorld.value = false;
         }
    };

    // Formátování data (jednoduchý příklad)
    const formatDate = (dateString: string) => {
      if (!dateString) return 'N/A';
      try {
        return new Date(dateString).toLocaleDateString();
      } catch (e) {
        return dateString; // Fallback na původní string
      }
    };

    const worldName = computed(() => {
        if (loadingWorld.value) return 'Loading world...';
        return world.value ? world.value.name : `ID: ${campaign.value?.world_id}`;
    });

    // Načíst pozvánky, až když víme, že je uživatel GM (po načtení členů)
    watch(isCurrentUserGM, (isGM) => {
        if(isGM && campaign.value && !invitesLoading.value) {
            loadInvites(campaign.value.id);
        }
    }); // immediate: true není potřeba, závisí na members

    // Sledování změn ID v URL
    watch(
      () => props.campaignId,
      (newId) => {
        if (newId) {
          loadCampaignDetail(Number(newId));
        }
      },
      { immediate: true }
    );

    // Handlery pro události z child komponent
    const handleMembersUpdated = () => {
      if (campaign.value) {
        loadMembers(campaign.value.id);
      }
    };
    const handleInvitesUpdated = () => {
      if (campaign.value && isCurrentUserGM.value) {
        loadInvites(campaign.value.id);
      }
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
  margin-bottom: 1.5rem;
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
}

/* Styly pro tlačítko Zpět (pokud je třeba) */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  text-decoration: none;
}
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }

.management-section {
    margin-top: 2rem;
}
</style> 