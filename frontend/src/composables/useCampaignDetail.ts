import { ref, computed, watch, shallowRef } from 'vue';
import type { Ref } from 'vue';
import * as campaignsApi from '@/services/api/campaigns';
import * as worldsApi from '@/services/api/worlds';
import * as campaignMembersApi from '@/services/api/campaignMembers';
import type { Campaign } from '@/types/campaign';
import type { World } from '@/types/world';
import type { UserCampaignRead } from '@/types/user_campaign';
import { CampaignRoleEnum } from '@/types/campaign_role';
import { useAuthStore } from '@/store/auth.store';

export function useCampaignDetail(campaignId: Ref<number | null>) {
  const campaign = shallowRef<Campaign | null>(null);
  const world = shallowRef<World | null>(null);
  const members = ref<UserCampaignRead[]>([]);

  const loading = ref(false);
  const error = ref<string | null>(null);
  const loadingWorld = ref(false);
  const membersLoading = ref(false);
  const membersError = ref<string | undefined>(undefined);

  // Name Editing State
  const isEditingName = ref(false);
  const editedName = ref('');
  const isSavingName = ref(false);

  const authStore = useAuthStore();
  const currentUserId = computed(() => authStore.user?.id);

  const isCurrentUserGM = computed<boolean | null>(() => {
    if (membersLoading.value || !currentUserId.value) return null;
    const currentUserMembership = members.value.find(m => m.user_id === currentUserId.value);
    return currentUserMembership?.role === CampaignRoleEnum.GM;
  });

  const owner = computed<UserCampaignRead | null>(() => {
    if (membersLoading.value) return null;
    return members.value.find(m => m.role === CampaignRoleEnum.GM) || null;
  });

  const loadWorldDetail = async (worldId: number) => {
    loadingWorld.value = true;
    try {
      world.value = await worldsApi.getWorldById(worldId);
    } catch (err: any) {
      console.error("Load World Detail Error:", err);
      // Optionally set an error state specific to the world
    } finally {
      loadingWorld.value = false;
    }
  };

  const loadMembers = async (id: number) => {
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

  const loadCampaignData = async (id: number | null) => {
    if (id === null) {
      error.value = "Invalid Campaign ID.";
      loading.value = false;
      campaign.value = null;
      world.value = null;
      members.value = [];
      return;
    }

    loading.value = true;
    error.value = null;
    campaign.value = null;
    world.value = null;
    members.value = []; // Reset members as well

    try {
      // Fetch campaign details first
      campaign.value = await campaignsApi.getCampaignById(id);

      // Fetch world and members in parallel
      const promises = [];
      if (campaign.value?.world_id) {
        promises.push(loadWorldDetail(campaign.value.world_id));
      }
      promises.push(loadMembers(id));

      await Promise.all(promises);

    } catch (err: any) {
      console.error("Load Campaign Data Error:", err);
      error.value = `Failed to load campaign: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
      campaign.value = null; // Ensure campaign is null on error
    } finally {
      loading.value = false;
      // Ensure loading flags are correctly set even if errors occurred during parallel fetches
      if (membersLoading.value) membersLoading.value = false;
      if (loadingWorld.value) loadingWorld.value = false;
    }
  };

  // Watch the campaignId for changes and reload data
  watch(campaignId, (newId) => {
    loadCampaignData(newId);
  }, { immediate: true }); // Load data immediately when the composable is used

  // Function to explicitly reload members (e.g., after an update)
  const reloadMembers = () => {
      if (campaignId.value !== null) {
          loadMembers(campaignId.value);
      }
  };

  // --- Name Editing Functions ---
  const startEditingName = () => {
    if (!campaign.value || !isCurrentUserGM.value) return; // Only GM can edit
    editedName.value = campaign.value.name;
    isEditingName.value = true;
  };

  const cancelEditingName = () => {
    isEditingName.value = false;
  };

  const saveName = async () => {
    if (!campaign.value || !editedName.value.trim() || editedName.value === campaign.value.name || !isCurrentUserGM.value) {
      isEditingName.value = false;
      return;
    }

    isSavingName.value = true;
    try {
      // Assume updateCampaign only needs the fields being changed
      const updatedCampaignData = await campaignsApi.updateCampaign(campaign.value.id, { name: editedName.value.trim() });
      // Update the local campaign state
      campaign.value = { ...campaign.value, ...updatedCampaignData };
      isEditingName.value = false;
      console.log("[useCampaignDetail] Campaign name saved successfully.");
    } catch (err: any) {
      console.error("[useCampaignDetail] Failed to save campaign name:", err);
      // Consider adding user-facing error feedback here (e.g., via an event or state)
      // error.value = `Failed to save name: ${err.message || 'Unknown error'}`; // Avoid overwriting the main load error
      alert(`Failed to save name: ${err.response?.data?.detail || err.message || 'Unknown error'}`); // Simple alert for now
    } finally {
      isSavingName.value = false;
    }
  };

  return {
    campaign,
    world,
    members,
    loading,
    error,
    loadingWorld,
    membersLoading,
    membersError,
    isCurrentUserGM,
    owner,
    loadCampaignData, // Expose main loading function if needed elsewhere
    reloadMembers, // Expose member reload function
    // Name Editing
    isEditingName,
    editedName,
    isSavingName,
    startEditingName,
    cancelEditingName,
    saveName
  };
} 