<template>
  <div class="session-detail-view">
    <div v-if="loading" class="loading-state">Loading session details...</div>
    <div v-else-if="error" class="error-message">
      Error loading session: {{ error }}
    </div>
    <div v-else-if="session" class="session-content">
      <header class="view-header">
        <h1>{{ session.title }}</h1>
        <router-link 
          :to="{ name: 'CampaignDetail', params: { campaignId: props.campaignId } }"
          class="btn btn-secondary"
        >
          &larr; Back to Campaign
        </router-link>
      </header>

      <div class="session-details">
        <section class="detail-section">
          <h2>Details</h2>
          <ul>
            <li v-if="session.date_time"><strong>Date & Time:</strong> {{ formatFullDateTime(session.date_time) }}</li>
            <li><strong>Campaign ID:</strong> {{ session.campaign_id }}</li>
            <li><strong>Created:</strong> {{ formatDate(session.created_at) }}</li>
            <li><strong>Last Updated:</strong> {{ formatDate(session.updated_at) }}</li>
          </ul>
        </section>
        
        <section v-if="session.description" class="detail-section">
          <h2>Description</h2>
          <p>{{ session.description }}</p>
        </section>

        <section v-if="session.summary" class="detail-section">
          <h2>Summary</h2>
          <p>{{ session.summary }}</p>
        </section>

        <!-- TODO: Add sections for related entities like characters, journal entries, etc. -->

      </div>

      <!-- New Availability Section -->
      <section class="detail-section availability-section">
        <h2>Dostupnost</h2>

        <!-- GM Slot Management -->
        <div v-if="isCurrentUserGM">
          <h3>Spravovat časové sloty</h3>
          <GMAvailabilityManager 
            :session-id="numericSessionId"
            :existing-slots="sessionSlots"
            @slots-updated="loadAvailabilityData" 
          />
        </div>
        
        <!-- Availability Grid -->
        <div v-if="!availabilityLoading && !availabilityError">
          <AvailabilityDisplayGrid
            v-if="currentUserId && sessionSlots.length > 0"
            :session-id="numericSessionId"
          :current-user-id="currentUserId"
            :is-gm="!!isCurrentUserGM"
            :slots="sessionSlots"
            :user-availabilities="userAvailabilities"
            @availability-changed="handleAvailabilityChange" 
          />
          <p v-else-if="sessionSlots.length === 0 && !isCurrentUserGM">
            Zatím nebyly definovány žádné časové sloty pro zadání dostupnosti.
          </p>
           <p v-else-if="sessionSlots.length === 0 && isCurrentUserGM">
            Zatím jste nedefinovali žádné časové sloty. Můžete je přidat výše.
          </p>
          <p v-else>Pro zadání dostupnosti musíte být přihlášen.</p>
        </div>
        <p v-else-if="availabilityLoading">Načítání dostupnosti...</p>
        <p v-else-if="availabilityError" class="text-error">Chyba načítání dostupnosti: {{ availabilityError }}</p>
      </section>

    </div>
    <div v-else class="not-found">
      Session not found.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import * as sessionsApi from '@/services/api/sessions';
import * as availabilityApi from '@/services/api/sessionAvailability';
import * as campaignMembersApi from '@/services/api/campaignMembers';
import type { Session } from '@/types/session';
import type { SessionSlot } from '@/types/session_slot';
import type { UserAvailability } from '@/types/user_availability';
import type { UserCampaignRead } from '@/types/user_campaign';
import { useAuthStore } from '@/store/auth.store';
import { CampaignRoleEnum } from '@/types/campaign_role';
import GMAvailabilityManager from '@/components/campaign/GMAvailabilityManager.vue';
import AvailabilityDisplayGrid from '@/components/campaign/AvailabilityDisplayGrid.vue';

// --- Props Definition --- 
const props = defineProps<{ 
    campaignId: string | number;
    sessionId: string | number;
}>();

// --- State --- 
const authStore = useAuthStore();
const session = ref<Session | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const sessionSlots = ref<SessionSlot[]>([]);
const userAvailabilities = ref<UserAvailability[]>([]);
const availabilityLoading = ref(true);
const availabilityError = ref<string | null>(null);
const currentUserMembership = ref<UserCampaignRead | null>(null);
const membershipLoading = ref(false);

// --- Computed Properties --- 
const currentUserId = computed(() => authStore.user?.id);
const numericSessionId = computed(() => Number(props.sessionId));
const isCurrentUserGM = computed(() => {
  return currentUserMembership.value?.role === CampaignRoleEnum.GM;
});

// --- Methods --- 
const loadSessionDetail = async () => {
  if (!numericSessionId.value) return;
  loading.value = true;
  error.value = null;
  session.value = null;
  try {
    session.value = await sessionsApi.getSessionById(numericSessionId.value);
    if (session.value && !currentUserMembership.value && !membershipLoading.value) { 
         await loadCurrentUserMembership(session.value.campaign_id);
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load session details';
    console.error("Load Session Detail Error:", err);
  } finally {
    loading.value = false;
  }
};

const loadAvailabilityData = async () => {
    if (!numericSessionId.value) return;
    availabilityLoading.value = true;
    availabilityError.value = null;
    try {
        [sessionSlots.value, userAvailabilities.value] = await Promise.all([
            availabilityApi.getSlots(numericSessionId.value),
            availabilityApi.getAllSessionAvailabilities(numericSessionId.value)
        ]);
    } catch (err: any) {
        availabilityError.value = err.message || 'Failed to load availability data';
        console.error("Load Availability Data Error:", err);
        sessionSlots.value = [];
        userAvailabilities.value = [];
    } finally {
        availabilityLoading.value = false;
    }
};

const loadCurrentUserMembership = async (campId: number) => {
    if (!currentUserId.value || !campId) return;
    membershipLoading.value = true;
    currentUserMembership.value = null;
    try {
        currentUserMembership.value = await campaignMembersApi.getCurrentUserMembership(campId);
    } catch (err: any) {
        console.error("Could not load current user membership:", err);
        error.value = err.response?.data?.detail || err.message || 'Failed to load membership details';
    } finally {
        membershipLoading.value = false;
    }
};

const handleAvailabilityChange = () => {
    console.log("Availability changed, refreshing data...");
    loadAvailabilityData();
};

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return dateString;
  }
};

const formatFullDateTime = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';
    try {
        const date = new Date(dateString);
        return date.toLocaleString();
    } catch (e) {
        console.error("Error formatting date:", e);
        return dateString;
    }
};

// --- Lifecycle Hooks --- 
onMounted(() => {
  loadSessionDetail();
  loadAvailabilityData();
});

// --- Watchers --- 
watch(
  () => props.sessionId,
  (newId) => {
    if (newId) {
      loadSessionDetail();
      loadAvailabilityData();
    }
  },
  { immediate: false } 
);
 watch(
  () => props.campaignId,
  (newCampId) => {
      if (newCampId && !currentUserMembership.value && !membershipLoading.value && !loading.value && session.value?.campaign_id === Number(newCampId)) {
          loadCurrentUserMembership(Number(newCampId));
      }
  },
  { immediate: false } 
 );

</script>

<style scoped>
/* Basic styling - adapt from CampaignDetailView or create new */
.session-detail-view {
  padding: 2rem;
}

.session-content {
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

.availability-section h2 {
    margin-bottom: 1rem;
}
.availability-section h3 {
    font-size: 1.1rem;
    color: #666;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
}
.text-error {
    color: rgb(var(--v-theme-error));
}
</style> 