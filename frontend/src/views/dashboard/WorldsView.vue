<template>
  <div class="worlds-view">
    <header class="view-header">
      <h1>My Worlds</h1>
      <button @click="showAddWorldModal = true" class="btn btn-primary">
        <i class="icon">+</i> Add New World
      </button>
    </header>

    <div class="world-list-container">
      <!-- Zde bude seznam světů -->
      <p v-if="loading">Loading worlds...</p>
      <p v-else-if="error">{{ error }}</p>
      <div v-else-if="worlds.length === 0">
        You haven't created any worlds yet.
      </div>
      <ul v-else class="world-list">
        <li v-for="world in worlds" :key="world.id" class="world-list-item">
          <div class="world-info">
            <h2>{{ world.name }}</h2>
            <p>{{ world.description || 'No description' }}</p>
            <!-- Zobrazení kampaní -->
            <div v-if="world.campaigns && world.campaigns.length > 0" class="world-campaigns">
              <strong>Campaigns:</strong>
              <ul>
                <li v-for="campaign in world.campaigns" :key="campaign.id">
                  {{ campaign.name }}
                  <!-- Zde by mohl být odkaz na detail kampaně -->
                </li>
              </ul>
            </div>
            <div v-else class="world-campaigns-empty">
              No campaigns in this world yet.
            </div>
          </div>
          <div class="world-actions">
            <button @click="openEditModal(world)" class="btn btn-secondary btn-sm">Edit</button>
            <router-link :to="`/dashboard/worlds/${world.id}/campaigns`" class="btn btn-info btn-sm">Campaigns</router-link>
            <button @click="confirmDelete(world)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Modál pro přidání/úpravu světa (zjednodušený) -->
    <div v-if="showAddWorldModal || editingWorld" class="modal-backdrop">
      <div class="modal">
        <h2>{{ editingWorld ? 'Edit World' : 'Add New World' }}</h2>
        <form @submit.prevent="handleSaveWorld">
          <div class="form-group">
            <label for="worldName">Name:</label>
            <input type="text" id="worldName" v-model="worldForm.name" required>
          </div>
          <div class="form-group">
            <label for="worldDescription">Description:</label>
            <textarea id="worldDescription" v-model="worldForm.description"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">{{ editingWorld ? 'Save Changes' : 'Create World' }}</button>
          </div>
           <p v-if="formError" class="error-message">{{ formError }}</p>
        </form>
      </div>
    </div>

     <!-- Modál pro potvrzení smazání (zjednodušený) -->
    <div v-if="worldToDelete" class="modal-backdrop">
      <div class="modal confirmation-modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete the world "{{ worldToDelete.name }}"? This action cannot be undone.</p>
         <div class="modal-actions">
            <button type="button" @click="worldToDelete = null" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="handleDeleteWorld" class="btn btn-danger">Delete</button>
          </div>
           <p v-if="deleteError" class="error-message">{{ deleteError }}</p>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from 'vue';
import * as worldsApi from '../../services/api/worlds'; // Zkusíme relativní cestu
import type { World, WorldCreate, WorldUpdate } from '../../types/world'; // Zkusíme relativní cestu

// Nový typ pro formulářová data
interface WorldFormData {
  name: string;
  description: string | null;
}

export default defineComponent({
  name: 'WorldsView',
  setup() {
    const worlds = ref<World[]>([]);
    const loading = ref(true);
    const error = ref<string | null>(null);
    const formError = ref<string | null>(null);
    const deleteError = ref<string | null>(null);

    const showAddWorldModal = ref(false);
    const editingWorld = ref<World | null>(null);
    const worldToDelete = ref<World | null>(null);

    // Použijeme nový typ pro formulář
    const worldForm = reactive<WorldFormData>({
      name: '',
      description: null // Inicializujeme jako null pro konzistenci
    });

    const loadWorlds = async () => {
      loading.value = true;
      error.value = null;
      try {
        worlds.value = await worldsApi.getWorlds();
      } catch (err: any) {
        // Zpracování chyby - err může být string z rejectu v apiClient nebo AxiosError
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load worlds.');
        console.error("Load Worlds Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const resetForm = () => {
      worldForm.name = '';
      worldForm.description = null; // Reset na null
      editingWorld.value = null;
      formError.value = null;
    };

    const closeModal = () => {
      showAddWorldModal.value = false;
      editingWorld.value = null; // Zajistí zavření i editačního módu
      resetForm();
    };

     const openEditModal = (world: World) => {
      editingWorld.value = world;
      worldForm.name = world.name; // world.name je string
      worldForm.description = world.description; // world.description je string | null
      showAddWorldModal.value = false; 
      formError.value = null; 
    };

    const handleSaveWorld = async () => {
       formError.value = null;
       try {
         if (editingWorld.value) {
           // Update
           const worldDataToUpdate: WorldUpdate = {};
           // Porovnáváme s původními hodnotami editovaného světa
           if (worldForm.name !== editingWorld.value.name) {
               // worldForm.name je nyní zaručeně string
               worldDataToUpdate.name = worldForm.name;
           }
           if (worldForm.description !== editingWorld.value.description) {
               // worldForm.description je string | null
               worldDataToUpdate.description = worldForm.description;
           }

           // Pokud nejsou žádné změny, neposílej request
           if (Object.keys(worldDataToUpdate).length === 0) {
               closeModal();
               return;
           }
           const updatedWorld = await worldsApi.updateWorld(editingWorld.value.id, worldDataToUpdate);
           const index = worlds.value.findIndex((w: World) => w.id === updatedWorld.id);
           if (index !== -1) {
               worlds.value[index] = updatedWorld;
           }

         } else {
           // Create
           // Ověříme, zda jméno není prázdné (i když je 'required' v HTML)
           if (!worldForm.name.trim()) {
               formError.value = "World name cannot be empty.";
               return;
           }
           const newWorldData: WorldCreate = {
               // worldForm.name je zaručeně string
               name: worldForm.name,
               description: worldForm.description
           };
           const newWorld = await worldsApi.createWorld(newWorldData);
           worlds.value.push(newWorld);
         }
         closeModal();
       } catch(err: any) {
          formError.value = typeof err === 'string' ? err : (err?.message || (editingWorld.value ? 'Failed to update world.' : 'Failed to create world.'));
          console.error("Save World Error:", err);
       }
    };

    const confirmDelete = (world: World) => {
        worldToDelete.value = world;
        deleteError.value = null; // Resetuj chybu při otevření modalu
    };

    const handleDeleteWorld = async () => {
      if (!worldToDelete.value) return;
      deleteError.value = null;
      try {
          await worldsApi.deleteWorld(worldToDelete.value.id);
          worlds.value = worlds.value.filter((w: World) => w.id !== worldToDelete.value!.id);
          worldToDelete.value = null; // Zavřít modal
      } catch (err: any) {
           deleteError.value = typeof err === 'string' ? err : (err?.message || 'Failed to delete world.');
           console.error("Delete World Error:", err);
      }
    };


    onMounted(loadWorlds);

    return {
      worlds,
      loading,
      error,
      formError,
      deleteError,
      showAddWorldModal,
      editingWorld,
      worldToDelete,
      worldForm,
      // loadWorlds, // Není potřeba exportovat, volá se v onMounted
      closeModal,
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
  background-color: #f8f9fa; /* Světlejší pozadí pro kontrast */
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6; /* Decentní oddělovač */
}

.view-header h1 {
  margin: 0;
  color: #343a40; /* Tmavší barva pro nadpis */
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem; /* Mezera mezi ikonou a textem */
  transition: background-color 0.2s ease;
}

.btn .icon {
 font-style: normal; /* Zajistí, že ikona nebude kurzívou */
}


.btn-primary {
  background-color: #7851a9; /* Hlavní barva aplikace */
  color: white;
}
.btn-primary:hover {
  background-color: #5f3f87; /* Tmavší odstín pro hover */
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

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
}

.world-list-container {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.world-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.world-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}
.world-list-item:last-child {
  border-bottom: none;
}

.world-info h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: #495057;
}

.world-info p {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.5rem; /* Přidáme mezeru pod popisem */
}

.world-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center; /* Zarovnání tlačítek na střed */
}

.world-campaigns {
  margin-top: 0.5rem;
  font-size: 0.85rem;
}

.world-campaigns strong {
  color: #495057;
}

.world-campaigns ul {
  list-style: disc;
  margin: 0.25rem 0 0 1.2rem; /* Odsazení seznamu */
  padding: 0;
}

.world-campaigns li {
   color: #6c757d;
}

.world-campaigns-empty {
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #adb5bd; /* Světlejší barva pro prázdnou zprávu */
    font-style: italic;
}

/* Styly pro modál - zjednodušené, použijte vaše existující nebo knihovnu */
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

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
   color: #495057;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  box-sizing: border-box; /* Aby padding nezvětšoval šířku */
}
.form-group textarea {
    min-height: 80px;
    resize: vertical;
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
}

.error-message {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 1rem;
  text-align: center; /* Centrování chybové hlášky v modalu */
}

/* Přidáme styl pro nové tlačítko, pokud nemáte obecný .btn-info */
.btn-info {
  background-color: #17a2b8;
  color: white;
}
.btn-info:hover {
   background-color: #138496;
}

</style> 