import { ref, computed, watch } from 'vue';
import type { Ref, ComputedRef } from 'vue';
import type { Campaign, CampaignUpdate } from '@/types/campaign';
import * as campaignsApi from '@/services/api/campaigns';
// import { marked } from 'marked'; // Remove marked
import MarkdownIt from 'markdown-it'; // Import MarkdownIt

// Initialize markdown-it instance
const md = new MarkdownIt({
  html: false, // Keep HTML disabled for security unless specifically needed
  linkify: true,
  typographer: true,
});

export function useCampaignDetailDescription(
  campaign: Ref<Campaign | null>,
  isCurrentUserGM: ComputedRef<boolean | null>
) {
  const isEditingDescription = ref(false);
  const editedDescription = ref('');
  const isSavingDescription = ref(false);
  const saveError = ref<string | null>(null);

  // Watch for campaign changes to reset editing state if needed
  watch(campaign, (newCampaign) => {
    if (newCampaign) {
      editedDescription.value = newCampaign.description || '';
    }
    // Optionally reset editing state when campaign changes
    // isEditingDescription.value = false; 
  }, { immediate: true });

  const renderedDescription = computed(() => {
    if (campaign.value?.description) {
      try {
        // Use markdown-it's render method
        return md.render(campaign.value.description);
      } catch (error) {
        console.error('Error rendering markdown:', error);
        return '<p>Error rendering description.</p>'; 
      }
    }
    return '';
  });

  const startEditingDescription = () => {
    if (isCurrentUserGM.value && campaign.value) {
      editedDescription.value = campaign.value.description || '';
      isEditingDescription.value = true;
    }
  };

  const cancelEditingDescription = () => {
    if (campaign.value) {
      editedDescription.value = campaign.value.description || '';
    }
    isEditingDescription.value = false;
    saveError.value = null; // Clear any previous error
  };

  const saveDescription = async () => {
    if (!campaign.value || !isCurrentUserGM.value || !campaign.value.id) {
      saveError.value = 'Cannot save description: Missing data or insufficient permissions.';
      return;
    }

    isSavingDescription.value = true;
    saveError.value = null;
    try {
      const updateData: CampaignUpdate = {
        // Include other potentially updatable fields if the API requires them
        // For now, assuming only description is updated here.
        // Check CampaignUpdate type for required fields.
        // Let's assume name is also needed or can be passed
        name: campaign.value.name, // Pass current name
        description: editedDescription.value,
        // world_id: campaign.value.world_id // Pass world_id if required
      };
      const updatedCampaign = await campaignsApi.updateCampaign(campaign.value.id, updateData);
      
      // Update the local campaign ref with the response
      campaign.value = { ...campaign.value, ...updatedCampaign }; 
      
      isEditingDescription.value = false;
    } catch (err: any) {
      console.error("Failed to save campaign description:", err);
      saveError.value = `Failed to save: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    } finally {
      isSavingDescription.value = false;
    }
  };

  return {
    isEditingDescription,
    editedDescription,
    isSavingDescription,
    saveError,
    renderedDescription, // Expose rendered description
    startEditingDescription,
    cancelEditingDescription,
    saveDescription,
  };
} 