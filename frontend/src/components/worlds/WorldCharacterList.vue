<template>
  <section class="characters-section detail-section">
    <!-- Remove the internal section header -->
    <!-- 
    <div class="section-header">
      <h2>Characters</h2>
      <button v-if="canManage" @click="$emit('open-add-character')" class="btn btn-primary btn-sm">Add Character</button>
    </div>
     -->
    
    <p v-if="charactersLoading" class="loading-state">Loading characters...</p>
    <p v-else-if="charactersError" class="error-message">{{ charactersError }}</p>
    <p v-else-if="characters.length === 0" class="empty-state">No characters found in this world.</p>
    <ul v-else class="entity-list">
      <li v-for="character in characters" :key="character.id" class="entity-list-item">
         <div class="entity-info">
           <router-link :to="{ name: 'CharacterDetail', params: { characterId: character.id } }" class="entity-name-link">
             <span class="entity-name">{{ character.name }}</span>
           </router-link>
           <!-- Display Assigned User -->
           <span v-if="character.user_id" class="assigned-user-info">
             Assigned to: {{ getUserDisplayName(character.user_id) }}
           </span>
           <span v-else class="assigned-user-info text-muted">
             Not assigned
           </span>
           <div class="entity-details">
              <div 
                v-if="character.description"
                class="entity-description-preview" 
                v-html="renderDescriptionPreview(character.description)"
              ></div>
              <span v-else class="entity-description-preview text-muted"><em>No description</em></span>
              <!-- Add tags or other info if available -->
              <span class="entity-date">Created: {{ formatDate(character.created_at) }}</span>
            </div>
         </div>
         <!-- User Assignment Select (only for world owner) -->
         <div v-if="isOwner" class="entity-actions">
             <v-select
                 v-model="character.user_id"
                 :items="assignableUserOptions"
                 :loading="assignableUsersLoading || assignmentLoading[character.id]"
                 :disabled="assignableUsersLoading || assignmentLoading[character.id]"
                 @update:modelValue="(newUserId) => handleAssignUser(character.id, newUserId)"
                 label="Assign User"
                 item-title="username"
                 item-value="id"
                 density="compact"
                 clearable
                 hide-details
                 style="min-width: 200px;"
             ></v-select>
              <v-progress-circular
                  v-if="assignmentLoading[character.id]"
                  indeterminate
                  size="20"
                  class="ml-2"
              ></v-progress-circular>
         </div>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, toRefs, computed, reactive } from 'vue';
import * as charactersApi from '@/services/api/characters';
import * as worldsApi from '@/services/api/worlds'; // Import worlds API
import type { Character } from '@/types/character';
import type { UserSimple } from '@/services/api/worlds'; // Import UserSimple type
import MarkdownIt from 'markdown-it'; // Import markdown-it
import { formatDate } from '@/utils/dateFormatter'; // Import formatDate
// Import Vuetify components if not globally registered
// import { VSelect, VProgressCircular } from 'vuetify/components'; // Example

const props = defineProps<{
  worldId: number | string;
  isOwner: boolean; // Add prop to indicate if the current user is the world owner
}>();

const { worldId, isOwner } = toRefs(props);

const characters = ref<Character[]>([]);
const charactersLoading = ref(false);
const charactersError = ref<string | undefined>(undefined);

// State for assignable users
const assignableUsers = ref<UserSimple[]>([]);
const assignableUsersLoading = ref(false);
const assignableUsersError = ref<string | undefined>(undefined);

// State for assignment loading indicator per character
const assignmentLoading = reactive<Record<number, boolean>>({});

// Initialize markdown-it instance
const md = new MarkdownIt({ html: false, linkify: true });

// Method to render description preview
const renderDescriptionPreview = (markdown: string | null): string => {
  if (!markdown) {
    return '';
  }
  const maxLength = 100;
  let truncatedMd = markdown.length > maxLength 
    ? markdown.substring(0, maxLength) + '...' 
    : markdown;
  return md.render(truncatedMd);
};

// Fetch characters for the world
const fetchWorldCharacters = async (id: number | string) => {
    const numericWorldId = Number(id);
    if (isNaN(numericWorldId)) {
        charactersError.value = "Invalid World ID provided.";
        return;
    }
    charactersLoading.value = true;
    charactersError.value = undefined;
    characters.value = [];
    try {
        // Use getAllWorldCharacters which should return characters with user_id
        characters.value = await charactersApi.getAllWorldCharacters(numericWorldId);
    } catch (err: any) {
        console.error("Fetch World Characters Error:", err);
        charactersError.value = `Failed to load characters: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    } finally {
        charactersLoading.value = false;
    }
};

// Fetch users assignable to characters in this world
const fetchAssignableUsers = async (id: number | string) => {
    const numericWorldId = Number(id);
    if (isNaN(numericWorldId)) {
        assignableUsersError.value = "Invalid World ID.";
        return;
    }
    assignableUsersLoading.value = true;
    assignableUsersError.value = undefined;
    assignableUsers.value = [];
    try {
        assignableUsers.value = await worldsApi.getCampaignUsersInWorld(numericWorldId);
    } catch (err: any) {
        console.error("Fetch Assignable Users Error:", err);
        assignableUsersError.value = `Failed to load users for assignment: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        // Optionally show a user-friendly message in the UI
    } finally {
        assignableUsersLoading.value = false;
    }
};

// Computed property for v-select items, adding an "Unassigned" option
const assignableUserOptions = computed(() => {
    // Format users for v-select
    const users = assignableUsers.value.map((user: UserSimple) => ({
        id: user.id,
        username: user.username // Use username for display
    }));
    // Add an explicit "Unassigned" option represented by null
    // v-select with 'clearable' handles the null value automatically
    return users;
});

// Method to get display name for assigned user
const getUserDisplayName = (userId: number | null): string => {
    if (userId === null) return 'Not assigned';
    const user = assignableUsers.value.find((u: UserSimple) => u.id === userId);
    return user ? user.username : `User ID: ${userId}`; // Fallback if user not found in list
};

// Method to handle user assignment via v-select change
const handleAssignUser = async (characterId: number, newUserId: number | null) => {
    console.log(`Assigning user ${newUserId} to character ${characterId}`);
    assignmentLoading[characterId] = true;
    try {
        const payload = { user_id: newUserId };
        const updatedCharacter = await charactersApi.assignCharacterUser(characterId, payload);

        // Update local character data
        const index = characters.value.findIndex(c => c.id === characterId);
        if (index !== -1) {
            characters.value[index].user_id = updatedCharacter.user_id;
            // Optionally refresh other character data if needed:
            // characters.value[index] = { ...characters.value[index], ...updatedCharacter };
        }
        // TODO: Add user feedback (e.g., snackbar message)
        console.log(`Successfully assigned user ${newUserId} to character ${characterId}`);

    } catch (err: any) {
        console.error("Assign User Error:", err);
        // Revert the v-select value if the API call failed
        const index = characters.value.findIndex(c => c.id === characterId);
        if (index !== -1) {
            // Force re-render or find a way to revert v-model if necessary
             // Note: Directly mutating character.user_id might be reverted by v-model,
             // consider refreshing the specific character data or the whole list.
             // For now, logging the error. User might need to manually retry.
             console.error("Failed to update UI after assignment error.");
        }
        // TODO: Add user feedback (e.g., snackbar message)
         alert(`Error assigning user: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
    } finally {
        assignmentLoading[characterId] = false;
    }
};

// Watch for worldId changes to load characters and assignable users
watch(
  worldId,
  (newId) => {
    if (newId) {
      fetchWorldCharacters(newId);
      if (isOwner.value) { // Fetch assignable users only if the current user is the owner
          fetchAssignableUsers(newId);
      } else {
          // Clear assignable users if not owner
          assignableUsers.value = [];
          assignableUsersError.value = undefined;
      }
    } else {
      characters.value = [];
      charactersError.value = "No world selected.";
      charactersLoading.value = false;
      assignableUsers.value = [];
      assignableUsersError.value = undefined;
      assignableUsersLoading.value = false;
    }
  },
  { immediate: true } // Load data immediately when the component mounts
);

</script>

<style scoped>
/* Adopt styles from WorldLocationList, potentially using more generic class names */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.detail-section h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.entity-list {
  list-style: none;
  padding: 0;
  margin: 0;
  border: 1px solid #e9ecef;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
}

.entity-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center; /* Align items vertically center */
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e9ecef;
}

.entity-list-item:last-child {
    border-bottom: none;
}

.entity-info {
  /* Adjust flex properties if needed */
  flex-grow: 1; /* Allow info to take available space */
  margin-right: 1rem; /* Space between info and actions */
}

.entity-name-link {
    text-decoration: none;
    color: var(--v-theme-primary, #7851a9); /* Use primary theme color */
    font-weight: 600;
    cursor: pointer;
    display: inline-block; /* Needed for margin */
    margin-bottom: 0.25rem; /* Space below name */
}

.entity-name-link:hover .entity-name {
    text-decoration: underline;
}

.entity-name {
  font-size: 1.1rem;
}

.entity-details {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.9rem;
  color: #6c757d;
}

.entity-description-preview {
  line-height: 1.4;
}

.entity-description-preview :deep(p) {
    margin: 0;
    display: inline;
}

.entity-date {
  font-size: 0.8rem;
  color: #adb5bd;
  margin-top: 0.25rem;
}

.text-muted {
    color: #6c757d;
    font-style: italic;
}

.loading-state,
.error-message,
.empty-state {
  padding: 1rem; /* Adjusted padding */
  text-align: center; /* Center align messages */
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #dee2e6; /* Use dashed border for distinction */
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.error-message {
  color: #dc3545; 
  border-color: #f5c6cb;
  background-color: #f8d7da;
}

/* Placeholder for actions if needed later */
/*
.entity-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
*/

/* Ensure button styles are consistent if not globally defined */
.btn {
  /* Basic button resets or styles */
  display: inline-block;
  font-weight: 400;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  border: 1px solid transparent;
  padding: 0.375rem 0.75rem;
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
  color: #fff;
  background-color: #0069d9;
  border-color: #0062cc;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;
  border-radius: 0.2rem;
}

.assigned-user-info {
    font-size: 0.85rem;
    color: #6c757d; /* Use muted color */
    margin-top: 0.2rem; /* Add some space below the name */
    display: block; /* Ensure it takes its own line if needed */
}

.entity-actions {
  display: flex;
  align-items: center; /* Center items vertically */
  gap: 0.5rem;
  flex-shrink: 0; /* Prevent actions from shrinking */
}
</style> 