<template>
  <div class="member-list-section detail-section">
    <h2>Members</h2>
    <div v-if="loading" class="loading-state">Loading members...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="members.length > 0">
      <ul class="member-list">
        <li v-for="member in members" :key="member.id" class="member-item">
          <span class="member-name">{{ member.user.username }} ({{ member.user.email }})</span>
          <span class="member-role">
            <template v-if="isEditingRole === member.id">
              <select v-model="editingRoleValue" @change="saveRoleChange(member.user_id)">
                <option v-for="role in availableRoles" :key="role" :value="role">
                  {{ role }}
                </option>
              </select>
              <button @click="cancelRoleEdit" class="btn-small btn-secondary">Cancel</button>
            </template>
            <template v-else>
              {{ member.role }}
              <button v-if="canManage && member.user_id !== currentUserId"
                      @click="startRoleEdit(member)"
                      class="btn-small btn-secondary btn-edit-role">
                Edit Role
              </button>
            </template>
          </span>
          <button v-if="canManage && member.user_id !== currentUserId"
                  @click="removeMember(member.user_id, member.user.username)"
                  class="btn-small btn-danger btn-remove">
            Remove
          </button>
        </li>
      </ul>
    </div>
    <div v-else>No members found (besides the owner).</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, type PropType } from 'vue';
import type { UserCampaignRead } from '@/types/user_campaign';
import { CampaignRoleEnum } from '@/types/campaign_role';
import * as campaignMembersApi from '@/services/api/campaignMembers';

export default defineComponent({
  name: 'CampaignMemberList',
  props: {
    members: {
      type: Array as PropType<UserCampaignRead[]>,
      required: true,
    },
    campaignId: {
      type: Number,
      required: true,
    },
    canManage: {
      type: Boolean,
      default: false,
    },
    currentUserId: {
      type: Number,
      required: true,
    },
    loading: Boolean,
    error: String,
  },
  emits: ['members-updated'], // Emit event when members list changes
  setup(props, { emit }) {
    const isEditingRole = ref<number | null>(null); // Store the ID of the UserCampaign being edited
    const editingRoleValue = ref<CampaignRoleEnum>(CampaignRoleEnum.PLAYER);
    const availableRoles = ref(Object.values(CampaignRoleEnum));

    const startRoleEdit = (member: UserCampaignRead) => {
      isEditingRole.value = member.id;
      editingRoleValue.value = member.role;
    };

    const cancelRoleEdit = () => {
      isEditingRole.value = null;
    };

    const saveRoleChange = async (userId: number) => {
      if (!isEditingRole.value) return;
      try {
        await campaignMembersApi.updateCampaignMemberRole(props.campaignId, userId, editingRoleValue.value);
        alert('Role updated successfully!');
        isEditingRole.value = null;
        emit('members-updated'); // Notify parent to refresh list
      } catch (err: any) {         alert(`Error updating role: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
        // Optionally keep editing mode open or close it
        // cancelRoleEdit();
      }
    };

    const removeMember = async (userId: number, username: string) => {
      if (confirm(`Are you sure you want to remove member "${username}" from the campaign?`)) {
        try {
          await campaignMembersApi.removeCampaignMember(props.campaignId, userId);
          alert('Member removed successfully!');
          emit('members-updated'); // Notify parent to refresh list
        } catch (err: any) {
          alert(`Error removing member: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
        }
      }
    };

    return {
      isEditingRole,
      editingRoleValue,
      availableRoles,
      startRoleEdit,
      cancelRoleEdit,
      saveRoleChange,
      removeMember,
    };
  },
});
</script>

<style scoped>
.member-list-section {
  /* Styles inherit from CampaignDetailView or add specific ones */
}
.member-list {
  list-style: none;
  padding: 0;
}
.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid #e9ecef;
}
.member-item:last-child {
  border-bottom: none;
}
.member-name {
  font-weight: 500;
}
.member-role {
  margin-left: auto;
  margin-right: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.member-role select {
    padding: 0.2rem 0.4rem;
    border-radius: 0.2rem;
    border: 1px solid #ced4da;
    font-size: 0.85rem;
}

.btn-small {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
}
.btn-edit-role {
    margin-left: 0.5rem; /* Add some space */
}
.btn-secondary { background-color: #6c757d; color: white; border: none; border-radius: 0.2rem; cursor: pointer; }
.btn-secondary:hover { background-color: #5a6268; }
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