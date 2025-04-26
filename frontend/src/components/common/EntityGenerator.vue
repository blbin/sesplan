<template>
  <v-card>
    <v-card-title>Generate New {{ entityTypeLabel }}</v-card-title>
    <v-card-text>
      <v-alert v-if="error" type="error" dense dismissible v-model="showError">
        {{ error }}
      </v-alert>

      <v-form @submit.prevent="generate" :disabled="isLoading">
        <v-select
          v-model="selectedExamples"
          :items="availableEntities"
          :label="`Select existing ${entityTypeLabel} examples`"
          :item-title="(item: any) => item.name || `Unnamed ${entityTypeLabel}`"
          item-value="id"
          multiple
          chips
          closable-chips
          :loading="loadingEntities"
          :rules="[(v: number[]) => (!!v && v.length > 0) || 'At least one example is required']"
          required
          class="mb-4"
        ></v-select>

        <v-textarea
          v-model="context"
          label="Optional Context"
          placeholder="Provide any additional context or specific requirements for the generation..."
          rows="3"
          class="mb-4"
        ></v-textarea>

        <v-btn
          type="submit"
          color="primary"
          :loading="isLoading"
          :disabled="isLoading || selectedExamples.length === 0"
        >
          Generate {{ entityTypeLabel }}
          <template v-slot:loader>
            <v-progress-circular indeterminate size="20"></v-progress-circular>
          </template>
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, type PropType } from 'vue';
import { aiService } from '@/services/api/aiService';

// Import API services for fetching examples
import * as characterService from '@/services/api/characters';
import * as locationService from '@/services/api/locations';
import * as organizationService from '@/services/api/organizations';
import * as itemService from '@/services/api/items';

const props = defineProps({
  worldId: {
    type: Number,
    required: true,
  },
  entityType: {
    type: String as PropType<'character' | 'location' | 'organization' | 'item'>,
    required: true,
  },
});

// Emit event when an entity is successfully generated
const emit = defineEmits<{
  (e: 'entity-generated', entity: any): void;
}>();

// Component state
const selectedExamples = ref<number[]>([]); // Store IDs of selected examples
const context = ref<string | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);
const showError = ref(false);
const loadingEntities = ref(false); // To show loading in v-select
const availableEntities = ref<any[]>([]); // Store entities fetched from Pinia

// --- Load Available Entities via API ---

const getApiServiceForEntityType = () => {
  switch (props.entityType) {
    case 'character': return characterService;
    case 'location': return locationService;
    case 'organization': return organizationService;
    case 'item': return itemService;
    default:
      console.error(`[EntityGenerator] No API service found for entity type: ${props.entityType}`);
      return null;
  }
};

const loadAvailableEntities = async () => {
  loadingEntities.value = true;
  error.value = null; // Reset error on load
  showError.value = false;
  availableEntities.value = []; // Clear previous examples

  const apiService = getApiServiceForEntityType();
  if (!apiService) {
    error.value = `Configuration error: Cannot load examples for ${props.entityType}.`;
    showError.value = true;
    loadingEntities.value = false;
    return;
  }

  try {
    let entities: any[] = [];
    // Assume each service has a method like get<Entities>ByWorld
    // Adjust method names if they are different
    if (typeof (apiService as any).getCharactersByWorld === 'function' && props.entityType === 'character') {
        entities = await (apiService as any).getCharactersByWorld(props.worldId);
    } else if (typeof (apiService as any).getLocationsByWorld === 'function' && props.entityType === 'location') {
        entities = await (apiService as any).getLocationsByWorld(props.worldId);
    } else if (typeof (apiService as any).getOrganizationsByWorld === 'function' && props.entityType === 'organization') {
        entities = await (apiService as any).getOrganizationsByWorld(props.worldId);
    } else if (typeof (apiService as any).getItemsByWorld === 'function' && props.entityType === 'item') {
        entities = await (apiService as any).getItemsByWorld(props.worldId);
    } else {
        console.warn(`[EntityGenerator] Could not find appropriate fetch method in service for ${props.entityType}`);
        throw new Error(`No method found to fetch ${props.entityType} examples.`);
    }

    // Filter out potentially unnamed entities or ensure they have an id and name
    availableEntities.value = entities.filter((e: any) => e && typeof e.id !== 'undefined' && typeof e.name === 'string' && e.name.trim() !== '');
    console.log(`[EntityGenerator] Loaded ${availableEntities.value.length} ${props.entityType} examples via API.`);

  } catch (err: any) {
    console.error(`[EntityGenerator] Failed to load entities via API for ${props.entityType}:`, err);
    error.value = `Failed to load existing ${props.entityType} examples: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    showError.value = true;
    availableEntities.value = [];
  } finally {
    loadingEntities.value = false;
  }
};

// Watch for changes in entityType or worldId to reload examples
watch(() => [props.entityType, props.worldId], loadAvailableEntities, { immediate: true });

// --- Generation Logic (Remove Pinia interaction) ---

const generate = async () => {
  if (selectedExamples.value.length === 0) {
    error.value = 'Please select at least one example entity.';
    showError.value = true;
    return;
  }

  isLoading.value = true;
  error.value = null;
  showError.value = false;

  try {
    // Find the full example objects based on selected IDs
    const exampleEntitiesData = availableEntities.value.filter(entity =>
        selectedExamples.value.includes(entity.id)
    ).map(entity => ({
        id: entity.id,
        name: entity.name,
        description: entity.description
    }));

    const payload = {
      existing_entities: exampleEntitiesData,
      context: context.value,
    };

    const newEntity = await aiService.generateEntity(
      props.worldId,
      props.entityType,
      payload
    );

    console.log(`[EntityGenerator] Successfully generated ${props.entityType}:`, newEntity);

    emit('entity-generated', newEntity); // Emit event for parent component

    // Optionally reset form or provide success feedback
    selectedExamples.value = [];
    context.value = null;

  } catch (err: any) {
    console.error(`[EntityGenerator] Generation failed for ${props.entityType}:`, err);
    error.value = err.response?.data?.detail || err.message || `An unknown error occurred during ${props.entityType} generation.`;
    showError.value = true;
  } finally {
    isLoading.value = false;
  }
};

// Computed property for display label
const entityTypeLabel = computed(() => {
  // Capitalize first letter for display
  return props.entityType.charAt(0).toUpperCase() + props.entityType.slice(1);
});

</script>

<style scoped>
/* Add any specific styles here if needed */
</style> 