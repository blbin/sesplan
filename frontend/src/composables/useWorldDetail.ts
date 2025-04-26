import { ref, computed, watch } from 'vue';
import type { Ref } from 'vue';
import * as worldsApi from '@/services/api/worlds';
import type { World } from '@/types/world';
import { formatDateTime, formatDate } from '@/utils/dateFormatter';
import MarkdownIt from 'markdown-it';

// Initialize markdown-it instance (consider making this a shared utility if used elsewhere)
const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
});

export function useWorldDetail(worldIdProp: Ref<string | number | undefined>) {
  const world = ref<World | null>(null);
  const worldLoading = ref(true);
  const worldError = ref<string | undefined>(undefined);

  // Name Editing State
  const isEditingName = ref(false);
  const editedName = ref('');
  const isSavingName = ref(false);

  // Description Editing State
  const isEditingDescription = ref(false);
  const editedDescription = ref('');
  const isSavingDescription = ref(false);

  const isCurrentUserOwner = computed(() => {
      // Simple owner check - might need enhancement based on actual auth logic
      // Assuming if we can load the world without permission errors, the user might have rights,
      // or the world is public. A dedicated permission check/prop might be better.
      return world.value !== null && !worldLoading.value && worldError.value === undefined;
  });

  // Computed property for rendering description
  const renderedDescription = computed(() => {
    if (world.value?.description) {
      return md.render(world.value.description);
    }
    return ''; // Return empty string instead of HTML paragraph for flexibility
  });

  // Method to render markdown preview
  const renderMarkdownPreview = (markdown: string | null | undefined, maxLength: number = 100): string => {
      if (!markdown) {
          return '';
      }
      let truncatedMd = markdown.length > maxLength
          ? markdown.substring(0, maxLength) + '...'
          : markdown;
      // Use renderInline to avoid block elements like <p>
      return md.renderInline(truncatedMd);
  };


  // Fetch World Details Function
  const fetchWorldDetails = async (id: number | string) => {
    const numericId = Number(id);
    if (isNaN(numericId) || numericId <= 0) {
      console.error("Invalid World ID for fetching:", id);
      worldError.value = "Invalid World ID provided.";
      worldLoading.value = false;
      world.value = null;
      return;
    }

    console.log(`[useWorldDetail] Fetching details for world ID: ${numericId}`);
    worldLoading.value = true;
    worldError.value = undefined;
    world.value = null; // Reset before fetching

    try {
      const fetchedWorld = await worldsApi.getWorldById(numericId);
      world.value = fetchedWorld;
      console.log("[useWorldDetail] World data fetched:", fetchedWorld);
    } catch (err: any) {
      console.error("[useWorldDetail] Fetch World Error:", err);
      if (err.response?.status === 404) {
        worldError.value = 'World not found.';
      } else if (err.response?.status === 403) {
        worldError.value = 'You do not have permission to view this world.';
      } else {
        worldError.value = `Failed to load world details: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
      }
    } finally {
      worldLoading.value = false;
      console.log("[useWorldDetail] Finished fetching world details.");
    }
  };

  // Name Editing Functions
  const startEditingName = () => {
    if (!world.value) return;
    editedName.value = world.value.name;
    isEditingName.value = true;
  };

  const cancelEditingName = () => {
    isEditingName.value = false;
  };

  const saveName = async () => {
    if (!world.value || !editedName.value || editedName.value === world.value.name) {
      isEditingName.value = false;
      return;
    }
    isSavingName.value = true;
    try {
      // Assume updateWorld only needs the fields being changed
      const updatedWorld = await worldsApi.updateWorld(world.value.id, { name: editedName.value });
      world.value = { ...world.value, ...updatedWorld }; // Merge updates
      isEditingName.value = false;
      console.log("[useWorldDetail] World name saved successfully.");
    } catch (err: any) {
      console.error("[useWorldDetail] Failed to save world name:", err);
      // Consider adding user-facing error feedback here (e.g., via an event or state)
      worldError.value = `Failed to save name: ${err.message || 'Unknown error'}`;
    } finally {
      isSavingName.value = false;
    }
  };

  // Description Editing Functions
  const startEditingDescription = () => {
    if (!world.value) return;
    editedDescription.value = world.value.description || '';
    isEditingDescription.value = true;
  };

  const cancelEditingDescription = () => {
    isEditingDescription.value = false;
  };

  const saveDescription = async () => {
    if (!world.value) return;
    // Check if description actually changed
    if (editedDescription.value === (world.value.description || '')) {
        isEditingDescription.value = false;
        return;
    }
    isSavingDescription.value = true;
    try {
      const updatedWorld = await worldsApi.updateWorld(world.value.id, { description: editedDescription.value });
      world.value = { ...world.value, ...updatedWorld }; // Merge updates
      isEditingDescription.value = false;
      console.log("[useWorldDetail] World description saved successfully.");
    } catch (err: any) {
      console.error("[useWorldDetail] Failed to save description:", err);
      worldError.value = `Failed to save description: ${err.message || 'Unknown error'}`;
      // Add user-facing error handling
    } finally {
      isSavingDescription.value = false;
    }
  };

  // Watch the prop for changes
  watch(
    worldIdProp,
    (newId) => {
      console.log('[useWorldDetail] worldIdProp changed:', newId);
      if (newId !== undefined && newId !== null && String(newId).trim() !== '') {
        fetchWorldDetails(newId);
      } else {
        console.warn("[useWorldDetail] worldId prop is invalid, resetting state.");
        world.value = null;
        worldLoading.value = false; // No longer loading if ID is invalid
        worldError.value = "World ID is missing or invalid.";
        // Reset editing states as well
        isEditingName.value = false;
        isEditingDescription.value = false;
      }
    },
    { immediate: true } // Run immediately on composable initialization
  );

  // Return reactive state and methods
  return {
    world,
    worldLoading,
    worldError,
    isCurrentUserOwner, // Note: Simplified ownership check

    // Name editing
    isEditingName,
    editedName,
    isSavingName,
    startEditingName,
    cancelEditingName,
    saveName,

    // Description editing
    isEditingDescription,
    editedDescription,
    isSavingDescription,
    renderedDescription,
    startEditingDescription,
    cancelEditingDescription,
    saveDescription,

    // Utilities (re-exported for convenience)
    formatDate,
    formatDateTime,
    renderMarkdownPreview, // Export the preview function
  };
} 