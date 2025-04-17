<template>
  <form @submit.prevent="createInvite" class="invite-form">
    <div class="form-group">
      <label for="max-uses">Max Uses (optional, 0 or empty for unlimited):</label>
      <input type="number" id="max-uses" v-model.number="inviteData.max_uses" min="0">
    </div>
    <div class="form-group">
      <label for="expires-at">Expires At (optional):</label>
      <input type="datetime-local" id="expires-at" v-model="inviteData.expires_at">
    </div>
    <div v-if="error" class="error-message form-error">{{ error }}</div>
    <div class="modal-actions">
      <button type="button" @click="cancelInvite" class="btn btn-secondary">Cancel</button>
      <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
        {{ isSubmitting ? 'Creating...' : 'Create Invite Link' }}
      </button>
    </div>
  </form>
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
  emits: ['invite-sent', 'cancel'],
  setup(props, { emit }) {
    const inviteData = reactive<Partial<CampaignInviteCreate>>({
      max_uses: 1,
      expires_at: null,
    });
    const isSubmitting = ref(false);
    const error = ref<string | null>(null);

    const createInvite = async () => {
      isSubmitting.value = true;
      error.value = null;
      try {
        const payload: CampaignInviteCreate = {
          max_uses: inviteData.max_uses === 0 || !inviteData.max_uses ? null : Number(inviteData.max_uses),
          expires_at: inviteData.expires_at ? new Date(inviteData.expires_at).toISOString() : null,
        };
        await campaignInvitesApi.createCampaignInvite(props.campaignId, payload);
        inviteData.max_uses = 1;
        inviteData.expires_at = null;
        emit('invite-sent');
      } catch (err: any) {
        error.value = `Error creating invite: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
      } finally {
        isSubmitting.value = false;
      }
    };

    const cancelInvite = () => {
      emit('cancel');
    };

    return {
      inviteData,
      isSubmitting,
      error,
      createInvite,
      cancelInvite,
    };
  },
});
</script>

<style scoped>
.invite-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
    padding: 0.6rem 1.2rem;
    border-radius: 0.3rem;
    cursor: pointer;
    border: none;
    font-weight: 500;
    text-decoration: none;
    transition: background-color 0.2s ease;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover:not(:disabled) { background-color: #0056b3; }
.btn-primary:disabled { background-color: #adb5bd; cursor: not-allowed; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }

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