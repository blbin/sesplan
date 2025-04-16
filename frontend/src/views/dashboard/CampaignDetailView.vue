<template>
  <div class="campaign-detail-view">
    <div v-if="loading" class="loading-state">Loading campaign details...</div>
    <div v-else-if="error" class="error-message">
      Error loading campaign: {{ error }}
    </div>
    <div v-else-if="campaign" class="campaign-content">
      <header class="view-header">
        <h1>{{ campaign.name }}</h1>
        <!-- Tlačítko Zpět (volitelné) -->
        <router-link to="/dashboard/campaigns" class="btn btn-secondary">
          &larr; Back to Campaigns
        </router-link>
      </header>

      <div class="campaign-details">
        <section class="detail-section">
          <h2>Description</h2>
          <p>{{ campaign.description || 'No description provided.' }}</p>
        </section>

        <section class="detail-section">
          <h2>Details</h2>
          <ul>
            <li><strong>World:</strong> {{ worldName }}</li>
            <li><strong>Owner ID:</strong> {{ campaign.owner_id }}</li>
            <li><strong>Created:</strong> {{ formatDate(campaign.created_at) }}</li>
            <li><strong>Last Updated:</strong> {{ formatDate(campaign.updated_at) }}</li>
          </ul>
        </section>

        <!-- Zde můžete přidat další sekce, např. pro sezení, postavy, poznámky atd. -->

      </div>
    </div>
    <div v-else class="not-found">
      Campaign not found.
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import * as campaignsApi from '@/services/api/campaigns';
import * as worldsApi from '@/services/api/worlds'; // Pro načtení jména světa
import type { Campaign } from '@/types/campaign';
import type { World } from '@/types/world';

export default defineComponent({
  name: 'CampaignDetailView',
  props: {
    // Díky props: true v routeru můžeme přijmout ID jako prop
    campaignId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const campaign = ref<Campaign | null>(null);
    const world = ref<World | null>(null); // Pro uložení informací o světě
    const loading = ref(true);
    const error = ref<string | null>(null);
    const loadingWorld = ref(false);

    const loadCampaignDetail = async (id: number) => {
      loading.value = true;
      error.value = null;
      campaign.value = null; // Reset před načítáním
      world.value = null; // Reset světa
      loadingWorld.value = false;
      try {
        campaign.value = await campaignsApi.getCampaignById(id);
        // Pokud se kampaň načetla, načteme i detail světa
        if (campaign.value) {
            await loadWorldDetail(campaign.value.world_id);
        }
      } catch (err: any) {
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load campaign details.');
        console.error("Load Campaign Detail Error:", err);
      } finally {
        loading.value = false;
      }
    };

    const loadWorldDetail = async (worldId: number) => {
        loadingWorld.value = true;
         try {
            world.value = await worldsApi.getWorldById(worldId);
         } catch (err: any) {
             console.error("Load World Detail Error:", err);
             // Chybu světa nemusíme nutně zobrazovat jako hlavní chybu stránky
             // Můžeme zobrazit jen ID světa jako fallback
         } finally {
            loadingWorld.value = false;
         }
    };

    // Formátování data (jednoduchý příklad)
    const formatDate = (dateString: string) => {
      if (!dateString) return 'N/A';
      try {
        return new Date(dateString).toLocaleDateString();
      } catch (e) {
        return dateString; // Fallback na původní string
      }
    };

    const worldName = computed(() => {
        if (loadingWorld.value) return 'Loading world...';
        return world.value ? world.value.name : `ID: ${campaign.value?.world_id}`;
    });

    // Sledování změn ID v URL (pokud by uživatel navigoval mezi detaily)
    watch(
        () => props.campaignId,
        (newId) => {
            if (newId) {
            loadCampaignDetail(Number(newId));
            }
        },
        { immediate: true } // Spustí se i při prvním načtení
    );

    return {
      campaign,
      loading,
      error,
      worldName,
      formatDate,
    };
  },
});
</script>

<style scoped>
.campaign-detail-view {
  padding: 2rem;
}

.campaign-content {
  background-color: #fff;
  padding: 1.5rem 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section h2 {
  font-size: 1.2rem;
  color: #495057;
  margin-bottom: 0.75rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #e9ecef;
}

.detail-section p,
.detail-section ul {
  font-size: 0.95rem;
  color: #6c757d;
  line-height: 1.6;
}

.detail-section ul {
  list-style: none;
  padding: 0;
}
.detail-section li {
  margin-bottom: 0.5rem;
}
.detail-section li strong {
  color: #495057;
  margin-right: 0.5rem;
}

.loading-state,
.not-found {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 1rem;
  border-radius: 0.25rem;
}

/* Styly pro tlačítko Zpět (pokud je třeba) */
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
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
</style> 