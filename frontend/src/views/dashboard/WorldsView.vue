<template>
  <div class="worlds-view">
    <header class="view-header">
      <h1>My Worlds</h1>
      <button @click="openAddModal" class="btn btn-primary">
        <i class="icon">+</i> Add New World
      </button>
    </header>

    <div class="world-list-container">
      <p v-if="loading">Loading worlds...</p>
      <p v-else-if="error">{{ error }}</p>
      <div v-else-if="worlds.length === 0">
        You haven't created any worlds yet.
      </div>
      <WorldList
        v-else
        :worlds="worlds"
        @edit-world="openEditModal"
        @delete-world="confirmDelete"
      />
    </div>

    <WorldFormModal
      :show="showAddWorldModal || !!editingWorld"
      :worldToEdit="editingWorld"
      :isSaving="isSavingWorld"
      :error="formError"
      @save="handleSaveWorld"
      @cancel="closeModal"
    />

     <!-- Modál pro potvrzení smazání - Replaced with component -->
     <ConfirmDeleteModal
        :show="!!worldToDelete"
        itemType="world"
        :itemName="worldToDelete?.name"
        :isDeleting="isDeletingWorld"
        :error="deleteError"
        @confirm="handleDeleteWorld"
        @cancel="worldToDelete = null"
     />

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import * as worldsApi from '@/services/api/worlds';
import type { World, WorldCreate, WorldUpdate } from '@/types/world';
import WorldList from '@/components/worlds/WorldList.vue';
import WorldFormModal from '@/components/worlds/WorldFormModal.vue';
import ConfirmDeleteModal from '@/components/common/ConfirmDeleteModal.vue';

export default defineComponent({
  name: 'WorldsView',
  components: {
      WorldList,
      WorldFormModal,
      ConfirmDeleteModal,
  },
  setup() {
    const worlds = ref<World[]>([]);
    const loading = ref(true);
    const error = ref<string | null>(null);
    const formError = ref<string | null>(null);
    const deleteError = ref<string | null>(null);
    const isSavingWorld = ref(false);
    const isDeletingWorld = ref(false);

    const showAddWorldModal = ref(false);
    const editingWorld = ref<World | null>(null);
    const worldToDelete = ref<World | null>(null);

    const loadWorlds = async () => {
      loading.value = true;
      error.value = null;
      try {
        worlds.value = await worldsApi.getWorlds();
      } catch (err: any) {
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load worlds.');
        console.error("Load Worlds Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const openAddModal = () => {
        editingWorld.value = null;
        formError.value = null;
        showAddWorldModal.value = true;
    };

    const closeModal = () => {
      showAddWorldModal.value = false;
      editingWorld.value = null;
      formError.value = null;
    };

     const openEditModal = (world: World) => {
      formError.value = null;
      editingWorld.value = world;
      showAddWorldModal.value = false;
    };

    const handleSaveWorld = async (data: WorldCreate | WorldUpdate) => {
       formError.value = null;
       isSavingWorld.value = true;
       try {
         if (editingWorld.value && ('name' in data || 'description' in data)) {
           if (!editingWorld.value) {
               throw new Error("Assertion failed: editingWorld should not be null here.");
           }
           const updatedWorld = await worldsApi.updateWorld(editingWorld.value.id, data as WorldUpdate);
           const index = worlds.value.findIndex((w: World) => w.id === updatedWorld.id);
           if (index !== -1) {
               worlds.value[index] = updatedWorld;
           }
         } else if (!editingWorld.value) {
           const newWorld = await worldsApi.createWorld(data as WorldCreate);
           worlds.value.push(newWorld);
         }
         closeModal();
       } catch(err: any) {
          formError.value = typeof err === 'string' ? err : (err?.message || (editingWorld.value ? 'Failed to update world.' : 'Failed to create world.'));
          console.error("Save World Error:", err);
       } finally {
           isSavingWorld.value = false;
       }
    };

    const confirmDelete = (world: World) => {
        worldToDelete.value = world;
        deleteError.value = null;
    };

    const handleDeleteWorld = async () => {
      if (!worldToDelete.value) return;
      const idToDelete = worldToDelete.value.id;
      deleteError.value = null;
      isDeletingWorld.value = true;
      try {
          await worldsApi.deleteWorld(idToDelete);
          worlds.value = worlds.value.filter((w: World) => w.id !== idToDelete);
          worldToDelete.value = null;
      } catch (err: any) {
           deleteError.value = typeof err === 'string' ? err : (err?.message || 'Failed to delete world.');
           console.error("Delete World Error:", err);
      } finally {
           isDeletingWorld.value = false;
      }
    };

    onMounted(loadWorlds);

    return {
      worlds,
      loading,
      error,
      formError,
      deleteError,
      isSavingWorld,
      isDeletingWorld,
      showAddWorldModal,
      editingWorld,
      worldToDelete,
      closeModal,
      openAddModal,
      openEditModal,
      handleSaveWorld,
      confirmDelete,
      handleDeleteWorld,
    };
  }
});
</script>

<style scoped>
.worlds-view {
  padding: 2rem;
  background-color: #f8f9fa;
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

.world-list-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* World list item styles moved to WorldList.vue */

/* Button styles (keep general ones used in header/modals) */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  text-decoration: none;
}
.btn .icon {
 font-style: normal;
}
.btn:disabled { /* Style for disabled buttons */
    opacity: 0.65;
    cursor: not-allowed;
}
.btn-primary {
  background-color: #7851a9;
  color: white;
}
.btn-primary:not(:disabled):hover {
  background-color: #5f3f87;
}
.btn-secondary {
  background-color: #6c757d;
   color: white;
}
.btn-secondary:not(:disabled):hover {
   background-color: #5a6268;
}
.btn-danger {
  background-color: #dc3545;
  color: white;
}
.btn-danger:not(:disabled):hover {
   background-color: #c82333;
}
.btn-sm { /* Keep if used in modals */
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
}

/* Modal styles (only for delete confirmation modal now) */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 2rem;
  border-radius: 0.5rem;
  min-width: 300px;
  max-width: 500px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.modal h2 {
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #343a40;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
   padding-top: 1rem;
   border-top: 1px solid #e9ecef;
}

.confirmation-modal p {
    margin-bottom: 1.5rem;
    color: #495057;
    line-height: 1.5;
}

.error-message {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 1rem;
  text-align: center;
}
</style> 