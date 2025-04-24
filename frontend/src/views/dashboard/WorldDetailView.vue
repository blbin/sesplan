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
        <p><strong>Description:</strong> {{ world.description || 'No description provided.' }}</p>
        <p><strong>Public:</strong> {{ world.is_public ? 'Yes' : 'No' }}</p>
        <p><strong>Created:</strong> {{ formatDate(world.created_at) }}</p>
        <p><strong>Last Updated:</strong> {{ formatDate(world.updated_at) }}</p>
      </div>

      <!-- Tabs for sections -->
      <v-tabs v-model="currentTab" background-color="transparent" color="primary" grow>
        <v-tab value="characters">Characters</v-tab>
        <v-tab value="locations">Locations</v-tab>
        <v-tab value="items">Items</v-tab>
      </v-tabs>

      <v-window v-model="currentTab">
        <v-window-item value="characters">
          <WorldCharacterList :world-id="Number(worldId)" />
        </v-window-item>

        <v-window-item value="locations">
          <WorldLocationList
            v-if="world && isCurrentUserOwner !== null"
            :locations="locations"
            :worldId="Number(worldId)"
            :canManage="isCurrentUserOwner"
            :loading="locationsLoading"
            :error="locationsError"
            @locations-updated="handleLocationsUpdated"
            @open-add-location="openAddLocationModal"
            @edit-location="openEditLocationModal"
          />
        </v-window-item>

        <v-window-item value="items">
          <WorldItemList
            v-if="world && isCurrentUserOwner !== null"
            :items="items"
            :characters="[]" 
            :locations="locations"
            :worldId="Number(worldId)"
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
            :worldId="Number(worldId)"
            :locations="locations" 
            :locationToEdit="locationToEdit"
            @saved="handleLocationSaved"
            @cancel="closeLocationModal"
          />
        </div>
      </div>

      <!-- Add/Edit Item Form Modal -->
      <div v-if="showItemForm" class="modal-overlay">
        <div class="modal-content">
          <CreateItemForm
            :worldId="Number(worldId)"
            :characters="[]" 
            :locations="locations"
            :itemToEdit="itemToEdit"
            @saved="handleItemSaved"
            @cancel="closeItemModal"
          />
        </div>
      </div>

    </div>
    <!-- Fallback if world somehow wasn't found after loading -->
    <div v-else>
      <p>World not found.</p>
      <router-link :to="{ name: 'Worlds' }" class="btn btn-secondary">Back to Worlds</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, computed } from 'vue';
import * as worldsApi from '@/services/api/worlds';
// import * as charactersApi from '@/services/api/characters'; // Removed
import * as locationsApi from '@/services/api/locations';
import * as itemsApi from '@/services/api/items';
import type { World } from '@/types/world';
// import type { Character } from '@/types/character'; // Removed
import type { Location } from '@/types/location';
import type { Item } from '@/types/item';
import WorldCharacterList from '@/components/worlds/WorldCharacterList.vue'; // Added
import WorldLocationList from '@/components/worlds/WorldLocationList.vue';
import CreateLocationForm from '@/components/worlds/CreateLocationForm.vue';
import WorldItemList from '@/components/worlds/WorldItemList.vue';
import CreateItemForm from '@/components/worlds/CreateItemForm.vue';
// import LocationTagTypeManager from '@/components/worlds/LocationTagTypeManager.vue';

export default defineComponent({
  name: 'WorldDetailView',
  components: {
    WorldCharacterList, // Added
    WorldLocationList,
    CreateLocationForm,
    WorldItemList,
    CreateItemForm,
    // Odebrána registrace LocationTagTypeManager
  },
  props: {
    worldId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const world = ref<World | null>(null);
    // const characters = ref<Character[]>([]); // Removed
    const locations = ref<Location[]>([]);
    const items = ref<Item[]>([]);
    const worldLoading = ref(true);
    // const charactersLoading = ref(false); // Removed
    const locationsLoading = ref(false);
    const itemsLoading = ref(false);
    const worldError = ref<string | undefined>(undefined);
    // const charactersError = ref<string | undefined>(undefined); // Removed
    const locationsError = ref<string | undefined>(undefined);
    const itemsError = ref<string | undefined>(undefined);
    const showLocationForm = ref(false);
    const showItemForm = ref(false);
    const locationToEdit = ref<Location | null>(null);
    const itemToEdit = ref<Item | null>(null);
    const currentTab = ref('characters');

    // Assuming only the world owner can manage locations/items for now
    const isCurrentUserOwner = computed(() => {
        // Placeholder: In a real app, this would check authStore.user.id against world.owner_id
        // For now, just return true if world is loaded successfully.
        // If the API returns 403, worldError will be set.
        return world.value !== null && !worldLoading.value && worldError.value === undefined;
    });

    const fetchWorldDetails = async (id: number) => {
      worldLoading.value = true;
      worldError.value = undefined;
      world.value = null;
      // characters.value = []; // Removed
      locations.value = [];
      items.value = [];
      // charactersError.value = undefined; // Removed
      locationsError.value = undefined;
      itemsError.value = undefined;
      // charactersLoading.value = false; // Removed
      locationsLoading.value = false;
      itemsLoading.value = false;

      try {
        world.value = await worldsApi.getWorldById(id);
        // fetchWorldCharacters(id); // Removed - Handled by WorldCharacterList
        fetchWorldLocations(id); // Keep for now, potential future refactor
        fetchWorldItems(id);     // Keep for now, potential future refactor
      } catch (err: any) {
        console.error("Fetch World Error:", err);
        if (err.response?.status === 404) {
          worldError.value = 'World not found.';
        } else if (err.response?.status === 403) {
          worldError.value = 'You do not have permission to view this world.';
        } else {
          worldError.value = `Failed to load world details: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
      } finally {
        worldLoading.value = false;
      }
    };

    // const fetchWorldCharacters = async (id: number) => { ... }; // Removed

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

    const handleLocationsUpdated = () => {
      if (world.value) {
        fetchWorldLocations(world.value.id);
      }
    };

    const handleItemsUpdated = () => {
      if (world.value) {
        fetchWorldItems(world.value.id);
      }
    };

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

    const openAddItemModal = () => {
      itemToEdit.value = null;
      showItemForm.value = true;
    };

    const openEditItemModal = (item: Item) => {
      itemToEdit.value = { ...item };
      showItemForm.value = true;
    };

    const handleItemSaved = () => {
      closeItemModal();
      handleItemsUpdated();
    };

    const closeItemModal = () => {
      showItemForm.value = false;
      itemToEdit.value = null;
    };

    const formatDate = (dateString: string | null | undefined): string => {
      if (!dateString) return 'N/A';
      try {
        // Using toLocaleDateString for just the date part
        return new Date(dateString).toLocaleDateString();
      } catch (e) {
        return String(dateString);
      }
    };

    onMounted(() => {
       if (props.worldId) {
           fetchWorldDetails(Number(props.worldId));
       } else {
           worldError.value = "World ID is missing.";
           worldLoading.value = false;
       }
    });

    watch(() => props.worldId, (newId, oldId) => {
      if (newId && newId !== oldId) {
        fetchWorldDetails(Number(newId));
      } else if (!newId) {
          // Handle case where worldId becomes null/undefined
          world.value = null;
          locations.value = [];
          items.value = [];
          worldError.value = "World ID is missing.";
          worldLoading.value = false;
      }
    });

    // Watch pro případ, že by výchozí tab byl 'tags', nastavíme jiný
    watch(currentTab, (newTab) => {
        if (newTab === 'tags') {
            currentTab.value = 'characters'; // Nebo jiný platný tab
        }
    });

    return {
      world,
      // characters, // Removed
      locations,
      items,
      worldLoading,
      // charactersLoading, // Removed
      locationsLoading,
      itemsLoading,
      worldError,
      // charactersError, // Removed
      locationsError,
      itemsError,
      showLocationForm,
      locationToEdit,
      showItemForm,
      itemToEdit,
      currentTab,
      isCurrentUserOwner,
      formatDate,
      handleLocationsUpdated,
      openAddLocationModal,
      openEditLocationModal,
      handleLocationSaved,
      closeLocationModal,
      handleItemsUpdated,
      openAddItemModal,
      openEditItemModal,
      handleItemSaved,
      closeItemModal,
      // Pass worldId explicitly if needed by template sections other than child components
      worldId: computed(() => props.worldId)
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

/* Styles for Character List Section Removed */

/* General Loading/Error/Button/Modal styles can remain or be moved to global styles */
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
  padding: 1.5rem 2rem; /* Slightly reduced padding */
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  /* Overflow handling might be needed if content is too long */
  max-height: 90vh; 
  overflow-y: auto;
}

/* Make tabs look a bit nicer */
.v-tabs {
  margin-bottom: 1.5rem;
}

.v-window-item {
  padding-top: 1rem; /* Add some space below tabs */
}
</style> 