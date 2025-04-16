<template>
  <div class="campaigns-view">
    <header class="view-header">
      <h1>My Campaigns</h1>
      <button @click="openAddModal" class="btn btn-primary">
        <i class="icon">+</i> Add New Campaign
      </button>
    </header>

    <div class="list-container">
      <p v-if="loading">Loading campaigns...</p>
      <p v-if="worldError && !loading" class="error-message">Could not load world names: {{ worldError }}</p>
      <p v-else-if="error" class="error-message">{{ error }}</p>
      <div v-else-if="campaigns.length === 0">
        You haven't created any campaigns yet.
      </div>
      <ul v-else class="item-list">
        <li v-for="campaign in campaigns" :key="campaign.id" class="item-list-item">
          <div class="item-info">
            <h2>
              <router-link :to="`/dashboard/campaigns/${campaign.id}`" class="item-link">
                {{ campaign.name }}
              </router-link>
            </h2>
            <p>{{ campaign.description || 'No description' }}</p>
            <small class="world-info">World: {{ getWorldName(campaign.world_id) }}</small>
          </div>
          <div class="item-actions">
            <button @click="openEditModal(campaign)" class="btn btn-secondary btn-sm">Edit</button>
            <button @click="confirmDelete(campaign)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Modál pro přidání/úpravu kampaně -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal">
        <h2>{{ editingCampaign ? 'Edit Campaign' : 'Add New Campaign' }}</h2>
        <form @submit.prevent="handleSaveCampaign">
          <!-- Výběr světa (pouze při vytváření) -->
          <div v-if="!editingCampaign" class="form-group">
             <label for="campaignWorld">World:</label>
             <select id="campaignWorld" v-model="campaignForm.world_id" required>
                <option disabled value="">Please select a world</option>
                <option v-for="world in availableWorlds" :key="world.id" :value="world.id">
                  {{ world.name }}
                </option>
             </select>
             <p v-if="loadingWorlds">Loading worlds...</p>
             <p v-if="worldError" class="error-message">{{ worldError }}</p>
          </div>

          <div class="form-group">
            <label for="campaignName">Name:</label>
            <input type="text" id="campaignName" v-model="campaignForm.name" required>
          </div>
          <div class="form-group">
            <label for="campaignDescription">Description:</label>
            <textarea id="campaignDescription" v-model="campaignForm.description"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!editingCampaign && !campaignForm.world_id">
              {{ editingCampaign ? 'Save Changes' : 'Create Campaign' }}
            </button>
          </div>
           <p v-if="formError" class="error-message">{{ formError }}</p>
        </form>
      </div>
    </div>

     <!-- Modál pro potvrzení smazání -->
    <div v-if="campaignToDelete" class="modal-backdrop">
      <div class="modal confirmation-modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete the campaign "{{ campaignToDelete.name }}"? This action cannot be undone.</p>
         <div class="modal-actions">
            <button type="button" @click="campaignToDelete = null" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="handleDeleteCampaign" class="btn btn-danger">Delete</button>
          </div>
           <p v-if="deleteError" class="error-message">{{ deleteError }}</p>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from 'vue';
import * as campaignsApi from '@/services/api/campaigns';
import * as worldsApi from '@/services/api/worlds'; // Potřebujeme pro načtení světů
import type { Campaign, CampaignCreate, CampaignUpdate } from '@/types/campaign';
import type { World } from '@/types/world'; // Potřebujeme typ World

// Typ pro formulář kampaně
interface CampaignFormData {
  name: string;
  description: string | null;
  world_id: number | null; // Musí být null initialně pro select
}

export default defineComponent({
  name: 'CampaignsView',
  setup() {
    const campaigns = ref<Campaign[]>([]);
    const availableWorlds = ref<World[]>([]);
    const loading = ref(true);
    const loadingWorlds = ref(false);
    const error = ref<string | null>(null);
    const worldError = ref<string | null>(null); // Chyba při načítání světů
    const formError = ref<string | null>(null);
    const deleteError = ref<string | null>(null);

    const showModal = ref(false);
    const editingCampaign = ref<Campaign | null>(null);
    const campaignToDelete = ref<Campaign | null>(null);

    const campaignForm = reactive<CampaignFormData>({
      name: '',
      description: null,
      world_id: null // Důležité pro select
    });

    const loadCampaigns = async () => {
      loading.value = true;
      error.value = null;
      try {
        // Načteme všechny kampaně vlastněné uživatelem
        campaigns.value = await campaignsApi.getCampaigns();
      } catch (err: any) {
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load campaigns.');
        console.error("Load Campaigns Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const loadWorlds = async () => {
        loadingWorlds.value = true;
        worldError.value = null;
        try {
            availableWorlds.value = await worldsApi.getWorlds();
        } catch (err: any) {
            worldError.value = typeof err === 'string' ? err : (err?.message || 'Failed to load worlds.');
            console.error("Load Worlds Error:", err);
        } finally {
            loadingWorlds.value = false;
        }
    };

    const resetForm = () => {
      campaignForm.name = '';
      campaignForm.description = null;
      campaignForm.world_id = null; // Resetovat i world_id
      editingCampaign.value = null;
      formError.value = null;
    };

    const closeModal = () => {
      showModal.value = false;
      resetForm();
    };

     const openAddModal = () => {
        resetForm();
        editingCampaign.value = null;
        showModal.value = true;
        if (availableWorlds.value.length === 0 && !loadingWorlds.value) {
            loadWorlds(); 
        }
    };


     const openEditModal = (campaign: Campaign) => {
      editingCampaign.value = campaign;
      campaignForm.name = campaign.name;
      campaignForm.description = campaign.description;
      campaignForm.world_id = campaign.world_id; // Nastavit pro informaci, i když se nemění
      showModal.value = true;
    };

    const getWorldName = (worldId: number): string => {
        const world = availableWorlds.value.find(w => w.id === worldId);
        return world ? world.name : `ID: ${worldId}`;
    };

    const handleSaveCampaign = async () => {
       formError.value = null;
       try {
         if (editingCampaign.value) {
           // Update
           const campaignDataToUpdate: CampaignUpdate = {};
           if (campaignForm.name !== editingCampaign.value.name) {
               campaignDataToUpdate.name = campaignForm.name;
           }
           if (campaignForm.description !== editingCampaign.value.description) {
               campaignDataToUpdate.description = campaignForm.description;
           }

           if (Object.keys(campaignDataToUpdate).length === 0) {
               closeModal();
               return;
           }

           const updatedCampaign = await campaignsApi.updateCampaign(editingCampaign.value.id, campaignDataToUpdate);
           const index = campaigns.value.findIndex(c => c.id === updatedCampaign.id);
           if (index !== -1) {
               campaigns.value[index] = updatedCampaign;
           }
         } else {
           // Create
           if (!campaignForm.name.trim()) {
                formError.value = "Campaign name cannot be empty.";
                return;
           }
           if (!campaignForm.world_id) {
               formError.value = "Please select a world for the campaign.";
               return;
           }
           const newCampaignData: CampaignCreate = {
               name: campaignForm.name,
               description: campaignForm.description,
               world_id: campaignForm.world_id // world_id je nyní číslo
           };
           const newCampaign = await campaignsApi.createCampaign(newCampaignData);
           campaigns.value.push(newCampaign);
         }
         closeModal();
       } catch(err: any) {
          formError.value = typeof err === 'string' ? err : (err?.message || (editingCampaign.value ? 'Failed to update campaign.' : 'Failed to create campaign.'));
          console.error("Save Campaign Error:", err);
       }
    };

    const confirmDelete = (campaign: Campaign) => {
        campaignToDelete.value = campaign;
        deleteError.value = null;
    };

    const handleDeleteCampaign = async () => {
      if (!campaignToDelete.value) return;
      deleteError.value = null;
      try {
          await campaignsApi.deleteCampaign(campaignToDelete.value.id);
          campaigns.value = campaigns.value.filter(c => c.id !== campaignToDelete.value!.id);
          campaignToDelete.value = null;
      } catch (err: any) {
           deleteError.value = typeof err === 'string' ? err : (err?.message || 'Failed to delete campaign.');
           console.error("Delete Campaign Error:", err);
      }
    };


    onMounted(() => {
        loadCampaigns();
        loadWorlds();
    });

    return {
      campaigns,
      availableWorlds,
      loading,
      loadingWorlds,
      error,
      worldError,
      formError,
      deleteError,
      showModal,
      editingCampaign,
      campaignToDelete,
      campaignForm,
      closeModal,
      openAddModal,
      openEditModal,
      handleSaveCampaign,
      confirmDelete,
      handleDeleteCampaign,
      getWorldName,
    };
  }
});
</script>

<style scoped>
/* Použijeme stejné styly jako pro WorldsView, ale s jinými názvy tříd pro přehlednost */
.campaigns-view {
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

.list-container { /* Dříve world-list-container */
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.item-list { /* Dříve world-list */
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-list-item { /* Dříve world-list-item */
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* Zarovnání nahoru pro případ delšího textu */
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}
.item-list-item:last-child {
  border-bottom: none;
}

.item-info { /* Dříve world-info */
    flex-grow: 1;
    margin-right: 1rem; /* Mezera mezi info a actions */
}

.item-info h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  color: #495057;
}

.item-info p {
  margin: 0 0 0.5rem 0; /* Mezera pod popisem */
  font-size: 0.9rem;
  color: #6c757d;
}

.item-info .world-info { /* Styl pro World Info */
    font-size: 0.85rem; /* Mírně zvětšíme */
    color: #6c757d; /* Změníme barvu */
    display: block;
    margin-top: 0.25rem; /* Malá mezera nad */
}


.item-actions { /* Dříve world-actions */
  display: flex;
  flex-shrink: 0; /* Aby se tlačítka nezmenšovala */
  gap: 0.5rem;
}


/* Styly pro modál a tlačítka - přebíráme z WorldsView */
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
}
.btn .icon { font-style: normal; }
.btn-primary { background-color: #7851a9; color: white; }
.btn-primary:hover { background-color: #5f3f87; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }

.modal-backdrop {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0, 0, 0, 0.5); display: flex;
  justify-content: center; align-items: center; z-index: 1000;
}
.modal {
  background-color: white; padding: 2rem; border-radius: 0.5rem;
  min-width: 300px; max-width: 500px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
.modal h2 { margin-top: 0; margin-bottom: 1.5rem; color: #343a40; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #495057; }
.form-group input[type="text"],
.form-group textarea,
.form-group select { /* Přidáno pro select */
  width: 100%; padding: 0.5rem; border: 1px solid #ced4da;
  border-radius: 0.25rem; box-sizing: border-box; font-size: 0.9rem; /* Sjednotíme velikost */
}
.form-group textarea { min-height: 80px; resize: vertical; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1.5rem;
  padding-top: 1rem; border-top: 1px solid #e9ecef;
}
.confirmation-modal p { margin-bottom: 1.5rem; color: #495057; }
.error-message { color: #dc3545; font-size: 0.9rem; margin-top: 1rem; text-align: center; }

/* Přidáme styl pro odkazy v seznamu */
.item-link {
  color: inherit; /* Dědí barvu z h2 */
  text-decoration: none;
}
.item-link:hover {
  color: #7851a9; /* Zvýraznění při hover */
  text-decoration: underline;
}

</style> 