<template>
  <form @submit.prevent="handleSubmit" class="create-organization-form">
    <h3>{{ isEditing ? 'Edit Organization' : 'Add New Organization' }}</h3>
    
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div class="form-group">
      <label for="org-name">Name:</label>
      <input 
        type="text" 
        id="org-name" 
        v-model.trim="formData.name" 
        required 
        maxlength="255"
      />
    </div>

    <div class="form-group">
      <label for="org-description">Description:</label>
      <textarea 
        id="org-description" 
        v-model="formData.description"
      ></textarea>
    </div>

    <div class="form-group">
      <label for="org-parent">Parent Organization (Optional):</label>
      <select id="org-parent" v-model="formData.parent_organization_id">
        <option :value="null">-- None --</option>
        <option 
          v-for="org in availableParentOrganizations" 
          :key="org.id" 
          :value="org.id"
        >
          {{ org.name }}
        </option>
      </select>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
        {{ isSubmitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Organization') }}
      </button>
      <button type="button" @click="$emit('cancel')" class="btn btn-secondary">
        Cancel
      </button>
    </div>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, watch, computed, type PropType } from 'vue';
import * as organizationsApi from '@/services/api/organizations';
import type { Organization, OrganizationCreate, OrganizationUpdate } from '@/types/organization';

interface FormData {
  name: string;
  description: string | null;
  parent_organization_id: number | null;
}

export default defineComponent({
  name: 'CreateOrganizationForm',
  props: {
    worldId: {
      type: Number,
      required: true,
    },
    organizations: {
      type: Array as PropType<Organization[]>,
      required: true,
    },
    organizationToEdit: {
      type: Object as PropType<Organization | null>,
      default: null,
    },
  },
  emits: ['saved', 'cancel'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const errorMessage = ref<string | null>(null);

    const isEditing = computed(() => !!props.organizationToEdit);

    const initialFormData: FormData = {
      name: '',
      description: null,
      parent_organization_id: null,
    };

    const formData = reactive<FormData>({ ...initialFormData });

    // Filter out the organization being edited from potential parents
    const availableParentOrganizations = computed(() => {
      if (isEditing.value && props.organizationToEdit) {
        return props.organizations.filter(org => org.id !== props.organizationToEdit?.id);
      }
      return props.organizations;
    });

    // Reset form when switching between add/edit or when edit data changes
    watch(
      () => props.organizationToEdit,
      (newVal) => {
        errorMessage.value = null; // Clear errors on change
        if (newVal && isEditing.value) {
          formData.name = newVal.name;
          formData.description = newVal.description ?? null;
          formData.parent_organization_id = newVal.parent_organization_id ?? null;
        } else {
          Object.assign(formData, initialFormData); // Reset to initial state
        }
      },
      { immediate: true, deep: true }
    );

    const handleSubmit = async () => {
      isSubmitting.value = true;
      errorMessage.value = null;

      try {
        if (isEditing.value && props.organizationToEdit) {
          // Update existing organization
          const updateData: OrganizationUpdate = {
            name: formData.name !== props.organizationToEdit.name ? formData.name : undefined,
            description: formData.description !== props.organizationToEdit.description ? formData.description : undefined,
            parent_organization_id: formData.parent_organization_id !== props.organizationToEdit.parent_organization_id ? formData.parent_organization_id : undefined,
          };
          // Filter out undefined values to avoid sending them
          const filteredUpdateData = Object.fromEntries(
             Object.entries(updateData).filter(([, value]) => value !== undefined)
          );
          
          if (Object.keys(filteredUpdateData).length > 0) {
            await organizationsApi.updateOrganization(props.organizationToEdit.id, filteredUpdateData as OrganizationUpdate);
          } else {
             console.log("No changes detected for update."); // Or provide user feedback
          } 
        } else {
          // Create new organization
          const createData: OrganizationCreate = {
            ...formData,
            world_id: props.worldId,
            description: formData.description || undefined, // Send undefined if null/empty for backend consistency?
          };
          await organizationsApi.createOrganization(createData);
        }
        emit('saved');
      } catch (err: any) {
        console.error('Error saving organization:', err);
        errorMessage.value = err.response?.data?.detail || err.message || 'Failed to save organization. Please check the details.';
      } finally {
        isSubmitting.value = false;
      }
    };

    return {
      formData,
      isEditing,
      isSubmitting,
      errorMessage,
      availableParentOrganizations,
      handleSubmit,
    };
  },
});
</script>

<style scoped>
.create-organization-form {
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.create-organization-form h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
  font-weight: 600;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 1rem;
  box-sizing: border-box; /* Include padding and border in element's total width and height */
}

.form-group textarea {
  min-height: 80px; /* Adjust as needed */
  resize: vertical; /* Allow vertical resizing */
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem; /* Space between buttons */
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.error-message {
  background-color: #f8d7da; /* Light red background */
  color: #721c24; /* Dark red text */
  border: 1px solid #f5c6cb; /* Red border */
  padding: 0.75rem 1.25rem;
  margin-bottom: 1rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

/* Reusing btn styles from OrganizationDetailView or define globally */
.btn {
  display: inline-block;
  font-weight: 400;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  border: 1px solid transparent;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  text-decoration: none;
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-primary {
  color: #fff;
  background-color: #007bff;
  border-color: #007bff;
}
.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}
.btn-primary:disabled {
  background-color: #007bff;
  border-color: #007bff;
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-secondary {
  color: #fff;
  background-color: #6c757d;
  border-color: #6c757d;
}
.btn-secondary:hover {
  color: #fff;
  background-color: #5a6268;
  border-color: #545b62;
}
</style> 