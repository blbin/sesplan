<template>
  <form @submit.prevent="handleSaveCharacter" class="character-form">
    <div class="form-group">
      <label for="characterName">Name *</label>
      <v-text-field 
        v-model="formData.name" 
        :rules="[rules.required]"
        variant="outlined"
        density="compact"
        id="characterName"
      />
    </div>
    <div class="form-group">
      <label for="characterDescription">Description</label>
      <MarkdownEditor 
        v-model="formData.description as string"
        id="characterDescription"
        label="Character Description" 
      />
    </div>

    <!-- Assign User Select (Only for Owner) -->
    <div class="form-group" v-if="isOwner">
        <label for="characterAssignUser">Assign User</label>
        <v-select
            v-model="formData.user_id"
            :items="assignableUserOptions"
            label="Select user to assign"
            item-title="username"
            item-value="id"
            id="characterAssignUser"
            density="compact"
            variant="outlined"
            clearable
            hide-details
            :disabled="!isOwner || !assignableUsers || assignableUsers.length === 0"
            >
            <template v-slot:no-data>
                <v-list-item>
                <v-list-item-title>
                    No users available in world campaigns.
                </v-list-item-title>
                </v-list-item>
            </template>
        </v-select>
    </div>

    <v-alert v-if="formError" type="error" variant="tonal" density="compact" class="mb-4">
      {{ formError }}
    </v-alert>

    <div class="form-actions">
      <v-btn variant="text" @click="onCancel">Cancel</v-btn>
      <v-btn 
        color="primary" 
        type="submit" 
        :loading="isSubmitting"
        :disabled="!formData.name.trim()"
       >
        {{ isSubmitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Character') }}
      </v-btn>
    </div>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, watch, computed } from 'vue';
import type { PropType } from 'vue';
import * as charactersApi from '@/services/api/characters';
import type { Character, CharacterCreate, CharacterUpdate } from '@/types/character';
import type { UserSimple } from '@/services/api/worlds'; // Import UserSimple
// Removed CharacterTagType import
// Import Vuetify components used
import { VTextField, VBtn, VAlert, VSelect, VListItem, VListItemTitle } from 'vuetify/components'; // Removed VTextarea, VSelect
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'; // Import MarkdownEditor

interface CharacterFormData {
  name: string;
  description: string | null;
  user_id: number | null; // Add user_id
}

export default defineComponent({
  name: 'CreateCharacterForm',
  components: { VTextField, VBtn, VAlert, VSelect, VListItem, VListItemTitle, MarkdownEditor }, // Added MarkdownEditor, removed VTextarea, VSelect
  props: {
    worldId: {
      type: Number,
      required: true, 
    },
    characterToEdit: {
      type: Object as PropType<Character | null>,
      default: null,
    },
    // Removed availableTagTypes prop
    isOwner: {
        type: Boolean,
        default: false,
    },
    assignableUsers: {
        type: Array as PropType<UserSimple[]>,
        default: () => [],
    }
  },
  emits: ['saved', 'cancel'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const formError = ref<string | null>(null);
    // Removed selectedTagTypeIds

    // Basic required rule for Vuetify fields
    const rules = {
      required: (value: string) => !!value || 'This field is required.',
    };

    const formData = reactive<CharacterFormData>({
      name: '',
      description: '',
      user_id: null, // Initialize user_id
    });

    const isEditing = computed(() => !!props.characterToEdit);

    // Computed property for v-select items
    const assignableUserOptions = computed(() => {
        return props.assignableUsers.map(user => ({
            id: user.id,
            username: user.username
        }));
    });

    watch(
      () => props.characterToEdit,
      (character) => {
        if (character) {
          formData.name = character.name;
          formData.description = character.description || '';
          formData.user_id = character.user_id || null; // Set user_id
        } else {
          formData.name = '';
          formData.description = '';
          formData.user_id = null; // Reset user_id
        }
      },
      { immediate: true }
    );

    const onCancel = () => {
        emit('cancel');
    }

    const handleSaveCharacter = async () => {
      formError.value = null;
      if (!formData.name.trim()) {
        formError.value = 'Character name is required.';
        return;
      }

      isSubmitting.value = true;
      try {
        let savedCharacter: Character;
        if (isEditing.value && props.characterToEdit) {
          const characterDataToUpdate: Partial<CharacterUpdate> = {};
          if (formData.name !== props.characterToEdit.name) characterDataToUpdate.name = formData.name;
          if (formData.description !== (props.characterToEdit.description || '')) characterDataToUpdate.description = formData.description;
          // Add user_id change if user is owner
          if (props.isOwner && formData.user_id !== (props.characterToEdit.user_id || null)) {
              // Cast to any to bypass strict type checking for user_id potentially not being in Partial<CharacterUpdate>
              (characterDataToUpdate as any).user_id = formData.user_id;
          }
          
          // Only call API if there are changes
          if (Object.keys(characterDataToUpdate).length > 0) {
            savedCharacter = await charactersApi.updateCharacter(props.characterToEdit.id, characterDataToUpdate as CharacterUpdate);
          } else {
            console.log("No changes detected for update.");
            emit('cancel'); 
            isSubmitting.value = false;
            return;
          }
        } else {
          const newCharacterData: CharacterCreate = {
            name: formData.name,
            description: formData.description,
            world_id: props.worldId,
            // user_id cannot be set on creation via this form (assignment happens later)
            // user_id: props.isOwner ? formData.user_id : null, // Or maybe allow setting on create?
          };
          savedCharacter = await charactersApi.createCharacter(newCharacterData);
          // If assignment is needed immediately after creation (and user is owner):
          if (props.isOwner && formData.user_id !== null) {
             try {
                await charactersApi.assignCharacterUser(savedCharacter.id, { user_id: formData.user_id });
                savedCharacter.user_id = formData.user_id; // Update local object
             } catch (assignErr) {
                console.error("Failed to assign user after creation:", assignErr);
                // Optionally inform the user about the assignment failure
             }
          }
        }
        emit('saved', savedCharacter);
      } catch (err: any) {
        formError.value = `Save failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Save Character Error:", err);
      } finally {
        isSubmitting.value = false;
      }
    };

    return {
      formData,
      isEditing,
      isSubmitting,
      formError,
      rules,
      assignableUserOptions,
      handleSaveCharacter,
      onCancel,
    };
  },
});
</script>

<style scoped>
/* Using Vuetify components, less custom styling might be needed */
.character-form {
  padding: 1rem;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem; /* Smaller label */
  color: #495057;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
/* Error message styling is handled by v-alert */
</style> 