<template>
  <div class="session-list-view">
    <h1>My Sessions</h1>
    
    <div v-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <p>Loading sessions...</p>
    </div>
    
    <v-alert v-else-if="error" type="error" class="mb-4">
      {{ error }}
    </v-alert>
    
    <div v-else-if="sessions.length > 0">
      <v-list lines="two">
        <v-list-item 
          v-for="session in sessions" 
          :key="session.id"
          :title="session.title || 'Untitled Session'"
          :subtitle="`Campaign: ${session.campaign?.name || 'N/A'} - Date: ${formatFullDateTime(session.date_time)}`"
          @click="goToSessionDetail(session)"
        >
          <template v-slot:prepend>
            <v-icon>mdi-calendar-clock</v-icon>
          </template>
           <template v-slot:append>
                <v-icon>mdi-chevron-right</v-icon>
           </template>
        </v-list-item>
      </v-list>
    </div>
    
    <v-alert v-else type="info">
      You are not part of any sessions yet, or no sessions have been scheduled in your campaigns.
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import * as sessionsApi from '@/services/api/sessions'; 
import type { Session } from '@/types/session';
import { VProgressCircular, VAlert, VList, VListItem, VIcon } from 'vuetify/components'; // Explicit Vuetify imports

// State
const sessions = ref<Session[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);
const router = useRouter();

// Methods
const loadSessions = async () => {
  loading.value = true;
  error.value = null;
  try {
    sessions.value = await sessionsApi.getMySessions(); // Use the new API call
    // console.warn("getMySessions API call not implemented yet."); 
    // --- Placeholder Data (Removed) ---
    // await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading
    // sessions.value = []; // Start with empty for now
    // --- End Placeholder Data ---

  } catch (err: any) {
    console.error("Error loading user sessions:", err);
    error.value = `Failed to load sessions: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    sessions.value = []; // Clear sessions on error
  } finally {
    loading.value = false;
  }
};

const goToSessionDetail = (session: Session) => {
  if (session.id && session.campaign_id) {
    router.push({ 
      name: 'SessionDetail', 
      params: { 
        campaignId: session.campaign_id.toString(), 
        sessionId: session.id.toString() 
      } 
    });
  } else {
     console.error("Cannot navigate to session detail: Missing session ID or campaign ID", session);
     error.value = "Could not navigate to the selected session. Please try again.";
  }
};

const formatFullDateTime = (dateString: string | null | undefined): string => {
    if (!dateString) return 'Not scheduled';
    try {
        const date = new Date(dateString);
        // Check if the date is valid after parsing
        if (isNaN(date.getTime())) {
             return 'Invalid date';
        }
        return date.toLocaleString(); // Use locale-specific format
    } catch (e) {
        console.error("Error formatting date:", e);
        return dateString; // Return original string if formatting fails
    }
};


// Lifecycle Hooks
onMounted(() => {
  loadSessions();
});
</script>

<style scoped>
.session-list-view {
  padding: 1rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6c757d;
}

.loading-state p {
  margin-top: 1rem;
}

/* Add more styles as needed */
</style> 