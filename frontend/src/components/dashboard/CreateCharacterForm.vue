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
      <v-textarea 
        v-model="formData.description"
        variant="outlined"
        density="compact"
        rows="4"
        id="characterDescription"
      />
    </div>

    <!-- Tags Selection -->
    <div class="form-group">
      <label for="characterTags">Tags</label>
      <v-select
        id="characterTags"
        v-model="selectedTagTypeIds"
        :items="availableTagTypes"
        item-title="name"
        item-value="id"
        label="Select tags"
        multiple
        chips
        closable-chips
        variant="outlined"
        density="compact"
      ></v-select>
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
// Assume types will include tags eventually
import type { Character, CharacterCreate, CharacterUpdate } from '@/types/character';
import type { CharacterTagType } from '@/types/characterTagType'; // Corrected import path
// Import Vuetify components used
import { VTextField, VTextarea, VSelect, VBtn, VAlert } from 'vuetify/components';

interface CharacterFormData {
  name: string;
  description: string | null;
  // world_id is no longer part of the form data, it comes from the required prop
}

export default defineComponent({
  name: 'CreateCharacterForm',
  components: { VTextField, VTextarea, VSelect, VBtn, VAlert }, // Register Vuetify components
  props: {
    worldId: {
      type: Number,
      required: true, // worldId is now required as context is fixed
    },
    characterToEdit: {
      type: Object as PropType<Character | null>,
      default: null,
    },
    // Removed availableWorlds prop
    availableTagTypes: {
        type: Array as PropType<CharacterTagType[]>,
        default: () => [],
    },
  },
  emits: ['saved', 'cancel'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const formError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]); // For selected tag IDs

    // Basic required rule for Vuetify fields
    const rules = {
      required: (value: string) => !!value || 'This field is required.',
    };

    const formData = reactive<CharacterFormData>({
      name: '',
      description: null,
    });

    const isEditing = computed(() => !!props.characterToEdit);

    // Initialize form when characterToEdit changes (for editing)
    watch(
      () => props.characterToEdit,
      (character) => {
        if (character) {
          formData.name = character.name;
          formData.description = character.description;
          // Pre-fill selected tags if editing and character has tags
          selectedTagTypeIds.value = character.tags?.map(tag => tag.character_tag_type_id) || [];
        } else {
          // Reset form for creation
          formData.name = '';
          formData.description = null;
          selectedTagTypeIds.value = []; // Clear tags for new character
        }
      },
      { immediate: true, deep: true } // Use deep watch if character.tags is nested?
    );

    const onCancel = () => {
        emit('cancel');
    }

    const handleSaveCharacter = async () => {
      formError.value = null;
      if (!formData.name.trim()) {
        // Validation should be handled by Vuetify rules, but keep a fallback
        formError.value = 'Character name is required.';
        return;
      }

      isSubmitting.value = true;
      try {
        let savedCharacter: Character;
        if (isEditing.value && props.characterToEdit) {
          // Update - Include tags in the update payload
          const characterDataToUpdate: CharacterUpdate = {
             // Assuming CharacterUpdate schema accepts tag_type_ids
             // Only include fields if they changed
          };
          if (formData.name !== props.characterToEdit.name) characterDataToUpdate.name = formData.name;
          if (formData.description !== props.characterToEdit.description) characterDataToUpdate.description = formData.description;
          
          // Check if tags changed
          const originalTagIds = props.characterToEdit.tags?.map(t => t.character_tag_type_id).sort() || [];
          const currentTagIds = [...selectedTagTypeIds.value].sort();
          if (JSON.stringify(originalTagIds) !== JSON.stringify(currentTagIds)) {
              characterDataToUpdate.tag_type_ids = selectedTagTypeIds.value;
          }

          if (Object.keys(characterDataToUpdate).length > 0) {
            savedCharacter = await charactersApi.updateCharacter(props.characterToEdit.id, characterDataToUpdate);
          } else {
            console.log("No changes detected for update.");
            emit('cancel'); 
            isSubmitting.value = false;
            return;
          }
        } else {
          // Create - Include tags
          const newCharacterData: CharacterCreate = {
            name: formData.name,
            description: formData.description,
            world_id: props.worldId, // Use the required prop
            tag_type_ids: selectedTagTypeIds.value, // Add selected tag IDs
          };
          savedCharacter = await charactersApi.createCharacter(newCharacterData);
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
      selectedTagTypeIds,
      rules,
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