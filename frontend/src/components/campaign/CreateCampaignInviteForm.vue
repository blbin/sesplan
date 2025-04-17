<template>
  <div class="create-invite-section detail-section">
    <h2>Create New Invite</h2>
    <form @submit.prevent="createInvite" class="invite-form">
      <div class="form-group">
        <label for="max-uses">Max Uses (optional, 0 or empty for unlimited):</label>
        <input type="number" id="max-uses" v-model.number="inviteData.max_uses" min="0">
      </div>
      <div class="form-group">
        <label for="expires-at">Expires At (optional):</label>
        <input type="datetime-local" id="expires-at" v-model="inviteData.expires_at">
      </div>
      <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
        {{ isSubmitting ? 'Creating...' : 'Create Invite Link' }}
      </button>
      <div v-if="error" class="error-message form-error">{{ error }}</div>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';
import type { CampaignInviteCreate } from '@/types/campaign_invite';
import * as campaignInvitesApi from '@/services/api/campaignInvites';

export default defineComponent({
  name: 'CreateCampaignInviteForm',
  props: {
    campaignId: {
      type: Number,
      required: true,
    },
  },
  emits: ['invites-updated'], // Emit event when invites list changes
  setup(props, { emit }) {
    const inviteData = reactive<CampaignInviteCreate>({
      max_uses: 1, // Default to 1 use
      expires_at: null,
    });
    const isSubmitting = ref(false);
    const error = ref<string | null>(null);

    const createInvite = async () => {
      isSubmitting.value = true;
      error.value = null;
      try {
        // Convert empty string or 0 for max_uses to null for the API
        const payload: CampaignInviteCreate = {
          max_uses: inviteData.max_uses === 0 || inviteData.max_uses === null ? null : inviteData.max_uses,
          expires_at: inviteData.expires_at ? new Date(inviteData.expires_at).toISOString() : null,
        };
        await campaignInvitesApi.createCampaignInvite(props.campaignId, payload);
        alert('Invite created successfully!');
        // Reset form
        inviteData.max_uses = 1;
        inviteData.expires_at = null;
        emit('invites-updated'); // Notify parent to refresh list
      } catch (err: any) {
        error.value = `Error creating invite: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        alert(error.value);
      } finally {
        isSubmitting.value = false;
      }
    };

    return {
      inviteData,
      isSubmitting,
      error,
      createInvite,
    };
  },
});
</script>

<style scoped>
.create-invite-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.invite-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 400px; /* Limit form width */
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
  color: #495057;
}

.form-group input {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 0.95rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.btn-primary:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.form-error {
    margin-top: 0.5rem;
}

.error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 0.8rem;
    border-radius: 0.25rem;
    font-size: 0.9rem;
}
</style> 