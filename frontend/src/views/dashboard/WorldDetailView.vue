<template>
  <div class="world-detail-view">
    <!-- Use WorldDetailHeader - Pass worldId as a Ref -->
    <!-- Check if worldIdRef has a value before rendering header that depends on it -->
    <WorldDetailHeader v-if="worldIdRef" :world-id="worldIdRef" />

    <!-- Error state for world details (handled by composable) -->
    <div v-if="worldError" class="error-message">
      <p>{{ worldError }}</p>
      <router-link :to="{ name: 'Worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>

    <!-- Loading State - Show a simple loader while the main world data is fetching -->
     <div v-else-if="worldLoading" class="loading-message">
       <v-progress-circular indeterminate color="primary"></v-progress-circular>
       <p class="mt-4">Loading world...</p>
            </div>

    <!-- Content when world is loaded (or loading has finished, even if error occurred in sub-components) -->
    <div v-else class="world-content">

      <!-- Tabs for sections -->
      <v-tabs v-model="currentTab" background-color="transparent" color="primary" grow>
        <v-tab value="details">Details</v-tab>
        <v-tab value="characters">Characters</v-tab>
        <v-tab value="locations">Locations</v-tab>
        <v-tab value="organizations">Organizations</v-tab>
        <v-tab value="items">Items</v-tab>
      </v-tabs>

      <v-window v-model="currentTab">
        <!-- Details Tab Content -->
        <v-window-item value="details" eager> <!-- eager ensures composable is active -->
          <WorldDetailsTab v-if="worldIdRef" :world-id="worldIdRef" />
        </v-window-item>

        <!-- Characters Tab Content -->
        <v-window-item value="characters" eager>
          <WorldEntityTable
            ref="characterTableRef" 
            v-if="worldIdRef && isCurrentUserOwner !== undefined"
            :world-id="worldIdRef"
            entity-type="character"
            title="Characters"
            :headers="characterHeaders"
            :is-current-user-owner="isCurrentUserOwner"
            :fetch-tag-types="true"
            @add="openCharacterFormModal(null)"
            @edit="openCharacterFormModal"
            @delete="requestCharacterDelete"
            @generateAI="openAIGenerator('character')"
            @rowClick="handleCharacterRowClick"
            @update:assignableUsers="(users) => currentAssignableUsers = users"
          />
        </v-window-item>

        <!-- Locations Tab Content -->
        <v-window-item value="locations" eager>
          <WorldEntityTable
            ref="locationTableRef"
            v-if="worldIdRef && isCurrentUserOwner !== undefined"
            :world-id="worldIdRef"
            entity-type="location"
            title="Locations"
            :headers="locationHeaders"
            :is-current-user-owner="isCurrentUserOwner"
            :fetch-tag-types="true"
            @add="openAddLocationModal"
            @edit="openEditLocationModal"
            @delete="requestLocationDelete"
            @generateAI="openAIGenerator('location')"
            @rowClick="handleLocationRowClick"
           >
             <template v-slot:item.parent_location_id="{ item }">
              <router-link 
                v-if="item.parent_location_id && getParentLocationName(item.parent_location_id)" 
                :to="{ name: 'LocationDetail', params: { locationId: item.parent_location_id } }" 
                class="text-decoration-none"
                @click.stop 
              >
                {{ getParentLocationName(item.parent_location_id) }}
              </router-link>
            </template>
            </WorldEntityTable>
        </v-window-item>

        <!-- Organizations Tab Content -->
        <v-window-item value="organizations" eager>
          <WorldEntityTable
            ref="organizationTableRef"
            v-if="worldIdRef && isCurrentUserOwner !== undefined"
            :world-id="worldIdRef"
            entity-type="organization"
            title="Organizations"
             :headers="organizationHeaders"
            :is-current-user-owner="isCurrentUserOwner"
            :fetch-tag-types="true"
            @add="openAddOrganizationModal"
            @edit="openEditOrganizationModal"
            @delete="requestOrganizationDelete"
            @generateAI="openAIGenerator('organization')"
            @rowClick="handleOrganizationRowClick"
          >
             <template v-slot:item.parent_organization_id="{ item }">
              <router-link 
                v-if="item.parent_organization_id && getParentOrganizationName(item.parent_organization_id)" 
                :to="{ name: 'OrganizationDetail', params: { organizationId: item.parent_organization_id } }" 
                class="text-decoration-none"
                @click.stop
              >
                {{ getParentOrganizationName(item.parent_organization_id) }}
               </router-link>
            </template>
            </WorldEntityTable>
        </v-window-item>

        <!-- Items Tab Content -->
        <v-window-item value="items" eager>
           <WorldEntityTable
             ref="itemTableRef"
            v-if="worldIdRef && isCurrentUserOwner !== undefined"
            :world-id="worldIdRef"
            entity-type="item"
            title="Items"
             :headers="itemHeaders"
            :is-current-user-owner="isCurrentUserOwner"
            :fetch-tag-types="true"
            @add="openAddItemModal"
            @edit="openEditItemModal"
            @delete="requestItemDelete"
            @generateAI="openAIGenerator('item')"
            @rowClick="handleItemRowClick"
          >
              <template v-slot:item.location_id="{ item }">
                {{ getItemLocationName(item.location_id || null) }}
              </template>
              <template v-slot:item.character_id="{ item }">
                {{ getItemCharacterName(item.character_id || null) }}
              </template>
            </WorldEntityTable>
        </v-window-item>
      </v-window>

      <!-- MODALS -->
      <v-dialog v-model="showLocationForm" max-width="600px">
         <v-card class="position-relative">
           <v-card-title>
             <span class="text-h5">{{ locationToEdit ? 'Edit Location' : 'Add New Location' }}</span>
             <v-btn 
               icon="mdi-close" 
               variant="text" 
               @click="closeLocationModal"
               style="position: absolute; top: 8px; right: 8px; z-index: 1;"
             ></v-btn>
           </v-card-title>
           <v-card-text>
          <CreateLocationForm
               v-if="numericWorldId && showLocationForm"
            :worldId="numericWorldId"
               :locations="allLocations"
            :locationToEdit="locationToEdit"
            @saved="handleLocationSaved"
            @cancel="closeLocationModal"
          />
           </v-card-text>
         </v-card>
       </v-dialog>

      <v-dialog v-model="showOrganizationForm" max-width="600px">
         <v-card class="position-relative">
           <v-card-title>
             <span class="text-h5">{{ organizationToEdit ? 'Edit Organization' : 'Add New Organization' }}</span>
             <v-btn 
               icon="mdi-close" 
               variant="text" 
               @click="closeOrganizationModal"
               style="position: absolute; top: 8px; right: 8px; z-index: 1;"
             ></v-btn>
            </v-card-title>
           <v-card-text>
          <CreateOrganizationForm
               v-if="numericWorldId && showOrganizationForm"
            :worldId="numericWorldId"
               :organizations="allOrganizations"
            :organizationToEdit="organizationToEdit"
            @saved="handleOrganizationSaved"
            @cancel="closeOrganizationModal"
          />
           </v-card-text>
         </v-card>
       </v-dialog>

      <v-dialog v-model="showItemForm" max-width="600px">
         <v-card class="position-relative">
            <v-card-title>
              <span class="text-h5">{{ itemToEdit ? 'Edit Item' : 'Add New Item' }}</span>
              <v-btn 
                icon="mdi-close" 
                variant="text" 
                @click="closeItemModal"
                style="position: absolute; top: 8px; right: 8px; z-index: 1;"
              ></v-btn>
            </v-card-title>
           <v-card-text>
          <CreateItemForm
               v-if="numericWorldId && showItemForm"
            :worldId="numericWorldId"
               :characters="allCharacters"
               :locations="allLocations"
            :itemToEdit="itemToEdit"
            :availableTagTypes="itemTagTypes"
            @saved="handleItemSaved"
            @cancel="closeItemModal"
          />
           </v-card-text>
         </v-card>
       </v-dialog>

      <v-dialog v-model="showCharacterForm" max-width="600px">
         <v-card class="position-relative">
            <v-card-title>
              <span class="text-h5">{{ characterToEdit ? 'Edit Character' : 'Add New Character' }}</span>
              <v-btn 
                icon="mdi-close" 
                variant="text" 
                @click="closeCharacterModal"
                style="position: absolute; top: 8px; right: 8px; z-index: 1;"
              ></v-btn>
            </v-card-title>
           <v-card-text>
          <CreateCharacterForm
               v-if="numericWorldId && showCharacterForm"
               :worldId="numericWorldId"
               :characterToEdit="characterToEdit" 
               :availableTagTypes="characterTagTypes"
               :is-owner="isCurrentUserOwner"
               :assignable-users="currentAssignableUsers"
               @saved="handleCharacterSaved"
               @cancel="closeCharacterModal"
          />
           </v-card-text>
         </v-card>
       </v-dialog>

      <v-dialog v-model="showAIGeneratorDialog" max-width="700px" persistent>
        <v-card class="position-relative">
          <v-card-title class="text-h5 d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-robot</v-icon>
             Generate {{ aiEntityTypeLabel }} with AI
             <v-btn 
               icon="mdi-close" 
               variant="text" 
               @click="closeAIGenerator" 
               :disabled="isGenerating"
               style="position: absolute; top: 8px; right: 8px; z-index: 1;"
             ></v-btn>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pt-4">
             <v-alert v-if="generationError" type="error" variant="tonal" closable @click:close="generationError = null" class="mb-4">
                {{ generationError }}
              </v-alert>
            <div v-if="!isGenerating && !generationComplete">
               <p class="mb-4 text-body-1">Optionally select existing {{ aiEntityTypeLabel.toLowerCase() }}s as examples for style and content inspiration.</p>
              <v-select
                v-model="selectedExampleIds"
                :items="availableExamples"
                item-title="name"
                item-value="id"
                 :label="`Select ${aiEntityTypeLabel.toLowerCase()} examples (Optional)`"
                 multiple chips closable-chips
                 clearable
                :loading="loadingExamples"
                 class="mb-4"
              ></v-select>
              <v-textarea
                v-model="generationContext"
                label="Additional Context (Optional)"
                 placeholder="Provide specific requirements..."
                 rows="3" class="mb-4" hide-details
              ></v-textarea>
            </div>
            <div v-if="isGenerating" class="py-8 text-center">
              <v-progress-circular indeterminate size="64" color="primary" class="mb-4"></v-progress-circular>
               <p class="text-body-1">Generating new {{ aiEntityTypeLabel.toLowerCase() }}...</p>
              <p class="text-caption">This may take a few moments</p>
            </div>
             <div v-if="generationComplete && generatedEntity" class="py-4">
               <v-alert type="success" variant="tonal" class="mb-4">{{ aiEntityTypeLabel }} successfully generated!</v-alert>
              <v-card variant="outlined" class="mb-4">
                 <v-card-title>{{ generatedEntity.name || 'Unnamed Entity' }}</v-card-title>
                <v-card-text>
                   <p v-html="renderMarkdownPreview(generatedEntity.description || 'No description available.')"></p>
                </v-card-text>
              </v-card>
               <v-btn 
                color="primary"
                 variant="outlined"
                 prepend-icon="mdi-eye-outline"
                 @click="goToDetailView(generatedEntity, aiEntityType)"
                class="mr-2"
               >View Details</v-btn>
            </div>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
             <v-btn variant="text" :disabled="isGenerating" @click="closeAIGenerator">{{ generationComplete ? 'Close' : 'Cancel' }}</v-btn>
             <v-btn v-if="!isGenerating && !generationComplete" color="primary" @click="generateEntity">Generate</v-btn>
             <v-btn v-if="generationComplete" color="primary" @click="generateAnother">Generate Another</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="showDeleteConfirm" max-width="500px">
         <v-card class="position-relative">
           <v-card-title>
             <span class="text-h5">Confirm Deletion</span>
             <v-btn 
               icon="mdi-close" 
               variant="text" 
               @click="cancelDelete" 
               :disabled="isDeleting"
               style="position: absolute; top: 8px; right: 8px; z-index: 1;"
             ></v-btn>
           </v-card-title>
           <v-card-text>
             Are you sure you want to delete this {{ itemTypeToDelete }}?
             <strong v-if="itemToDelete">{{ itemToDelete.name }}</strong>
             <v-alert v-if="deleteError" type="error" variant="tonal" class="mt-3">{{ deleteError }}</v-alert>
           </v-card-text>
           <v-card-actions>
             <v-spacer></v-spacer>
             <v-btn variant="text" @click="cancelDelete" :disabled="isDeleting">Cancel</v-btn>
             <v-btn color="error" @click="executeDelete" :loading="isDeleting">Delete</v-btn>
           </v-card-actions>
         </v-card>
       </v-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Import Composables
import { useWorldDetail } from '@/composables/useWorldDetail';
import { useEntityManagement } from '@/composables/useEntityManagement';
import type { EntityType } from '@/composables/useEntityManagement';
import * as aiApi from '@/services/api/aiService';

// Import Components
import WorldDetailHeader from '@/components/dashboard/worlds/WorldDetailHeader.vue';
import WorldDetailsTab from '@/components/dashboard/worlds/WorldDetailsTab.vue';
import WorldEntityTable from '@/components/dashboard/worlds/WorldEntityTable.vue';
import CreateLocationForm from '@/components/worlds/CreateLocationForm.vue';
import CreateOrganizationForm from '@/components/dashboard/worlds/CreateOrganizationForm.vue';
import CreateItemForm from '@/components/worlds/CreateItemForm.vue';
import CreateCharacterForm from '@/components/dashboard/CreateCharacterForm.vue';

// Import Types
import type { Character } from '@/types/character';
import type { Location } from '@/types/location';
import type { Organization } from '@/types/organization';
import type { Item } from '@/types/item';
import type { ItemTagType } from '@/types/itemTagType';
import type { CharacterTagType } from '@/types/characterTagType';
import type { UserSimple } from '@/services/api/worlds';

// Import Vuetify components
import {
  VTabs, VTab, VWindow, VWindowItem, VDialog, VCard, VCardTitle, VCardText,
  VCardActions, VIcon, VDivider, VSelect, VTextarea, VProgressCircular,
  VAlert, VSpacer, VBtn, // Explicitly list Vuetify components used in this template
} from 'vuetify/components';

const route = useRoute();
const router = useRouter();

// --- World ID ---
const worldIdRef = computed(() => route.params.worldId as string | undefined);
const numericWorldId = computed(() => {
  const id = Number(worldIdRef.value);
  return !isNaN(id) && id > 0 ? id : null;
});

// --- World Detail Composable ---
const { worldError, worldLoading, isCurrentUserOwner, renderMarkdownPreview } = useWorldDetail(worldIdRef);

// --- Current Tab State ---
const currentTab = ref('details');
const validTabs = ['details', 'characters', 'locations', 'organizations', 'items'];

// --- Template Refs for Tables ---
const characterTableRef = ref<InstanceType<typeof WorldEntityTable> | null>(null);
const locationTableRef = ref<InstanceType<typeof WorldEntityTable> | null>(null);
const organizationTableRef = ref<InstanceType<typeof WorldEntityTable> | null>(null);
const itemTableRef = ref<InstanceType<typeof WorldEntityTable> | null>(null);

// Sledování změny záložky a aktualizace URL
watch(currentTab, (newTab) => {
  router.replace({ query: { ...route.query, tab: newTab } });
});

// Nastavení počáteční záložky z URL při načtení
onMounted(() => {
  const tabFromUrl = route.query.tab as string;
  if (tabFromUrl && validTabs.includes(tabFromUrl)) {
    currentTab.value = tabFromUrl;
  }
});

// --- Entity Management Composables (for unfiltered lists and specific tags) ---
const { allItems: allCharacters, tagTypes: characterTagTypes } = useEntityManagement<Character, CharacterTagType>(worldIdRef, 'character', true);
const { allItems: allLocations } = useEntityManagement<Location, any>(worldIdRef, 'location');
const { allItems: allOrganizations } = useEntityManagement<Organization, any>(worldIdRef, 'organization');
const { allItems: allItems, tagTypes: itemTagTypes } = useEntityManagement<Item, ItemTagType>(worldIdRef, 'item', true);

// --- Table Headers ---
const characterHeaders = ref([
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  // Removed Created At - can be added back if needed
  { title: 'Tags', key: 'tags', sortable: false },
]);
const locationHeaders = ref([
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Parent', key: 'parent_location_id', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Tags', key: 'tags', sortable: false },
]);
const organizationHeaders = ref([
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Parent', key: 'parent_organization_id', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Tags', key: 'tags', sortable: false },
]);
const itemHeaders = ref([
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Location', key: 'location_id', sortable: true },
  { title: 'Owner', key: 'character_id', sortable: true },
  { title: 'Tags', key: 'tags', sortable: false },
]);

// --- Modal States ---
    const showLocationForm = ref(false);
    const locationToEdit = ref<Location | null>(null);
const showOrganizationForm = ref(false);
    const organizationToEdit = ref<Organization | null>(null);
const showItemForm = ref(false);
    const itemToEdit = ref<Item | null>(null);
const showCharacterForm = ref(false);
const characterToEdit = ref<Character | null>(null);

// --- Delete Confirmation State ---
const showDeleteConfirm = ref(false);
const itemToDelete = ref<Location | Organization | Item | Character | null>(null);
const itemTypeToDelete = ref<EntityType | null>(null);
const isDeleting = ref(false);
const deleteError = ref<string | null>(null);

// --- AI Generator State ---
    const showAIGeneratorDialog = ref(false);
const aiEntityType = ref<EntityType>('character');
    const isGenerating = ref(false);
    const generationError = ref<string | null>(null);
    const generationComplete = ref(false);
    const selectedExampleIds = ref<number[]>([]);
    const generationContext = ref<string | null>(null);
    const generatedEntity = ref<any | null>(null);
    const availableExamples = ref<any[]>([]);
    const loadingExamples = ref(false);

// --- Assignable Users State ---
const currentAssignableUsers = ref<UserSimple[]>([]);

// --- Modal Control & Save Handlers ---
const openAddLocationModal = () => { locationToEdit.value = null; showLocationForm.value = true; };
const openEditLocationModal = (loc: Location) => { locationToEdit.value = { ...loc }; showLocationForm.value = true; };
const closeLocationModal = () => { showLocationForm.value = false; locationToEdit.value = null; };
const handleLocationSaved = () => { closeLocationModal(); locationTableRef.value?.refreshData(); };

const openAddOrganizationModal = () => { organizationToEdit.value = null; showOrganizationForm.value = true; };
const openEditOrganizationModal = (org: Organization) => { organizationToEdit.value = { ...org }; showOrganizationForm.value = true; };
const closeOrganizationModal = () => { showOrganizationForm.value = false; organizationToEdit.value = null; };
const handleOrganizationSaved = () => { closeOrganizationModal(); organizationTableRef.value?.refreshData(); };

const openAddItemModal = () => { itemToEdit.value = null; showItemForm.value = true; };
const openEditItemModal = (item: Item) => { itemToEdit.value = { ...item }; showItemForm.value = true; };
const closeItemModal = () => { showItemForm.value = false; itemToEdit.value = null; };
const handleItemSaved = () => { closeItemModal(); itemTableRef.value?.refreshData(); };

const openCharacterFormModal = (character: Character | null = null) => {
  console.log("Opening character form for:", character);
  characterToEdit.value = character; 
  showCharacterForm.value = true;
};

const closeCharacterModal = () => {
  showCharacterForm.value = false;
  characterToEdit.value = null;
};

const handleCharacterSaved = (savedCharacter: Character) => {
  console.log('Character saved:', savedCharacter);
  closeCharacterModal();
  characterTableRef.value?.refreshData();
};

// --- Delete ---
const requestDelete = (item: any, type: EntityType) => {
  itemToDelete.value = item;
  itemTypeToDelete.value = type;
  deleteError.value = null;
  showDeleteConfirm.value = true;
};
const requestCharacterDelete = (character: Character) => requestDelete(character, 'character');
const requestLocationDelete = (item: Location) => requestDelete(item, 'location');
const requestOrganizationDelete = (item: Organization) => requestDelete(item, 'organization');
const requestItemDelete = (item: Item) => requestDelete(item, 'item');

const cancelDelete = () => {
  showDeleteConfirm.value = false;
  itemToDelete.value = null;
  itemTypeToDelete.value = null;
};

// Get the correct table ref based on type - UPDATED HELPER
const getTableRefForType = (type: EntityType | null) => {
    if (!type) return null;
    switch (type) {
        case 'character': return characterTableRef;
        case 'location': return locationTableRef;
        case 'organization': return organizationTableRef;
        case 'item': return itemTableRef;
        default: return null;
    }
};

// Získání správné instance composable pro deleteItem
// (Potřebujeme je pro přístup k deleteItem a deleteError)
const entityComposables = {
  character: useEntityManagement<Character, CharacterTagType>(worldIdRef, 'character'),
  location: useEntityManagement<Location, any>(worldIdRef, 'location'),
  organization: useEntityManagement<Organization, any>(worldIdRef, 'organization'),
  item: useEntityManagement<Item, ItemTagType>(worldIdRef, 'item')
};

const executeDelete = async () => {
  if (!itemToDelete.value || !itemTypeToDelete.value) return;
  isDeleting.value = true;
  deleteError.value = null;
  const id = itemToDelete.value.id;
  const type = itemTypeToDelete.value;
  const tableRef = getTableRefForType(type);
  const composableInstance = entityComposables[type]; // Získání správné instance

  if (!composableInstance) {
      deleteError.value = `Internal error: Cannot find composable for type ${type}`;
      isDeleting.value = false;
      return;
  }

  try {
    // Volání deleteItem z příslušné instance composable
    await composableInstance.deleteItem(id); 
    // Počkáme na dokončení smazání a pak refreshujeme PŘES REF tabulky
    tableRef?.value?.refreshData(); 
    cancelDelete();
  } catch (err: any) { 
    console.error(`[WorldDetailView] Delete ${type} error:`, err);
    // Získání chyby z composable instance
    deleteError.value = composableInstance.deleteError.value || `Failed to delete ${type}: ${err.message || 'Unknown error'}`;
  } finally {
    isDeleting.value = false;
  }
};

// --- AI Generator ---
const aiEntityTypeLabel = computed(() => aiEntityType.value.charAt(0).toUpperCase() + aiEntityType.value.slice(1));

const openAIGenerator = (type: EntityType) => {
  aiEntityType.value = type;
      selectedExampleIds.value = [];
      generationContext.value = null;
      generationError.value = null;
      isGenerating.value = false;
      generationComplete.value = false;
      generatedEntity.value = null;
      loadingExamples.value = true;
  availableExamples.value = [];
      
      try {
        switch (type) {
      case 'character': availableExamples.value = allCharacters.value; break;
      case 'location': availableExamples.value = allLocations.value; break;
      case 'organization': availableExamples.value = allOrganizations.value; break;
      case 'item': availableExamples.value = allItems.value; break;
    }
      } catch (err: any) {
        generationError.value = `Failed to load examples: ${err.message}`;
      } finally {
    loadingExamples.value = false;
      }
      showAIGeneratorDialog.value = true;
    };

const closeAIGenerator = () => showAIGeneratorDialog.value = false;

    const generateEntity = async () => {
      if (!numericWorldId.value) return;
      isGenerating.value = true;
      generationError.value = null;
      const tableRef = getTableRefForType(aiEntityType.value);
  try {
        // Správné sestavení payloadu - příklady se pošlou jen pokud jsou vybrané
        const selectedExamples = selectedExampleIds.value.length > 0 
            ? availableExamples.value
                .filter(entity => selectedExampleIds.value.includes(entity.id))
                .map(entity => ({ id: entity.id, name: entity.name, description: entity.description }))
            : []; // Prázdné pole, pokud nejsou vybrány žádné příklady
    const payload = { existing_entities: selectedExamples, context: generationContext.value };

    const newEntity = await aiApi.aiService.generateEntity(numericWorldId.value, aiEntityType.value, payload);
        generatedEntity.value = newEntity;
        generationComplete.value = true;
        // Zavoláme refresh na referenci tabulky PO úspěšném generování
    tableRef?.value?.refreshData(); 
      } catch (err: any) {
    generationError.value = err.response?.data?.detail || err.message || "Generation error";
      } finally {
        isGenerating.value = false;
      }
    };
    
    const generateAnother = () => {
      generationComplete.value = false;
      generatedEntity.value = null;
};

// --- Navigation ---
const goToDetailView = (item: any, type: EntityType) => {
  let routeName = '';
  let params = {};
        switch (type) {
    case 'character': routeName = 'CharacterDetail'; params = { worldId: numericWorldId.value, characterId: item.id }; break;
    case 'location': routeName = 'LocationDetail'; params = { worldId: numericWorldId.value, locationId: item.id }; break;
    case 'organization': routeName = 'OrganizationDetail'; params = { worldId: numericWorldId.value, organizationId: item.id }; break;
    case 'item': routeName = 'ItemDetail'; params = { worldId: numericWorldId.value, itemId: item.id }; break;
  }
  if (routeName && numericWorldId.value) { 
    // Přidání aktuální záložky jako query parametr
    router.push({ name: routeName, params, query: { fromTab: currentTab.value } }); 
  }
};
const handleCharacterRowClick = (character: Character) => goToDetailView(character, 'character');
const handleLocationRowClick = (item: Location) => goToDetailView(item, 'location');
const handleOrganizationRowClick = (item: Organization) => goToDetailView(item, 'organization');
const handleItemRowClick = (item: Item) => goToDetailView(item, 'item');

// --- Slot Helpers (using unfiltered lists) ---
    const getParentLocationName = (parentId: number | null): string => {
  if (!parentId) return '';
  const parent = allLocations.value.find(loc => loc.id === parentId);
      return parent ? parent.name : `Unknown (ID: ${parentId})`;
    };
     const getParentOrganizationName = (parentId: number | null): string => {
  if (!parentId) return '';
  const parent = allOrganizations.value.find(org => org.id === parentId);
      return parent ? parent.name : `Unknown (ID: ${parentId})`;
    };
    const getItemLocationName = (locationId: number | null): string => {
      if (!locationId) return 'Not specified';
  const location = allLocations.value.find(loc => loc.id === locationId);
      return location ? location.name : `Unknown (ID: ${locationId})`;
    };
    const getItemCharacterName = (characterId: number | null): string => {
      if (!characterId) return 'Unassigned';
  const character = allCharacters.value.find(char => char.id === characterId);
      return character ? character.name : `Unknown (ID: ${characterId})`;
    };

</script>

<style scoped>
/* Styles are largely unchanged, but some might be redundant now */
.world-detail-view {
  padding: 1rem 2rem;
}

.loading-message { /* Style for the main loading indicator */
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 0.25rem;
  margin: 1rem 0; /* Added margin */
}

.error-message p {
    margin-bottom: 1rem;
}

.world-content {
  background-color: #fff;
  padding: 1.5rem 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-top: 1rem;
}

.v-tabs {
  margin-bottom: 1rem;
}

.v-window-item {
  padding-top: 1rem;
}

/* Simplified button style for router-link */
.btn-secondary {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  cursor: pointer;
  border: none;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
  transition: background-color 0.2s ease;
  background-color: #6c757d;
  color: white;
  margin-top: 1rem; /* Add space when shown in error message */
}
.btn-secondary:hover {
  background-color: #5a6268;
}

/* Ensure dialogs work well */
:deep(.v-dialog .v-overlay__content) {
    width: auto !important;
    margin: 24px; /* Add some margin */
}

@media (max-width: 768px) {
  .world-detail-view {
    padding: 1rem;
  }
  .world-content {
    padding: 1rem;
  }
}
</style> 