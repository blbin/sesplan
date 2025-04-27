<template>
  <div class="entity-table-container">
    <!-- Header: Title, Search, Action Buttons -->
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 class="text-h5">{{ title }}</h2>
      
      <!-- Search Field -->
      <v-text-field
        v-model="search"
        :label="`Search ${title}`"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="compact"
        hide-details
        single-line
        class="mx-4 flex-grow-1"
        style="max-width: 400px;" 
      ></v-text-field>
      
      <!-- Action Buttons -->
      <div>
        <v-btn 
          v-if="isCurrentUserOwner" 
          color="primary" 
          variant="flat" 
          prepend-icon="mdi-plus" 
          @click="emitAdd"
          class="mr-2"
          size="small"
        >
          Add {{ singularEntityType }}
        </v-btn>
        <v-btn 
          color="primary" 
          variant="outlined" 
          prepend-icon="mdi-robot"
          @click="emitGenerateAI"
          :disabled="worldLoading || loading" 
          size="small"
        >
          Generate with AI
        </v-btn>
      </div>
    </div>

    <!-- Error Display -->
    <v-alert 
      v-if="error || tagTypesError || assignableUsersError"
      type="error"
      variant="tonal"
      closable
      class="mb-4"
    >
      <p v-if="error">{{ error }}</p>
      <p v-if="tagTypesError">{{ tagTypesError }}</p>
      <p v-if="assignableUsersError">{{ assignableUsersError }}</p>
    </v-alert>

    <!-- Data Table -->
    <v-data-table
      :headers="dynamicHeaders"
      :items="items"
      :loading="loading || tagTypesLoading || isDeleting"
      item-value="id"
      class="elevation-1 clickable-rows"
      :items-per-page="itemsPerPage"
      :items-per-page-options="[5, 10, 25, { value: -1, title: 'All' }]"
      :search="search" 
      @click:row="handleRowClick"
    >
      <!-- Loading Slot -->
       <template v-slot:loading>
         <v-skeleton-loader type="table-row@5"></v-skeleton-loader>
       </template>

      <!-- Header Slot for Tags Filter -->
      <template v-slot:header.tags>
        <div @click.stop> 
          Tags
          <v-select
            v-model="selectedTagIds"
            :items="tagTypes"
            item-title="name"
            item-value="id"
            multiple
            chips
            closable-chips
            clearable
            :loading="tagTypesLoading"
            density="compact"
            hide-details
            variant="underlined"
            class="tag-filter-select"
            placeholder="Filter..."
            :menu-props="{ closeOnContentClick: false }"
          ></v-select>
        </div>
      </template>

      <!-- Item Slot for Name (Bold) -->
      <template v-slot:item.name="{ item }">
        <strong>{{ item.name }}</strong>
      </template>

      <!-- Item Slot for Description (Markdown Preview) -->
      <template v-slot:item.description="{ item }">
        <div v-if="item.description" v-html="renderMarkdownPreview(item.description)" class="description-preview"></div>
        <em v-else class="text-muted">No description</em>
      </template>

      <!-- Item Slot for Tags (Chips) -->
      <template v-slot:item.tags="{ item }">
        <v-chip 
          v-for="(tag, index) in getTagsForItem(item)" 
          :key="tag ? tag[getTagTypeIdKey(props.entityType)] : index" 
          size="small" 
          class="mr-1 mb-1 clickable-tag"
          @click.stop="addTagToFilter(tag ? tag[getTagTypeIdKey(props.entityType)] : null)"
        >
          {{ getTagTypeName(tag ? tag[getTagTypeIdKey(props.entityType)] : null) || 'Tag' }}
        </v-chip>
      </template>

      <!-- Item Slot for Assigned User (Characters only) -->
      <template v-if="entityType === 'character'" v-slot:item.assigned_user="{ item }">
        <!-- Always display the name -->
        <span>{{ getUserDisplayName((item as any).user_id) }}</span>
      </template>

      <!-- Item Slot for Actions (Edit/Delete) -->
      <template v-slot:item.actions="{ item }">
        <v-tooltip location="top">
          <template v-slot:activator="{ props: tooltipProps }">
            <v-icon v-bind="tooltipProps" small @click.stop="emitEdit(item)" class="mr-2 action-icon">mdi-pencil</v-icon>
          </template>
          <span>Edit {{ singularEntityType }}</span>
        </v-tooltip>
        <v-tooltip location="top">
          <template v-slot:activator="{ props: tooltipProps }">
            <v-icon v-bind="tooltipProps" small @click.stop="emitDelete(item)" class="action-icon">mdi-delete</v-icon>
          </template>
          <span>Delete {{ singularEntityType }}</span>
        </v-tooltip>
      </template>

      <!-- No Data Slot -->
      <template v-slot:no-data>
        <p v-if="search || selectedTagIds.length > 0" class="text-center pa-4 text-muted">
          No {{ title.toLowerCase() }} match the current filters.
        </p>
        <p v-else class="text-center pa-4 text-muted">No {{ title.toLowerCase() }} found for this world yet.</p>
      </template>

       <!-- Allow overriding slots from parent -->
       <template v-for="(_, slot) in $slots" v-slot:[slot]="scope">
         <slot :name="slot" v-bind="scope || {}"></slot>
       </template>

    </v-data-table>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef, defineExpose, watch } from 'vue';
import { useEntityManagement } from '@/composables/useEntityManagement';
import type { EntityType } from '@/composables/useEntityManagement'; // Import as type
import { useWorldDetail } from '@/composables/useWorldDetail'; // To check world loading state and get markdown renderer
import { 
  VBtn, 
  VTextField, 
  VDataTable,
  VSelect, 
  VChip, 
  VIcon, 
  VTooltip, 
  VAlert,
  VSkeletonLoader,
} from 'vuetify/components';

// Type for table headers - Use a more specific type if available from Vuetify
type TableHeader = { 
  title: string; 
  key: string; 
  sortable?: boolean; 
  align?: 'start' | 'center' | 'end';
  // Add other potential header properties if needed
};
type ReadonlyHeaders = Readonly<TableHeader[]>;

// Props definition
const props = defineProps<{
  worldId: string | number | undefined;
  entityType: EntityType;
  title: string;
  headers: ReadonlyHeaders;
  isCurrentUserOwner: boolean;
  itemsPerPage?: number;
  fetchTagTypes?: boolean;
}>();

// Default props
const { itemsPerPage = 10 } = props;

// Emits definition
const emit = defineEmits<{
  (e: 'add'): void;
  (e: 'edit', item: any): void;
  (e: 'delete', item: any): void;
  (e: 'generateAI'): void;
  (e: 'rowClick', item: any): void;
  (e: 'update:assignableUsers', newValue: any[]): void;
}>();

// Use the entity management composable
const {
  items,
  tagTypes,
  assignableUsers,
  loading,
  error,
  tagTypesLoading,
  tagTypesError,
  assignableUsersError,
  isDeleting,
  search,
  selectedTagIds,
  addTagToFilter,
  getTagTypeName,
  deleteItem,
  refreshData,
} = useEntityManagement(
    toRef(props, 'worldId'), 
    props.entityType, 
    props.fetchTagTypes, 
    toRef(props, 'isCurrentUserOwner')
);

// Use world detail composable for world loading state and markdown preview
const { worldLoading, renderMarkdownPreview } = useWorldDetail(toRef(props, 'worldId'));

// Expose the refreshData function to the parent component
defineExpose({
  refreshData
});

// Compute singular entity type for button labels
const singularEntityType = computed(() => {
  return props.title.endsWith('s') ? props.title.slice(0, -1) : props.title;
});

// Add the 'actions' and potentially 'assigned_user' column headers dynamically
const dynamicHeaders = computed(() => {
    let newHeaders = [...props.headers];

    // Add Assigned User column for characters
    if (props.entityType === 'character') {
       const userHeader: TableHeader = { title: 'Assigned User', key: 'assigned_user', sortable: true, align: 'start' };
       // Insert before actions if actions column exists, otherwise push
       const actionsIndex = newHeaders.findIndex(h => h.key === 'actions');
       if (actionsIndex !== -1) {
           newHeaders.splice(actionsIndex, 0, userHeader);
       } else {
           newHeaders.push(userHeader);
       }
    }

    // Add Actions column if not present
    const actionsHeader: TableHeader = { title: 'Actions', key: 'actions', sortable: false, align: 'end' };
    if (!newHeaders.some((h: TableHeader) => h.key === 'actions')) {
        newHeaders.push(actionsHeader);
    }
    return newHeaders;
});

// Helper to get the correct tag array from the item
const getTagsForItem = (item: any): any[] => {
  switch (props.entityType) {
    case 'character': return item.tags || [];
    case 'location': return item.tags || [];
    case 'organization': return item.tags || [];
    case 'item': return item.tags || [];
    default: return [];
  }
};

// Helper to get the key for the tag type ID within a tag object
const getTagTypeIdKey = (type: EntityType): string => {
  switch (type) {
    case 'character': return 'character_tag_type_id';
    case 'location': return 'location_tag_type_id';
    case 'organization': return 'organization_tag_type_id';
    case 'item': return 'item_tag_type_id';
    default: return 'id'; // Fallback, should not happen
  }
};

// --- User Assignment Helpers (Characters only) ---
const getUserDisplayName = (userId: number | null): string => {
    if (userId === null || props.entityType !== 'character') return '-'; // Display dash for unassigned or wrong type
    const user = assignableUsers.value.find(u => u.id === userId);
    return user ? user.username : `User ID: ${userId}`;
};

// --- Event Handlers ---
const emitAdd = () => {
  emit('add');
};

const emitEdit = (item: any) => {
  emit('edit', item);
};

const emitDelete = async (item: any) => {
  // Get singular type directly from props
  const singularType = props.entityType.charAt(0).toUpperCase() + props.entityType.slice(1);
  if (confirm(`Are you sure you want to delete ${singularType} "${item.name}"?`)) {
    await deleteItem(item.id);
    emit('delete', item);
  }
};

const emitGenerateAI = () => {
  emit('generateAI');
};

const handleRowClick = (event: MouseEvent, { item }: { item: any }) => {
  // Check if the click was on an interactive element within the row
  const target = event.target as HTMLElement;
  if (target.closest('.action-icon, .v-select, .clickable-tag')) {
    return; // Don't navigate if clicking on an action/select/tag
  }
  emit('rowClick', item);
};

// --- Watchers (If needed, e.g., to emit assignable users) ---
// Watch assignableUsers and emit an update event
watch(assignableUsers, (newValue) => {
    if (props.entityType === 'character') {
        emit('update:assignableUsers', newValue);
    }
}, { deep: true }); // Use deep watch if necessary, depends on how assignableUsers is updated

</script>

<style scoped>
/* Container styling */

.tag-filter-select {
  max-width: 200px; 
  margin-top: -10px; /* Align with header text */
}

.clickable-rows :deep(tbody tr:hover) {
  cursor: pointer;
  background-color: rgba(0, 0, 0, 0.03); /* Optional hover effect */
}

.description-preview {
  font-size: 0.9em;
  color: #555;
  max-width: 300px; /* Limit preview width */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-muted {
  color: #6c757d;
  font-style: italic;
}

.clickable-tag {
    cursor: pointer;
}

.action-icon {
    cursor: pointer;
    opacity: 0.7;
    transition: opacity 0.2s ease-in-out;
}

.action-icon:hover {
    opacity: 1;
}

/* Style for assigned user column if needed */
/* For example, to ensure v-select doesn't overflow */
:deep(.v-data-table__td.assigned-user-cell) {
    /* Adjust as needed */
}

</style> 