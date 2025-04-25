<template>
  <form @submit.prevent="handleSaveCharacter" class="character-form">
    <h3>{{ isEditing ? 'Edit Character' : 'Add New Character' }}</h3>

    <!-- World Selection (only for creating) -->
    <div v-if="!isEditing" class="form-group">
      <label for="characterWorld">World *</label>
      <select id="characterWorld" v-model="formData.world_id" required class="form-control">
        <option disabled :value="null">Please select a world</option>
        <option v-for="world in availableWorlds" :key="world.id" :value="world.id">
          {{ world.name }}
        </option>
      </select>
      <p v-if="!availableWorlds || availableWorlds.length === 0" class="info-message">
        <!-- Provide info or loading state if needed -->
        No worlds available or loading...
      </p>
    </div>

    <div class="form-group">
      <label for="characterName">Name *</label>
      <input 
        type="text" 
        id="characterName" 
        v-model="formData.name" 
        required 
        class="form-control"
      >
    </div>
    <div class="form-group">
      <label for="characterDescription">Description</label>
      <textarea 
        id="characterDescription" 
        v-model="formData.description"
        class="form-control"
        rows="4"
      ></textarea>
    </div>

    <div v-if="formError" class="error-message">
      {{ formError }}
    </div>

    <div class="form-actions">
      <button type="button" @click="onCancel" class="btn btn-secondary">Cancel</button>
      <button 
        type="submit" 
        class="btn btn-primary" 
        :disabled="isSubmitting || (!isEditing && !formData.world_id) || !formData.name.trim()"
       >
        {{ isSubmitting ? 'Saving...' : (isEditing ? 'Save Changes' : 'Create Character') }}
      </button>
    </div>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, watch, computed } from 'vue';
import type { PropType } from 'vue';
import * as charactersApi from '@/services/api/characters';
import type { Character, CharacterCreate, CharacterUpdate } from '@/types/character';
import type { World } from '@/types/world';

interface CharacterFormData {
  name: string;
  description: string | null;
  world_id: number | null; // Only for creating
}

export default defineComponent({
  name: 'CreateCharacterForm',
  props: {
    // worldId is only needed when creating a new character outside a specific world context
    worldId: {
      type: Number,
      default: null, // Make it optional
    },
    characterToEdit: {
      type: Object as PropType<Character | null>,
      default: null,
    },
    // Pass available worlds for selection when creating
    availableWorlds: {
        type: Array as PropType<World[]>,
        default: () => [],
    },
  },
  emits: ['saved', 'cancel'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const formError = ref<string | null>(null);

    const formData = reactive<CharacterFormData>({
      name: '',
      description: null,
      world_id: props.worldId, // Pre-fill if worldId prop is provided
    });

    const isEditing = computed(() => !!props.characterToEdit);

    // Initialize form when characterToEdit changes (for editing)
    watch(
      () => props.characterToEdit,
      (character) => {
        if (character) {
          formData.name = character.name;
          formData.description = character.description;
          formData.world_id = character.world_id; // Store world_id for context if needed, but not changeable
        } else {
          // Reset form for creation, potentially pre-filling worldId from prop
          formData.name = '';
          formData.description = null;
          formData.world_id = props.worldId;
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
          // Update
          const characterDataToUpdate: CharacterUpdate = {};
          if (formData.name !== props.characterToEdit.name) {
            characterDataToUpdate.name = formData.name;
          }
          if (formData.description !== props.characterToEdit.description) {
            characterDataToUpdate.description = formData.description;
          }

          if (Object.keys(characterDataToUpdate).length > 0) {
            savedCharacter = await charactersApi.updateCharacter(props.characterToEdit.id, characterDataToUpdate);
          } else {
            // No changes detected, emit original character data or just cancel?
            // Emitting saved with original data might be unexpected if nothing changed.
            // Let's emit cancel in this case or just do nothing.
            console.log("No changes detected for update.");
            emit('cancel'); // Emit cancel if no changes
            isSubmitting.value = false;
            return;
          }
        } else {
          // Create
          if (!formData.world_id) {
            formError.value = 'Please select a world.';
            isSubmitting.value = false;
            return;
          }
          const newCharacterData: CharacterCreate = {
            name: formData.name,
            description: formData.description,
            world_id: formData.world_id,
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
      handleSaveCharacter,
      onCancel,
    };
  },
});
</script>

<style scoped>
/* Basic form styling, adapt as needed */
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
}
.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  box-sizing: border-box;
}
textarea.form-control {
  min-height: 80px;
  resize: vertical;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}
.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 0.8rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
  margin-top: 1rem;
}
.info-message {
    font-size: 0.9rem;
    color: #6c757d;
    margin-top: 0.5rem;
}

/* Re-use button styles if defined globally or copy from another component */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0069d9;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style> 