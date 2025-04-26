import { ref, computed, watch } from 'vue';
import type { Ref } from 'vue';
import * as characterApi from '@/services/api/characters';
import * as locationApi from '@/services/api/locations';
import * as organizationApi from '@/services/api/organizations';
import * as itemApi from '@/services/api/items';
import * as characterTagTypeApi from '@/services/api/characterTagTypeService';
import * as locationTagTypeApi from '@/services/api/locationTagTypeService';
import * as organizationTagTypeApi from '@/services/api/organizationTagTypeService';
import * as itemTagTypeApi from '@/services/api/itemTagTypeService';

// Define types for entities and tags if they are not globally defined
// Re-using types from the original component for now
import type { Character } from '@/types/character';
import type { Location } from '@/types/location';
import type { Organization } from '@/types/organization';
import type { Item } from '@/types/item';
// Import only TagType, assuming tag associations are part of the main entity types
import type { CharacterTagType } from '@/types/characterTagType';
import type { LocationTagType } from '@/types/locationTagType';
import type { OrganizationTagType } from '@/types/organizationTagType';
import type { ItemTagType } from '@/types/itemTagType';

// Generic type for entity and tag management
type Entity = Character | Location | Organization | Item;
type TagType = CharacterTagType | LocationTagType | OrganizationTagType | ItemTagType;
// Removed generic Tag type as we will access tags directly from the entity

// Define a mapping for API calls based on entity type
const apiMap = {
  character: {
    getAll: characterApi.getAllWorldCharacters,
    delete: characterApi.deleteCharacter,
    getTagTypes: characterTagTypeApi.getCharacterTagTypes,
  },
  location: {
    getAll: locationApi.getLocationsByWorld,
    delete: locationApi.deleteLocation,
    getTagTypes: locationTagTypeApi.getLocationTagTypes,
  },
  organization: {
    getAll: organizationApi.getOrganizationsByWorld,
    delete: organizationApi.deleteOrganization,
    getTagTypes: organizationTagTypeApi.getOrganizationTagTypes,
  },
  item: {
    getAll: itemApi.getItemsByWorld,
    delete: itemApi.deleteItem,
    getTagTypes: itemTagTypeApi.getItemTagTypes,
  },
};

export type EntityType = keyof typeof apiMap;

// Adjusting generic constraints as we don't need a separate Tag generic type anymore
export function useEntityManagement<E extends Entity, TT extends TagType>(
  worldIdProp: Ref<string | number | undefined>,
  entityType: EntityType,
  fetchTagTypesFlag: boolean = false // Add flag to control tag type fetching
) {
  const items = ref<E[]>([]) as Ref<E[]>;
  const tagTypes = ref<TT[]>([]) as Ref<TT[]>;
  const loading = ref(false);
  const error = ref<string | undefined>(undefined);
  const tagTypesLoading = ref(false);
  const tagTypesError = ref<string | undefined>(undefined);
  const isDeleting = ref(false);
  const deleteError = ref<string | null>(null);

  // Search and Filter state
  const search = ref('');
  const selectedTagIds = ref<number[]>([]);

  const numericWorldId = computed(() => {
    const id = Number(worldIdProp.value);
    return !isNaN(id) && id > 0 ? id : null;
  });

  const entityApi = apiMap[entityType];
  if (!entityApi) {
    throw new Error(`[useEntityManagement] Invalid entity type: ${entityType}`);
  }

  // --- Fetching Functions ---
  const fetchItems = async (worldId: number) => {
    console.log(`[useEntityManagement:${entityType}] Fetching items for world ID: ${worldId}`);
    loading.value = true;
    error.value = undefined;
    items.value = [];
    try {
      // Assuming the response type matches E[] - Explicitly cast
      items.value = await entityApi.getAll(worldId) as E[];
      console.log(`[useEntityManagement:${entityType}] Fetched ${items.value.length} items.`);
    } catch (err: any) {
      console.error(`[useEntityManagement:${entityType}] Fetch Items Error:`, err);
      error.value = `Failed to load ${entityType}s: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    } finally {
      loading.value = false;
    }
  };

  const fetchTagTypes = async (worldId: number) => {
    console.log(`[useEntityManagement:${entityType}] Fetching tag types for world ID: ${worldId}`);
    tagTypesLoading.value = true;
    tagTypesError.value = undefined;
    tagTypes.value = [];
    try {
       // Assuming the response type matches TT[] - Explicitly cast
      tagTypes.value = await entityApi.getTagTypes(worldId) as TT[];
      console.log(`[useEntityManagement:${entityType}] Fetched ${tagTypes.value.length} tag types.`);
    } catch (err: any) {
      console.error(`[useEntityManagement:${entityType}] Fetch Tag Types Error:`, err);
      tagTypesError.value = `Failed to load ${entityType} tag types: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    } finally {
      tagTypesLoading.value = false;
    }
  };

  // --- Filtering Logic ---
  const filteredItems = computed(() => {
    const searchLower = search.value.toLowerCase();
    return items.value.filter(item => {
      // Text search
      const nameMatch = item.name.toLowerCase().includes(searchLower);
      // Ensure description is optional and handle potential null/undefined
      const descMatch = item.description ? item.description.toLowerCase().includes(searchLower) : false;
      const textMatch = nameMatch || descMatch;

      // Tag filter
      let itemTags: any[] | undefined; // Use 'any' for tags array for simplicity now
      let tagTypeIdKey: string = '';

      // Determine the property name for tags and the key for tag type ID
      switch (entityType) {
        case 'character':
            itemTags = (item as Character).tags;
            tagTypeIdKey = 'character_tag_type_id';
            break;
        case 'location':
            itemTags = (item as Location).tags;
            tagTypeIdKey = 'location_tag_type_id';
            break;
        case 'organization':
            itemTags = (item as Organization).tags;
            tagTypeIdKey = 'organization_tag_type_id';
            break;
        case 'item':
            itemTags = (item as Item).tags;
            tagTypeIdKey = 'item_tag_type_id';
            break;
        default:
            itemTags = []; // Default to empty if type is somehow unknown
            tagTypeIdKey = '';
      }

      // Check if all selected filter tags are present in the item's tags
      const hasAllTags = selectedTagIds.value.every(filterTagId =>
        (itemTags || []).some((tag: any) => tag && tag[tagTypeIdKey] === filterTagId)
      );

      return textMatch && hasAllTags;
    });
  });

  // --- Helper to get Tag Type Name ---
  const getTagTypeName = (tagTypeId: number | null | undefined): string => {
    if (tagTypeId === null || tagTypeId === undefined) return '';
    // Find the tag type name from the fetched tagTypes list
    const tagType = tagTypes.value.find(tt => tt.id === tagTypeId);
    return tagType ? tagType.name : `Unknown Tag (ID: ${tagTypeId})`;
  };

  // --- Tag Filter Management ---
  const addTagToFilter = (tagTypeId: number | null | undefined) => {
    if (tagTypeId === null || tagTypeId === undefined) return;
    // Add tag ID to the selection if not already present
    if (!selectedTagIds.value.includes(tagTypeId)) {
      selectedTagIds.value.push(tagTypeId);
    }
  };

  // --- Deletion Logic ---
  const deleteItem = async (id: number) => {
    console.log(`[useEntityManagement:${entityType}] Deleting item with ID: ${id}`);
    isDeleting.value = true;
    deleteError.value = null;
    try {
      await entityApi.delete(id);
      console.log(`[useEntityManagement:${entityType}] Item ${id} deleted successfully.`);
      // Refresh the list after successful deletion
      if (numericWorldId.value) {
        await fetchItems(numericWorldId.value);
      }
    } catch (err: any) {
      console.error(`[useEntityManagement:${entityType}] Delete Item Error:`, err);
      deleteError.value = `Failed to delete ${entityType}: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
      // Potentially re-throw or emit an event for UI feedback
    } finally {
      isDeleting.value = false;
    }
  };

  // --- Watcher for World ID Change ---
  watch(
    worldIdProp,
    (newId) => {
      console.log(`[useEntityManagement:${entityType}] worldIdProp changed:`, newId);
      const validId = Number(newId);
      if (!isNaN(validId) && validId > 0) {
        // Fetch items always when ID is valid
        fetchItems(validId);
        // Fetch tag types only if the flag is set
        if (fetchTagTypesFlag) {
          fetchTagTypes(validId);
        } else {
          tagTypes.value = []; // Ensure tags are cleared if not fetching
        }
      } else {
        // Reset state if the ID becomes invalid
        console.warn(`[useEntityManagement:${entityType}] worldId prop is invalid, resetting state.`);
        items.value = [];
        tagTypes.value = [];
        loading.value = false;
        tagTypesLoading.value = false;
        error.value = undefined;
        tagTypesError.value = undefined;
        selectedTagIds.value = [];
        search.value = '';
      }
    },
    { immediate: true } // Ensure fetch runs on initial load
  );

  // --- Manual Refresh Function ---
  const refresh = () => {
      if (numericWorldId.value) {
          console.log(`[useEntityManagement:${entityType}] Manual refresh triggered.`);
          // Re-fetch items
          fetchItems(numericWorldId.value);
          // Re-fetch tag types only if the flag is set
          if (fetchTagTypesFlag) {
            fetchTagTypes(numericWorldId.value);
          }
      }
  };

  return {
    // Data
    items: filteredItems, // Return the computed filtered list
    allItems: items, // Expose original unfiltered items ref if needed
    tagTypes,

    // State
    loading,
    error,
    tagTypesLoading,
    tagTypesError,
    isDeleting,
    deleteError,

    // Filters & Search
    search,
    selectedTagIds,
    addTagToFilter,

    // Helpers
    getTagTypeName,

    // Actions
    deleteItem,
    refresh, // Expose refresh function
  };
} 