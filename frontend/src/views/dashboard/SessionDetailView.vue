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
          :to="{ name: 'CampaignDetail', params: { campaignId: campaignId } }"
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
    </div>
    <div v-else class="not-found">
      Session not found.
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import * as sessionsApi from '@/services/api/sessions';
import type { Session } from '@/types/session';

export default defineComponent({
  name: 'SessionDetailView',
  props: {
    campaignId: {
      type: [String, Number],
      required: true,
    },
    sessionId: {
      type: [String, Number],
      required: true,
    },
  },
  setup(props) {
    const session = ref<Session | null>(null);
    const loading = ref(true);
    const error = ref<string | null>(null);

    const loadSessionDetail = async (id: number) => {
      loading.value = true;
      error.value = null;
      session.value = null;
      try {
        session.value = await sessionsApi.getSessionById(id);
      } catch (err: any) {
        error.value = `Failed to load session details: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Load Session Detail Error:", err);
      } finally {
        loading.value = false;
      }
    };

    // Helper function for simple date formatting
    const formatDate = (dateString: string | null | undefined) => {
      if (!dateString) return 'N/A';
      try {
        return new Date(dateString).toLocaleDateString();
      } catch (e) {
        return dateString;
      }
    };

    // Helper function for date and time formatting
    const formatFullDateTime = (dateString: string | null | undefined) => {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleString(); // Adjust locale/options as needed
        } catch (e) {
            console.error("Error formatting date:", e);
            return dateString; // Fallback
        }
    };

    // Load data when component mounts or props change
    onMounted(() => {
      loadSessionDetail(Number(props.sessionId));
    });

    watch(
      () => props.sessionId,
      (newId) => {
        if (newId) {
          loadSessionDetail(Number(newId));
        }
      }
    );

    return {
      session,
      loading,
      error,
      formatDate,
      formatFullDateTime,
      campaignId: props.campaignId // Pass campaignId for the back link
    };
  },
});
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

</style> 