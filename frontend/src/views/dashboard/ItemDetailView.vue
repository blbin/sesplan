<template>
  <div class="item-detail-view">
    <div v-if="loading" class="loading-message">Načítání detailu předmětu...</div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="item" class="item-content">
      <header class="view-header">
        <h1>{{ item.name }}</h1>
        <router-link v-if="worldId" :to="{ name: 'dashboard-world-detail', params: { worldId: worldId } }" class="btn btn-secondary">
          Zpět do světa
        </router-link>
        <button @click="openEditModal" class="btn btn-primary">Upravit předmět</button>
      </header>

      <div class="details-section">
        <h2>Detaily</h2>
        <p><strong>Popis:</strong></p>
        <p>{{ item.description || 'Žádný popis nebyl zadán.' }}</p>
        
        <p v-if="item.character_id">
          <strong>Postava:</strong> 
          ID: {{ item.character_id }}
        </p>
        <p v-if="item.location_id">
          <strong>Lokace:</strong> 
          ID: {{ item.location_id }}
        </p>
        <p><strong>ID světa:</strong> {{ worldId }}</p>
        <p><strong>Vytvořeno:</strong> {{ formatDate(item.created_at) }}</p>
        <p><strong>Aktualizováno:</strong> {{ formatDate(item.updated_at) }}</p>
      </div>

      <div class="details-section tags-section">
        <h2>Tagy</h2>
        <div v-if="item.tags && item.tags.length > 0" class="tags-container">
            <span
              v-for="tag in item.tags"
              :key="tag.id"
              class="tag-chip"
            >
              {{ tag.tag_type?.name || `Tag ID: ${tag.item_tag_type_id}` }}
            </span>
        </div>
        <p v-else>Žádné tagy přiřazeny.</p>
        <button @click="openTagEditDialog" class="btn btn-secondary mt-2">Upravit tagy</button>
      </div>

      <!-- Správa typů tagů -->
      <div class="details-section">
        <div class="section-header">
          <h2>Správa typů tagů předmětů</h2>
          <button @click="openAddTagTypeDialog" class="btn btn-primary">Přidat typ tagu</button>
        </div>

        <div v-if="tagTypesLoading" class="loading-state">Načítání typů tagů...</div>
        <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
        <div v-else-if="availableTagTypes.length > 0" class="tag-types-list">
          <div v-for="tagType in availableTagTypes" :key="tagType.id" class="tag-type-item">
            <span class="tag-type-name">{{ tagType.name }}</span>
            <div class="tag-type-actions">
              <button @click="openEditTagTypeDialog(tagType)" class="btn-icon">✏️</button>
              <button @click="confirmDeleteTagType(tagType)" class="btn-icon">🗑️</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">Zatím nebyly definovány žádné typy tagů předmětů pro tento svět.</div>
      </div>

      <!-- Edit Item Modal -->
      <div v-if="showEditModal" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Upravit předmět</h3>
            <button @click="closeEditModal" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <CreateItemForm
              v-if="worldId" 
              :worldId="worldId" 
              :characters="[]" 
              :locations="locations"
              :itemToEdit="item"
              :availableTagTypes="availableTagTypes"
              @saved="handleItemSaved"
              @cancel="closeEditModal"
            />
            <div v-else>Načítání kontextu světa...</div>
          </div>
        </div>
      </div>

      <!-- Edit Tags Modal -->
      <div v-if="showTagEditDialog" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Upravit tagy pro {{ item.name }}</h3>
            <button @click="closeTagEditDialog" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="tagTypesLoading">Načítání typů tagů...</div>
            <div v-else-if="tagTypesError" class="error-message">{{ tagTypesError }}</div>
            <div v-else>
              <div class="form-group">
                <label>Vyberte tagy:</label>
                <div class="tag-checkboxes">
                  <div v-for="tagType in availableTagTypes" :key="tagType.id" class="tag-checkbox">
                    <input 
                      type="checkbox" 
                      :id="'tag-' + tagType.id" 
                      :value="tagType.id" 
                      v-model="selectedTagTypeIds"
                    >
                    <label :for="'tag-' + tagType.id">{{ tagType.name }}</label>
                  </div>
                </div>
                <div v-if="availableTagTypes.length === 0" class="empty-tags-message">
                  Nejsou k dispozici žádné typy tagů. Nejprve nějaké vytvořte.
                </div>
              </div>
              <div v-if="tagSyncError" class="error-message">{{ tagSyncError }}</div>
              <div class="form-actions">
                <button @click="closeTagEditDialog" class="btn btn-secondary">Zrušit</button>
                <button 
                  @click="saveTags" 
                  class="btn btn-primary" 
                  :disabled="tagTypesLoading || isSavingTags"
                >
                  {{ isSavingTags ? 'Ukládání...' : 'Uložit tagy' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Add/Edit Tag Type Modal -->
      <div v-if="showTagTypeDialog" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ editingTagType ? 'Upravit typ tagu' : 'Přidat typ tagu' }}</h3>
            <button @click="closeTagTypeDialog" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="tagTypeName">Název typu tagu:</label>
              <input 
                type="text" 
                id="tagTypeName" 
                v-model="tagTypeName" 
                class="form-control" 
                :class="{ 'error': tagTypeDialogError }"
                @keyup.enter="saveTagType"
              >
              <div v-if="tagTypeDialogError" class="error-message">{{ tagTypeDialogError }}</div>
            </div>
            <div class="form-actions">
              <button @click="closeTagTypeDialog" class="btn btn-secondary">Zrušit</button>
              <button 
                @click="saveTagType" 
                class="btn btn-primary" 
                :disabled="!tagTypeName || isSavingTagType"
              >
                {{ isSavingTagType ? 'Ukládání...' : 'Uložit' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Tag Type Confirmation Modal -->
      <div v-if="showDeleteTagTypeConfirm" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>Potvrdit smazání</h3>
            <button @click="cancelDeleteTagType" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <p>Opravdu chcete smazat typ tagu "{{ tagTypeToDelete?.name }}"?</p>
            <div v-if="deleteTagTypeError" class="error-message">{{ deleteTagTypeError }}</div>
            <div class="form-actions">
              <button @click="cancelDeleteTagType" class="btn btn-secondary">Zrušit</button>
              <button 
                @click="executeDeleteTagType" 
                class="btn btn-danger" 
                :disabled="isDeletingTagType"
              >
                {{ isDeletingTagType ? 'Mazání...' : 'Smazat' }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import type { Item } from '@/types/item';
import type { ItemTagType } from '@/types/itemTagType';
import type { Location } from '@/types/location';
import * as itemsApi from '@/services/api/items';
import * as locationsApi from '@/services/api/locations';
import * as itemTagTypeApi from '@/services/api/itemTagTypeService';
import * as itemTagApi from '@/services/api/itemTagService';
import CreateItemForm from '@/components/worlds/CreateItemForm.vue';

export default defineComponent({
  name: 'ItemDetailView',
  components: { 
    CreateItemForm
  },
  props: {
    itemId: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const item = ref<Item | null>(null);
    const locations = ref<Location[]>([]);
    const loading = ref(true);
    const error = ref<string | null>(null);
    const showEditModal = ref(false);

    // State for tag editing dialog
    const showTagEditDialog = ref(false);
    const availableTagTypes = ref<ItemTagType[]>([]);
    const tagTypesLoading = ref(false);
    const tagTypesError = ref<string | null>(null);
    const selectedTagTypeIds = ref<number[]>([]); 
    const isSavingTags = ref(false);
    const tagSyncError = ref<string | null>(null);

    // State for tag type management
    const showTagTypeDialog = ref(false);
    const editingTagType = ref<ItemTagType | null>(null);
    const tagTypeName = ref('');
    const isSavingTagType = ref(false);
    const tagTypeDialogError = ref<string | null>(null);

    // State for delete confirmation
    const showDeleteTagTypeConfirm = ref(false);
    const tagTypeToDelete = ref<ItemTagType | null>(null);
    const isDeletingTagType = ref(false);
    const deleteTagTypeError = ref<string | null>(null);

    // Computed property pro získání worldId z načteného předmětu
    const worldId = computed(() => item.value?.world_id);

    const fetchItemDetails = async () => {
      loading.value = true;
      error.value = null;
      item.value = null;
      try {
        item.value = await itemsApi.getItem(props.itemId);
        // Pokud předmět existuje, načteme tagy pro jeho svět
        if (item.value?.world_id) {
          fetchTagTypes(item.value.world_id);
          fetchWorldLocations(item.value.world_id);
        } else if (!item.value && !loading.value) {
          error.value = 'Předmět nalezen, ale chybí ID světa.'; // Edge case
        }
      } catch (err: any) {
        console.error("Fetch Item Error:", err);
        if (err.response?.status === 404) {
          error.value = 'Předmět nenalezen.';
        } else {
          error.value = `Nepodařilo se načíst detaily předmětu: ${err.response?.data?.detail || err.message || 'Neznámá chyba'}`;
        }
      } finally {
        loading.value = false;
      }
    };

    const fetchTagTypes = async (idSvěta: number) => {
      if (!idSvěta) return; // Pojistka
      tagTypesLoading.value = true;
      tagTypesError.value = null;
      try {
        availableTagTypes.value = await itemTagTypeApi.getItemTagTypes(idSvěta);
      } catch (err: any) {
        console.error('Error fetching item tag types:', err);
        tagTypesError.value = err.message || 'Nepodařilo se načíst tagy';
        availableTagTypes.value = []; 
      } finally {
        tagTypesLoading.value = false;
      }
    };

    const fetchWorldLocations = async (idSvěta: number) => {
      try {
        locations.value = await locationsApi.getLocationsByWorld(idSvěta);
      } catch (err: any) {
        console.error('Error fetching world locations:', err);
        locations.value = [];
      }
    };

    // Item edit functions
    const openEditModal = () => {
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
    };

    const handleItemSaved = () => {
      closeEditModal();
      fetchItemDetails();
    };

    // Tag assignment functions
    const openTagEditDialog = () => {
      if (!item.value || worldId.value === undefined) return;
      selectedTagTypeIds.value = item.value.tags?.map(t => t.item_tag_type_id) || [];
      if (availableTagTypes.value.length === 0 || tagTypesError.value) {
        fetchTagTypes(worldId.value);
      }
      tagSyncError.value = null;
      showTagEditDialog.value = true;
    };

    const closeTagEditDialog = () => {
      showTagEditDialog.value = false;
    };

    const saveTags = async () => {
      if (!item.value) return;
      isSavingTags.value = true;
      tagSyncError.value = null;

      const originalTagTypeIds = item.value.tags?.map(t => t.item_tag_type_id) || [];
      const currentTagTypeIds = new Set(selectedTagTypeIds.value);
      const originalTagTypeIdsSet = new Set(originalTagTypeIds);

      const tagsToAdd = selectedTagTypeIds.value.filter(id => !originalTagTypeIdsSet.has(id));
      const tagsToRemove = originalTagTypeIds.filter(id => !currentTagTypeIds.has(id));

      const addPromises = tagsToAdd.map(tagTypeId => 
        itemTagApi.addItemTagToItem(props.itemId, tagTypeId)
      );
      const removePromises = tagsToRemove.map(tagTypeId => 
        itemTagApi.removeItemTagFromItem(props.itemId, tagTypeId)
      );

      try {
        await Promise.all([...addPromises, ...removePromises]);
        closeTagEditDialog();
        fetchItemDetails();
      } catch (err: any) {
        console.error("Error syncing tags:", err);
        tagSyncError.value = `Nepodařilo se synchronizovat tagy: ${err.message || 'Neznámá chyba'}`;
      } finally {
        isSavingTags.value = false;
      }
    };

    // Tag type management functions
    const openAddTagTypeDialog = () => {
      editingTagType.value = null;
      tagTypeName.value = '';
      tagTypeDialogError.value = null;
      showTagTypeDialog.value = true;
    };

    const openEditTagTypeDialog = (tagType: ItemTagType) => {
      editingTagType.value = { ...tagType };
      tagTypeName.value = tagType.name;
      tagTypeDialogError.value = null;
      showTagTypeDialog.value = true;
    };

    const closeTagTypeDialog = () => {
      showTagTypeDialog.value = false;
      editingTagType.value = null;
      tagTypeName.value = '';
      tagTypeDialogError.value = null;
    };

    const saveTagType = async () => {
      if (!tagTypeName.value || !worldId.value) return;
      isSavingTagType.value = true;
      tagTypeDialogError.value = null;

      try {
        if (editingTagType.value) {
          // Update
          const updateData = { name: tagTypeName.value };
          const updated = await itemTagTypeApi.updateItemTagType(worldId.value, editingTagType.value.id, updateData);
          // Update in local list
          const index = availableTagTypes.value.findIndex(t => t.id === updated.id);
          if (index !== -1) availableTagTypes.value[index] = updated;
        } else {
          // Create
          const createData = { name: tagTypeName.value };
          const created = await itemTagTypeApi.createItemTagType(worldId.value, createData);
          availableTagTypes.value.push(created);
        }
        closeTagTypeDialog();
      } catch (err: any) {
        console.error('Error saving tag type:', err);
        tagTypeDialogError.value = err.response?.data?.detail || err.message || 'Nepodařilo se uložit typ tagu';
      } finally {
        isSavingTagType.value = false;
      }
    };

    // Delete tag type functions
    const confirmDeleteTagType = (tagType: ItemTagType) => {
      tagTypeToDelete.value = tagType;
      deleteTagTypeError.value = null;
      showDeleteTagTypeConfirm.value = true;
    };

    const cancelDeleteTagType = () => {
      showDeleteTagTypeConfirm.value = false;
      tagTypeToDelete.value = null;
      deleteTagTypeError.value = null;
    };

    const executeDeleteTagType = async () => {
      if (!tagTypeToDelete.value || !worldId.value) return;
      isDeletingTagType.value = true;
      deleteTagTypeError.value = null;
      try {
        await itemTagTypeApi.deleteItemTagType(worldId.value, tagTypeToDelete.value.id);
        availableTagTypes.value = availableTagTypes.value.filter(t => t.id !== tagTypeToDelete.value?.id);
        cancelDeleteTagType(); // Close modal on success
      } catch (err: any) {
        console.error('Error deleting tag type:', err);
        deleteTagTypeError.value = err.response?.data?.detail || err.message || 'Nepodařilo se smazat typ tagu';
      } finally {
        isDeletingTagType.value = false;
      }
    };

    const formatDate = (dateString: string | null | undefined): string => {
      if (!dateString) return 'N/A';
      try {
        return new Date(dateString).toLocaleDateString();
      } catch (e) {
        return String(dateString); 
      }
    };

    onMounted(fetchItemDetails);

    return {
      item,
      loading,
      error,
      worldId,
      locations,
      formatDate,
      // Item edit
      showEditModal,
      openEditModal,
      closeEditModal,
      handleItemSaved,
      // Tag assignment
      showTagEditDialog,
      availableTagTypes,
      tagTypesLoading,
      tagTypesError,
      selectedTagTypeIds,
      isSavingTags,
      tagSyncError,
      openTagEditDialog,
      closeTagEditDialog,
      saveTags,
      // Tag type management
      showTagTypeDialog,
      editingTagType,
      tagTypeName,
      isSavingTagType,
      tagTypeDialogError,
      openAddTagTypeDialog,
      openEditTagTypeDialog,
      closeTagTypeDialog,
      saveTagType,
      // Delete tag type
      showDeleteTagTypeConfirm,
      tagTypeToDelete,
      isDeletingTagType,
      deleteTagTypeError,
      confirmDeleteTagType,
      cancelDeleteTagType,
      executeDeleteTagType
    };
  }
});
</script>

<style scoped>
.item-detail-view {
  padding: 1rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.view-header h1 {
  margin: 0;
  font-size: 2rem;
}

.details-section {
  margin-bottom: 2rem;
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.details-section h2 {
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.5rem;
}

.tag-types-list {
  margin-top: 1rem;
}

.tag-type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.tag-type-item:last-child {
  border-bottom: none;
}

.tag-type-name {
  font-weight: 500;
}

.tag-type-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.btn-icon:hover {
  background-color: #f0f0f0;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 1rem;
  color: #666;
}

.empty-state {
  font-style: italic;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag-chip {
  background-color: #e0f2f1;
  color: #00796b;
  padding: 0.3rem 0.7rem;
  border-radius: 16px;
  font-size: 0.9rem;
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
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.form-control.error {
  border-color: #dc3545;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.tag-checkboxes {
  margin-top: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 0.5rem;
  border-radius: 4px;
}

.tag-checkbox {
  margin-bottom: 0.5rem;
}

.tag-checkbox:last-child {
  margin-bottom: 0;
}

.empty-tags-message {
  font-style: italic;
  color: #666;
  text-align: center;
  padding: 1rem;
}

.error-message {
  color: #dc3545;
  margin-top: 0.5rem;
}

.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
}

.btn-primary:hover {
  background-color: #1565c0;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.mt-2 {
  margin-top: 0.5rem;
}

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

.modal-container {
  background-color: white;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}
</style> 