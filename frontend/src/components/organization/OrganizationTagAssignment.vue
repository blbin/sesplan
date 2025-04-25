<template>
  <div class="tag-assignment">
    <h4>Assign Tags</h4>
    
    <!-- Display existing tags -->
    <div v-if="assignedTags.length > 0" class="assigned-tags">
      <span v-for="tag in assignedTags" :key="tag.id" class="tag-chip">
        {{ tag.tag_type?.name || `Tag ID: ${tag.organization_tag_type_id}` }}
        <button 
          @click="removeTag(tag.organization_tag_type_id)" 
          class="remove-btn"
          :disabled="isRemoving === tag.organization_tag_type_id"
          title="Remove tag"
        >
          &times;
        </button>
      </span>
    </div>
    <div v-else class="no-tags-message">No tags assigned yet.</div>

    <!-- Assign new tag dropdown -->
    <div class="assign-new-tag">
      <select v-model="selectedTagTypeIdToAdd" :disabled="isAdding">
        <option :value="null" disabled>-- Select a tag to add --</option>
        <option 
          v-for="tagType in availableTagTypesForAssignment" 
          :key="tagType.id" 
          :value="tagType.id"
        >
          {{ tagType.name }}
        </option>
      </select>
      <button 
        @click="assignTag" 
        :disabled="!selectedTagTypeIdToAdd || isAdding"
        class="btn btn-primary btn-sm"
      >
        {{ isAdding ? 'Assigning...' : 'Assign Tag' }}
      </button>
    </div>
    <div v-if="assignmentError" class="error-message">{{ assignmentError }}</div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, type PropType } from 'vue';
import type { OrganizationTag } from '@/types/organizationTag';
import type { OrganizationTagType } from '@/types/organizationTagType';
import * as organizationsApi from '@/services/api/organizations'; // For add/remove

export default defineComponent({
  name: 'OrganizationTagAssignment',
  props: {
    organizationId: {
      type: Number,
      required: true,
    },
    assignedTags: {
      type: Array as PropType<OrganizationTag[]>,
      required: true,
    },
    availableTagTypes: {
      type: Array as PropType<OrganizationTagType[]>,
      required: true,
    },
    // canManage prop might be needed to disable controls
    canManage: {
       type: Boolean,
       default: true, 
    }
  },
  emits: ['tags-updated'], 
  setup(props, { emit }) {
    const selectedTagTypeIdToAdd = ref<number | null>(null);
    const isAdding = ref(false);
    const isRemoving = ref<number | null>(null); // Store ID of tag being removed
    const assignmentError = ref<string | null>(null);

    // Filter available types to show only those not already assigned
    const availableTagTypesForAssignment = computed(() => {
      const assignedTypeIds = new Set(props.assignedTags.map(tag => tag.organization_tag_type_id));
      return props.availableTagTypes.filter(type => !assignedTypeIds.has(type.id));
    });

    const assignTag = async () => {
      if (!selectedTagTypeIdToAdd.value || isAdding.value) return;
      
      isAdding.value = true;
      assignmentError.value = null;
      try {
        await organizationsApi.addTagToOrganization(props.organizationId, selectedTagTypeIdToAdd.value);
        selectedTagTypeIdToAdd.value = null; // Reset dropdown
        emit('tags-updated'); // Notify parent to refetch organization data (which includes tags)
      } catch (err: any) {
        console.error("Error assigning tag:", err);
        assignmentError.value = err.response?.data?.detail || err.message || 'Failed to assign tag';
      } finally {
        isAdding.value = false;
      }
    };

    const removeTag = async (tagTypeId: number) => {
      isRemoving.value = tagTypeId;
      assignmentError.value = null;
       try {
        await organizationsApi.removeTagFromOrganization(props.organizationId, tagTypeId);
        emit('tags-updated'); 
      } catch (err: any) {
        console.error("Error removing tag:", err);
        assignmentError.value = err.response?.data?.detail || err.message || 'Failed to remove tag';
      } finally {
        isRemoving.value = null;
      }
    };

    return {
      selectedTagTypeIdToAdd,
      isAdding,
      isRemoving,
      assignmentError,
      availableTagTypesForAssignment,
      assignTag,
      removeTag,
    };
  },
});
</script>

<style scoped>
.tag-assignment {
  margin-top: 1.5rem;
}

h4 {
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.assigned-tags {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  background-color: #e9ecef; /* Light grey */
  color: #495057; /* Dark grey text */
  padding: 0.3rem 0.6rem;
  border-radius: 1rem; /* Pill shape */
  font-size: 0.85rem;
  white-space: nowrap;
}

.remove-btn {
  background: none;
  border: none;
  color: #6c757d; /* Medium grey */
  font-size: 1.1rem;
  font-weight: bold;
  margin-left: 0.4rem;
  padding: 0;
  line-height: 1;
  cursor: pointer;
  opacity: 0.7;
}

.remove-btn:hover {
  color: #dc3545; /* Red on hover */
  opacity: 1;
}

.remove-btn:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.no-tags-message {
  font-style: italic;
  color: #6c757d;
  margin-bottom: 1rem;
}

.assign-new-tag {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.assign-new-tag select {
  padding: 0.4rem 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  flex-grow: 1;
  max-width: 300px; /* Limit width */
}

.error-message {
  color: #721c24;
  background-color: #f8d7da;
  border-color: #f5c6cb;
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
  border: 1px solid transparent;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

/* Reusing button styles */
.btn {
    /* Basic styles */
    display: inline-block; 
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    text-align: center; 
    vertical-align: middle;
    cursor: pointer;
    user-select: none;
    border: 1px solid transparent;
    border-radius: 0.25rem;
    transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;
}
.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: .875rem;
    border-radius: 0.2rem;
}
.btn-primary {
    color: #fff;
    background-color: #007bff;
    border-color: #007bff;
}
.btn-primary:hover {
    color: #fff;
    background-color: #0069d9;
    border-color: #0062cc;
}
.btn:disabled {
    opacity: .65;
    cursor: not-allowed;
}

</style> 