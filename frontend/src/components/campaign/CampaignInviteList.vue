<template>
  <div class="invite-list-section detail-section">
    <h2>Invites</h2>
    <div v-if="loading" class="loading-state">Loading invites...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="invites.length > 0">
      <ul class="invite-list">
        <li v-for="invite in invites" :key="invite.id" class="invite-item">
          <span class="invite-token">Token: <code>{{ invite.token }}</code></span>
          <span class="invite-details">
            Uses: {{ invite.uses }} / {{ invite.max_uses === null ? '∞' : invite.max_uses }}
            <span v-if="invite.expires_at"> | Expires: {{ formatDateTime(invite.expires_at) }}</span>
          </span>
          <div class="invite-actions">
            <button @click="copyInviteLink(invite.token, invite.id)" class="btn-small btn-secondary">
              {{ copyStatus[invite.id] ? 'Copied!' : 'Copy Link' }}
            </button>
            <button v-if="canManage" @click="deleteInvite(invite.id)" class="btn-small btn-danger">
              Delete Invite
            </button>
          </div>
        </li>
      </ul>
    </div>
    <div v-else>No active invites found.</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, reactive } from 'vue';
import type { CampaignInvite } from '@/types/campaign_invite';
import * as campaignInvitesApi from '@/services/api/campaignInvites';

export default defineComponent({
  name: 'CampaignInviteList',
  props: {
    invites: {
      type: Array as PropType<CampaignInvite[]>,
      required: true,
    },
    campaignId: {
      type: Number,
      required: true,
    },
    canManage: {
      type: [Boolean, null] as PropType<boolean | null>,
      default: null,
    },
    loading: Boolean,
    error: String,
  },
  emits: ['invites-updated'], // Emit event when invites list changes
  setup(_props, { emit }) {
    const copyStatus = reactive<Record<number, boolean>>({});

    const formatDateTime = (dateTimeString: string | null): string => {
      if (!dateTimeString) return 'Never';
      try {
        return new Date(dateTimeString).toLocaleString();
      } catch (e) {
        return dateTimeString; // Fallback
      }
    };

    const deleteInvite = async (inviteId: number) => {
      if (confirm('Are you sure you want to delete this invite link?')) {
        try {
          await campaignInvitesApi.deleteCampaignInvite(inviteId);
          alert('Invite deleted successfully!');
          emit('invites-updated'); // Notify parent to refresh list
        } catch (err: any) {
          alert(`Error deleting invite: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
        }
      }
    };

    // Pass inviteId for feedback
    const copyInviteLink = async (token: string, inviteId: number) => {
      const inviteUrl = `${window.location.origin}/invite/${token}`;
      try {
        await navigator.clipboard.writeText(inviteUrl);
        copyStatus[inviteId] = true;
        setTimeout(() => {
          copyStatus[inviteId] = false;
        }, 1500);
      } catch (err) {
        console.error('Failed to copy invite link:', err);
        alert('Failed to copy invite link. Please copy it manually.');
      }
    };

    return {
      formatDateTime,
      deleteInvite,
      copyInviteLink,
      copyStatus,
    };
  },
});
</script>

<style scoped>
.invite-list-section {
    margin-top: 2rem;
}
.invite-list {
  list-style: none;
  padding: 0;
}
.invite-item {
  display: flex;
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid #e9ecef;
  gap: 0.5rem;
}
.invite-item:last-child {
  border-bottom: none;
}
.invite-token {
  font-family: monospace;
  background-color: #f1f3f5;
  padding: 0.2rem 0.4rem;
  border-radius: 0.2rem;
  word-break: break-all; /* Prevent long tokens from overflowing */
}
.invite-details {
  font-size: 0.85rem;
  color: #6c757d;
}

/* Re-use button styles */
.btn-small {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
}
.btn-danger { background-color: #dc3545; color: white; border: none; border-radius: 0.2rem; cursor: pointer; }
.btn-danger:hover { background-color: #c82333; }

.loading-state,
.error-message {
    padding: 1rem;
    text-align: center;
    color: #6c757d;
}
.error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 0.25rem;
}
</style> 