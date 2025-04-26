<template>
  <div class="world-detail-view">
    <!-- Loading state for world details -->
    <div v-if="worldLoading" class="loading-message">Loading world details...</div>
    <!-- Error state for world details -->
    <div v-else-if="worldError" class="error-message">
      <p>{{ worldError }}</p>
      <router-link :to="{ name: 'Worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>
    <!-- Content when world details are loaded -->
    <div v-else-if="world" class="world-content">
      <header class="view-header">
        <h1>{{ world.name }}</h1>
        <router-link :to="{ name: 'Worlds' }" class="btn btn-secondary">Back to List</router-link>
      </header>

      <div class="details-section">
        <h2>World Details</h2>
        <div class="description-content" v-html="renderedDescription"></div>
        <p><strong>Public:</strong> {{ world.is_public ? 'Yes' : 'No' }}</p>
        <p><strong>Created:</strong> {{ formatDate(world.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDate(world.updated_at) }}</p>
      </div>

      <!-- Tabs for sections -->
      <v-tabs v-model="currentTab" background-color="transparent" color="primary" grow>
        <v-tab value="characters">Characters</v-tab>
        <v-tab value="locations">Locations</v-tab>
        <v-tab value="organizations">Organizations</v-tab>
        <v-tab value="items">Items</v-tab>
      </v-tabs>

      <v-window v-model="currentTab">
        <v-window-item value="characters">
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="text-h5">Characters in this World</h2>
            <v-btn 
              color="primary" 
              variant="outlined" 
              prepend-icon="mdi-robot"
              @click="openAIGenerator('character')"
              :disabled="worldLoading"
              size="small"
            >
              Generate with AI
            </v-btn>
          </div>
          <WorldCharacterList v-if="numericWorldId" :world-id="numericWorldId" />
        </v-window-item>

        <v-window-item value="locations">
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="text-h5">Locations in this World</h2>
            <v-btn 
              color="primary" 
              variant="outlined" 
              prepend-icon="mdi-robot"
              @click="openAIGenerator('location')"
              :disabled="worldLoading || locationsLoading"
              size="small"
            >
              Generate with AI
            </v-btn>
          </div>
          <WorldLocationList
            v-if="numericWorldId && !locationsLoading && isCurrentUserOwner"
            :locations="locations"
            :worldId="numericWorldId"
            :canManage="isCurrentUserOwner"
            :loading="locationsLoading"
            :error="locationsError"
            @locations-updated="handleLocationsUpdated"
            @open-add-location="openAddLocationModal"
            @edit-location="openEditLocationModal"
          />
        </v-window-item>

        <v-window-item value="organizations">
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="text-h5">Organizations in this World</h2>
            <v-btn 
              color="primary" 
              variant="outlined" 
              prepend-icon="mdi-robot"
              @click="openAIGenerator('organization')"
              :disabled="worldLoading || organizationsLoading"
              size="small"
            >
              Generate with AI
            </v-btn>
          </div>
          <WorldOrganizationList
            v-if="numericWorldId && !organizationsLoading && isCurrentUserOwner"
            :organizations="organizations"
            :worldId="numericWorldId"
            :canManage="isCurrentUserOwner"
            :loading="organizationsLoading"
            :error="organizationsError"
            @organizations-updated="handleOrganizationsUpdated"
            @open-add-organization="openAddOrganizationModal"
            @edit-organization="openEditOrganizationModal"
          />
        </v-window-item>

        <v-window-item value="items">
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="text-h5">Items in this World</h2>
            <v-btn 
              color="primary" 
              variant="outlined" 
              prepend-icon="mdi-robot"
              @click="openAIGenerator('item')"
              :disabled="worldLoading || itemsLoading"
              size="small"
            >
              Generate with AI
            </v-btn>
          </div>
          <WorldItemList
            v-if="numericWorldId && !itemsLoading && isCurrentUserOwner"
            :items="items"
            :characters="[]"  
            :locations="locations"
            :worldId="numericWorldId"
            :canManage="isCurrentUserOwner"
            :loading="itemsLoading"
            :error="itemsError"
            @items-updated="handleItemsUpdated"
            @open-add-item="openAddItemModal"
            @edit-item="openEditItemModal"
          />
        </v-window-item>
      </v-window>

      <!-- Add/Edit Location Form Modal -->
      <div v-if="showLocationForm" class="modal-overlay">
        <div class="modal-content">
          <CreateLocationForm
            v-if="numericWorldId" 
            :worldId="numericWorldId"
            :locations="locations" 
            :locationToEdit="locationToEdit"
            @saved="handleLocationSaved"
            @cancel="closeLocationModal"
          />
        </div>
      </div>

      <!-- Add/Edit Organization Form Modal -->
      <div v-if="showOrganizationForm" class="modal-overlay">
        <div class="modal-content">
          <CreateOrganizationForm
            v-if="numericWorldId"
            :worldId="numericWorldId"
            :organizations="organizations"
            :organizationToEdit="organizationToEdit"
            @saved="handleOrganizationSaved"
            @cancel="closeOrganizationModal"
          />
        </div>
      </div>

      <!-- Add/Edit Item Form Modal -->
      <div v-if="showItemForm" class="modal-overlay">
        <div class="modal-content">
          <CreateItemForm
            v-if="numericWorldId" 
            :worldId="numericWorldId"
            :characters="[]" 
            :locations="locations"
            :itemToEdit="itemToEdit"
            :availableTagTypes="itemTagTypes"
            @saved="handleItemSaved"
            @cancel="closeItemModal"
          />
        </div>
      </div>

      <!-- AI Generator Dialog - Improved Design -->
      <v-dialog v-model="showAIGeneratorDialog" max-width="700px" persistent>
        <v-card>
          <v-card-title class="text-h5 d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-robot</v-icon>
            Generate {{ entityTypeLabel }} with AI
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text class="pt-4">
            <div v-if="generationError" class="mb-4">
              <v-alert type="error" variant="tonal" closable>
                {{ generationError }}
              </v-alert>
            </div>
            
            <div v-if="!isGenerating && !generationComplete">
              <p class="mb-4 text-body-1">
                Select existing {{ entityTypeLabel.toLowerCase() }}s as examples to influence the AI generation.
                The AI will create a new {{ entityTypeLabel.toLowerCase() }} with similar characteristics.
              </p>
              
              <v-select
                v-model="selectedExampleIds"
                :items="availableExamples"
                item-title="name"
                item-value="id"
                :label="`Select ${entityTypeLabel.toLowerCase()} examples`"
                multiple
                chips
                closable-chips
                :loading="loadingExamples"
                :rules="[(v: any) => (!!v && v.length > 0) || 'At least one example is required']"
                required
                class="mb-4"
              ></v-select>
              
              <v-textarea
                v-model="generationContext"
                label="Additional Context (Optional)"
                placeholder="Provide any specific requirements or context for the generation..."
                rows="3"
                class="mb-4"
                hide-details
              ></v-textarea>
            </div>
            
            <div v-if="isGenerating" class="py-8 text-center">
              <v-progress-circular indeterminate size="64" color="primary" class="mb-4"></v-progress-circular>
              <p class="text-body-1">Generating new {{ entityTypeLabel.toLowerCase() }}...</p>
              <p class="text-caption">This may take a few moments</p>
            </div>
            
            <div v-if="generationComplete" class="py-4">
              <v-alert type="success" variant="tonal" class="mb-4">
                {{ entityTypeLabel }} successfully generated!
              </v-alert>
              
              <v-card variant="outlined" class="mb-4">
                <v-card-title>{{ generatedEntity?.name || 'Unnamed Entity' }}</v-card-title>
                <v-card-text>
                  <p>{{ generatedEntity?.description || 'No description available.' }}</p>
                </v-card-text>
              </v-card>
            </div>
          </v-card-text>
          
          <v-divider></v-divider>
          
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn 
              variant="text" 
              :disabled="isGenerating"
              @click="closeAIGenerator"
            >
              {{ generationComplete ? 'Close' : 'Cancel' }}
            </v-btn>
            <v-btn
              v-if="!isGenerating && !generationComplete"
              color="primary"
              :disabled="selectedExampleIds.length === 0"
              @click="generateEntity"
            >
              Generate
            </v-btn>
            <v-btn
              v-if="generationComplete"
              color="primary"
              @click="generateAnother"
            >
              Generate Another
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

    </div>
    <!-- Fallback if world somehow wasn't found after loading -->
    <div v-else>
      <p>World not found.</p>
      <router-link :to="{ name: 'Worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue';
import * as worldsApi from '@/services/api/worlds';
import * as locationsApi from '@/services/api/locations';
import * as organizationsApi from '@/services/api/organizations';
import * as itemsApi from '@/services/api/items';
import * as itemTagTypeApi from '@/services/api/itemTagTypeService';
import * as characterApi from '@/services/api/characters';
import * as aiApi from '@/services/api/aiService';
import type { World } from '@/types/world';
import type { Location } from '@/types/location';
import type { Organization } from '@/types/organization';
import type { Item } from '@/types/item';
import type { ItemTagType } from '@/types/itemTagType';
import WorldCharacterList from '@/components/worlds/WorldCharacterList.vue';
import WorldLocationList from '@/components/worlds/WorldLocationList.vue';
import CreateLocationForm from '@/components/worlds/CreateLocationForm.vue';
import WorldOrganizationList from '@/components/dashboard/worlds/WorldOrganizationList.vue';
import CreateOrganizationForm from '@/components/dashboard/worlds/CreateOrganizationForm.vue';
import WorldItemList from '@/components/worlds/WorldItemList.vue';
import CreateItemForm from '@/components/worlds/CreateItemForm.vue';
import { formatDateTime, formatDate } from '@/utils/dateFormatter';
import MarkdownIt from 'markdown-it';

export default defineComponent({
  name: 'WorldDetailView',
  components: {
    WorldCharacterList,
    WorldLocationList,
    CreateLocationForm,
    WorldOrganizationList,
    CreateOrganizationForm,
    WorldItemList,
    CreateItemForm,
  },
  props: {
    worldId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const world = ref<World | null>(null);
    const locations = ref<Location[]>([]);
    const organizations = ref<Organization[]>([]);
    const items = ref<Item[]>([]);
    const itemTagTypes = ref<ItemTagType[]>([]);
    const worldLoading = ref(true);
    const locationsLoading = ref(false);
    const organizationsLoading = ref(false);
    const itemsLoading = ref(false);
    const itemTagTypesLoading = ref(false);
    const itemTagTypesError = ref<string | undefined>(undefined);
    const worldError = ref<string | undefined>(undefined);
    const locationsError = ref<string | undefined>(undefined);
    const organizationsError = ref<string | undefined>(undefined);
    const itemsError = ref<string | undefined>(undefined);
    const showLocationForm = ref(false);
    const showOrganizationForm = ref(false);
    const showItemForm = ref(false);
    const locationToEdit = ref<Location | null>(null);
    const organizationToEdit = ref<Organization | null>(null);
    const itemToEdit = ref<Item | null>(null);
    const currentTab = ref('locations');

    // --- AI Generator State - IMPROVED ---
    const showAIGeneratorDialog = ref(false);
    const entityType = ref<'character' | 'location' | 'organization' | 'item'>('character');
    const isGenerating = ref(false);
    const generationError = ref<string | null>(null);
    const generationComplete = ref(false);
    const selectedExampleIds = ref<number[]>([]);
    const generationContext = ref<string | null>(null);
    const generatedEntity = ref<any | null>(null);
    const availableExamples = ref<any[]>([]);
    const loadingExamples = ref(false);
    const loadingCharacterExamples = ref(false);

    const isCurrentUserOwner = computed(() => {
        return world.value !== null && !worldLoading.value && worldError.value === undefined;
    });

    const entityTypeLabel = computed(() => {
      // Capitalize first letter
      return entityType.value.charAt(0).toUpperCase() + entityType.value.slice(1);
    });

    // Initialize markdown-it
    const md = new MarkdownIt({
      html: false, // Basic security - don't render arbitrary HTML from markdown
      linkify: true, // Auto-detect links
      typographer: true, // Enable nice typography
    });

    // Computed property for rendering description
    const renderedDescription = computed(() => {
      if (world.value?.description) {
        return md.render(world.value.description);
      }
      return '<p><em>No description provided.</em></p>'; // Default message if no description
    });

    // Computed property for numeric world ID
    const numericWorldId = computed(() => {
      const id = Number(props.worldId);
      return !isNaN(id) && id > 0 ? id : null; // Return null if ID is invalid or not positive
    });

    // --- World Data Fetching Functions ---
    const fetchWorldDetails = async (id: number | string) => {
      const numericId = Number(id);
      if (isNaN(numericId)) {
        console.error("Invalid World ID:", id);
        worldError.value = "Invalid World ID provided.";
        worldLoading.value = false;
        return;
      }

      console.log(`Fetching details for world ID: ${numericId}`); // Add log
      worldLoading.value = true;
      worldError.value = undefined;
      // Reset states *before* fetching
      world.value = null;
      locations.value = [];
      organizations.value = [];
      items.value = [];
      itemTagTypes.value = [];
      locationsError.value = undefined;
      organizationsError.value = undefined;
      itemsError.value = undefined;
      itemTagTypesError.value = undefined;
      // Keep individual loading flags false initially, they will be set by their respective functions
      locationsLoading.value = false;
      organizationsLoading.value = false;
      itemsLoading.value = false;
      itemTagTypesLoading.value = false;


      try {
        console.log("Fetching main world data..."); // Add log
        const fetchedWorld = await worldsApi.getWorldById(numericId);
        console.log("Main world data fetched:", fetchedWorld); // Add log
        world.value = fetchedWorld;

        // Fetch related data concurrently and wait for all
        console.log("Initiating fetches for related data..."); // Add log
        await Promise.all([
          fetchWorldLocations(numericId),
          fetchWorldOrganizations(numericId),
          fetchWorldItems(numericId),
          fetchItemTagTypes(numericId)
        ]);
        console.log("All related data fetches completed or failed individually."); // Add log

      } catch (err: any) {
        console.error("Fetch World Error:", err);
        // Keep the existing error handling for world fetch
        if (err.response?.status === 404) {
          worldError.value = 'World not found.';
        } else if (err.response?.status === 403) {
          worldError.value = 'You do not have permission to view this world.';
        } else {
          worldError.value = `Failed to load world details: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
         // If the main world fetch fails, we might not want to proceed further.
         // The individual error handlers in fetchWorldLocations etc. should handle their specific errors if they were initiated.
      } finally {
        console.log("Setting worldLoading to false."); // Add log
        worldLoading.value = false; // Set loading to false only after all fetches are done or main fetch failed.
      }
    };

    const fetchWorldLocations = async (id: number) => {
      locationsLoading.value = true;
      locationsError.value = undefined;
      locations.value = [];
      try {
        locations.value = await locationsApi.getLocationsByWorld(id);
      } catch (err: any) {
        console.error("Fetch World Locations Error:", err);
        if (err.response?.status === 403) {
          locationsError.value = 'You do not have permission to view locations in this world.';
        } else {
          locationsError.value = `Failed to load locations: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
      } finally {
        locationsLoading.value = false;
      }
    };

    const fetchWorldOrganizations = async (id: number) => {
      organizationsLoading.value = true;
      organizationsError.value = undefined;
      organizations.value = [];
      try {
        organizations.value = await organizationsApi.getOrganizationsByWorld(id);
      } catch (err: any) {
        console.error("Fetch World Organizations Error:", err);
        if (err.response?.status === 403) {
          organizationsError.value = 'You do not have permission to view organizations in this world.';
        } else {
          organizationsError.value = `Failed to load organizations: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
      } finally {
        organizationsLoading.value = false;
      }
    };

    const fetchWorldItems = async (id: number) => {
      itemsLoading.value = true;
      itemsError.value = undefined;
      items.value = [];
      try {
        items.value = await itemsApi.getItemsByWorld(id);
      } catch (err: any) {
        console.error("Fetch World Items Error:", err);
        if (err.response?.status === 403) {
          itemsError.value = 'You do not have permission to view items in this world.';
        } else {
          itemsError.value = `Failed to load items: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
      } finally {
        itemsLoading.value = false;
      }
    };

    const fetchWorldCharacters = async (id: number) => {
      try {
        return await characterApi.getAllWorldCharacters(id);
      } catch (err: any) {
        console.error("Fetch World Characters Error:", err);
        throw err;
      }
    };

    const fetchItemTagTypes = async (id: number) => {
      itemTagTypesLoading.value = true;
      itemTagTypesError.value = undefined;
      itemTagTypes.value = [];
      try {
        itemTagTypes.value = await itemTagTypeApi.getItemTagTypes(id);
      } catch (err: any) {
        console.error("Fetch Item Tag Types Error:", err);
        itemTagTypesError.value = `Failed to load item tag types: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
      } finally {
        itemTagTypesLoading.value = false;
      }
    };

    // --- Event Handlers ---
    const handleLocationsUpdated = () => {
      if (world.value) {
        fetchWorldLocations(world.value.id);
      }
    };

    const handleOrganizationsUpdated = () => {
      if (world.value) {
        fetchWorldOrganizations(world.value.id);
      }
    };

    const handleItemsUpdated = () => {
      if (world.value) {
        fetchWorldItems(world.value.id);
        fetchItemTagTypes(world.value.id);
      }
    };

    // --- Modal Form Handlers ---
    const openAddLocationModal = () => {
      locationToEdit.value = null;
      showLocationForm.value = true;
    };

    const openEditLocationModal = (location: Location) => {
      locationToEdit.value = { ...location };
      showLocationForm.value = true;
    };

    const handleLocationSaved = () => {
      closeLocationModal();
      handleLocationsUpdated();
    };

    const closeLocationModal = () => {
      showLocationForm.value = false;
      locationToEdit.value = null;
    };

    const openAddOrganizationModal = () => {
      organizationToEdit.value = null;
      showOrganizationForm.value = true;
    };

    const openEditOrganizationModal = (organization: Organization) => {
      organizationToEdit.value = { ...organization };
      showOrganizationForm.value = true;
    };

    const closeOrganizationModal = () => {
      showOrganizationForm.value = false;
      organizationToEdit.value = null;
    };

    const handleOrganizationSaved = () => {
      closeOrganizationModal();
      handleOrganizationsUpdated();
    };

    const openAddItemModal = () => {
      itemToEdit.value = null;
      showItemForm.value = true;
    };

    const openEditItemModal = (item: Item) => {
      itemToEdit.value = { ...item };
      showItemForm.value = true;
    };

    const closeItemModal = () => {
      showItemForm.value = false;
      itemToEdit.value = null;
    };

    const handleItemSaved = () => {
      closeItemModal();
      handleItemsUpdated();
    };

    // --- AI Generator Methods - IMPROVED ---
    const openAIGenerator = async (type: 'character' | 'location' | 'organization' | 'item') => {
      console.log(`Opening AI Generator for type: ${type}`);
      entityType.value = type;
      
      // Reset generator state
      selectedExampleIds.value = [];
      generationContext.value = null;
      generationError.value = null;
      isGenerating.value = false;
      generationComplete.value = false;
      generatedEntity.value = null;
      loadingExamples.value = true;
      loadingCharacterExamples.value = false; // Reset character loading flag
      availableExamples.value = []; // Clear previous examples
      
      // Load examples for this entity type
      try {
        switch (type) {
          case 'character':
            loadingCharacterExamples.value = true;
            availableExamples.value = await fetchWorldCharacters(Number(props.worldId));
            break;
          case 'location':
            if (!locationsLoading.value) {
              availableExamples.value = locations.value;
            } else {
              console.warn("Attempted to open AI generator for locations while locations are still loading.");
              // Optionally set an error message or just show empty examples / rely on loading state
              generationError.value = "Location data is still loading, please wait.";
            }
            break;
          case 'organization':
             if (!organizationsLoading.value) {
              availableExamples.value = organizations.value;
            } else {
              console.warn("Attempted to open AI generator for organizations while organizations are still loading.");
              generationError.value = "Organization data is still loading, please wait.";
            }
            break;
          case 'item':
             if (!itemsLoading.value) {
              availableExamples.value = items.value;
            } else {
              console.warn("Attempted to open AI generator for items while items are still loading.");
              generationError.value = "Item data is still loading, please wait.";
            }
            break;
        }
        console.log(`[AI Generator] Loaded ${availableExamples.value.length} examples for ${type}`);
      } catch (err: any) {
        console.error(`[AI Generator] Failed to load examples for ${type}:`, err);
        generationError.value = `Failed to load examples: ${err.message}`;
        availableExamples.value = [];
      } finally {
        loadingExamples.value = false; // General loading indicator
        loadingCharacterExamples.value = false; // Ensure character loading is false
      }
      
      // Show the dialog
      showAIGeneratorDialog.value = true;
    };

    const closeAIGenerator = () => {
      showAIGeneratorDialog.value = false;
    };

    const generateEntity = async () => {
      if (selectedExampleIds.value.length === 0) {
        generationError.value = 'Please select at least one example.';
        return;
      }

      isGenerating.value = true;
      generationError.value = null;
      
      try {
        // Find the full example objects based on selected IDs
        const selectedExamples = availableExamples.value.filter(entity => 
          selectedExampleIds.value.includes(entity.id)
        ).map(entity => ({
          id: entity.id,
          name: entity.name,
          description: entity.description
        }));
        
        const payload = {
          existing_entities: selectedExamples,
          context: generationContext.value
        };
        
        console.log(`[AI Generator] Generating ${entityType.value} with payload:`, payload);
        
        // Call AI service
        const newEntity = await aiApi.aiService.generateEntity(
          Number(props.worldId),
          entityType.value,
          payload
        );
        
        console.log(`[AI Generator] Successfully generated ${entityType.value}:`, newEntity);
        
        // Store generated entity
        generatedEntity.value = newEntity;
        generationComplete.value = true;
        
        // Refresh the appropriate list
        refreshEntityList();
        
      } catch (err: any) {
        console.error(`[AI Generator] Generation failed:`, err);
        generationError.value = err.response?.data?.detail || err.message || `An error occurred during generation.`;
      } finally {
        isGenerating.value = false;
      }
    };
    
    const generateAnother = () => {
      // Reset generation state but keep the dialog open and examples selected
      generationComplete.value = false;
      generatedEntity.value = null;
      // Keep selectedExampleIds and generationContext for convenience
    };
    
    const refreshEntityList = () => {
      // Refresh the appropriate entity list based on the generated entity type
      switch (entityType.value) {
        case 'character':
          // Character list is managed by WorldCharacterList component
          // We might need to emit an event or reload the page
          console.log('[AI Generator] Character list refresh needs implementation.');
          // Changing tab and back could refresh it
          const currentTabValue = currentTab.value;
          if (currentTabValue === 'characters') {
            currentTab.value = 'locations';
            setTimeout(() => {
              currentTab.value = 'characters';
            }, 10);
          }
          break;
        case 'location':
          fetchWorldLocations(Number(props.worldId));
          break;
        case 'organization':
          fetchWorldOrganizations(Number(props.worldId));
          break;
        case 'item':
          fetchWorldItems(Number(props.worldId));
          break;
      }
    };

    // --- Watchers and Lifecycle Hooks ---
    // Remove onMounted as the watcher with immediate: true handles the initial call
    /*
    onMounted(() => {
      if (props.worldId) {
        fetchWorldDetails(Number(props.worldId));
      } else {
        worldError.value = "World ID is missing.";
        worldLoading.value = false;
      }
    });
    */

    watch(
      () => props.worldId,
      (newId) => {
        if (newId !== undefined && newId !== null) { // Check for existence
           fetchWorldDetails(newId); // Pass String or Number
        } else {
            console.warn("worldId prop became null or undefined");
            worldError.value = "World ID is missing.";
            worldLoading.value = false;
            // Reset data when ID becomes invalid
            world.value = null;
            locations.value = [];
            organizations.value = [];
            items.value = [];
            itemTagTypes.value = [];
        }
      },
      { immediate: true } // immediate: true ensures it runs on mount
    );

    return {
      world,
      locations,
      organizations,
      items,
      itemTagTypes,
      worldLoading,
      locationsLoading,
      organizationsLoading,
      itemsLoading,
      itemTagTypesLoading,
      itemTagTypesError,
      worldError,
      locationsError,
      organizationsError,
      itemsError,
      showLocationForm,
      showOrganizationForm,
      showItemForm,
      locationToEdit,
      organizationToEdit,
      itemToEdit,
      currentTab,
      isCurrentUserOwner,
      formatDate,
      formatDateTime,
      handleLocationsUpdated,
      handleOrganizationsUpdated,
      handleItemsUpdated,
      openAddLocationModal,
      openEditLocationModal,
      closeLocationModal,
      handleLocationSaved,
      openAddOrganizationModal,
      openEditOrganizationModal,
      closeOrganizationModal,
      handleOrganizationSaved,
      openAddItemModal,
      openEditItemModal,
      closeItemModal,
      handleItemSaved,
      worldId: computed(() => props.worldId),
      
      // AI Generator related exports
      showAIGeneratorDialog,
      entityType,
      entityTypeLabel,
      isGenerating,
      generationError,
      generationComplete,
      selectedExampleIds,
      generationContext,
      generatedEntity,
      availableExamples,
      loadingExamples,
      loadingCharacterExamples,
      openAIGenerator,
      closeAIGenerator,
      generateEntity,
      generateAnother,
      renderedDescription,
      numericWorldId // Expose the computed numeric ID
    };
  },
});
</script>

<style scoped>
/* Base styles for the view */
.world-detail-view {
  padding: 2rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.view-header h1 {
  margin: 0;
  color: #343a40;
}

.world-content {
  background-color: #fff;
  padding: 1.5rem 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.details-section {
  margin-bottom: 2rem;
}

.details-section h2 {
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
  font-size: 1.2rem;
  color: #495057;
}

.details-section p {
  margin: 0.5rem 0;
  line-height: 1.6;
  color: #555;
}

.details-section p strong {
  margin-right: 0.5em;
  color: #333;
}

/* General Loading/Error/Button/Modal styles */
.loading-message,
.error-message,
.access-denied-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 0.25rem;
  margin-bottom: 1rem;
}

.error-message p {
    margin-bottom: 1rem;
}

.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  cursor: pointer;
  border: none;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  transition: background-color 0.2s ease;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}

/* Modal styling */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 1.5rem 2rem;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  max-height: 90vh; 
  overflow-y: auto;
}

/* Make tabs look nicer */
.v-tabs {
  margin-bottom: 1rem;
}

.v-window-item {
  padding-top: 1rem; /* Add some space below tabs */
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .view-header .btn {
    margin-top: 1rem;
  }
  .modal-content {
    width: 95%;
    padding: 1.5rem;
  }
}

/* Add styles for rendered markdown if needed */
.description-content :deep(p) {
  margin-bottom: 1em; /* Example styling for paragraphs */
}
.description-content :deep(a) {
  color: var(--v-theme-primary); /* Example link styling */
  text-decoration: none;
}
.description-content :deep(a:hover) {
  text-decoration: underline;
}
</style> 