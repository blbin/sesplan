<template>
  <div>
    <!-- Sessions Section -->
    <section class="sessions-section detail-section">
      <div class="section-header">
        <h2>Sessions</h2>
        <button v-if="isCurrentUserGM" @click="openAddSessionModal" class="btn btn-primary btn-sm">Add Session</button>
      </div>
      <div v-if="sessionsLoading" class="loading-state small">Loading sessions...</div>
      <div v-else-if="sessionsError" class="error-message small">{{ sessionsError }}</div>
      <div v-else-if="sessions.length === 0">No sessions scheduled for this campaign yet.</div>
      <ul v-else class="item-list session-list">
        <li v-for="session in sessions" :key="session.id" class="item-list-item">
          <router-link
            :to="{ name: 'SessionDetail', params: { campaignId: campaignId, sessionId: session.id } }"
            class="item-link"
          >
            <div class="item-info">
              <h3>{{ session.title }}</h3>
              <p v-if="session.date_time" class="session-date">Date: {{ formatFullDateTime(session.date_time) }}</p>
              <p v-if="session.description" class="session-description">{{ session.description }}</p>
              <p v-if="session.summary" class="session-summary">Summary: {{ session.summary }}</p>
              <small class="item-meta">Created: {{ formatDate(session.created_at) }}</small>
            </div>
          </router-link>
          <div class="item-actions" v-if="isCurrentUserGM">
            <button @click="openEditSessionModal(session)" class="btn btn-secondary btn-sm">Edit</button>
            <button @click="confirmDeleteSession(session)" class="btn btn-danger btn-sm">Delete</button>
          </div>
        </li>
      </ul>
    </section>

    <!-- Add/Edit Session Modal -->
    <div v-if="showSessionModal" class="modal-backdrop">
      <div class="modal">
        <h2>{{ editingSession ? 'Edit Session' : 'Add New Session' }}</h2>
        <form @submit.prevent="handleSaveSession">
          <div class="form-group">
            <label for="sessionTitle">Title:</label>
            <input type="text" id="sessionTitle" v-model="sessionForm.title" required>
          </div>
          <div class="form-group">
            <label for="sessionDateTime">Date & Time (Optional):</label>
            <input type="datetime-local" id="sessionDateTime" v-model="sessionForm.date_time">
          </div>
          <div class="form-group">
            <label for="sessionDescription">Description (Optional):</label>
            <textarea id="sessionDescription" v-model="sessionForm.description"></textarea>
          </div>
          <div class="form-group">
            <label for="sessionSummary">Summary (Optional):</label>
            <textarea id="sessionSummary" v-model="sessionForm.summary"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeSessionModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="!sessionForm.title.trim()">
              {{ editingSession ? 'Save Changes' : 'Create Session' }}
            </button>
          </div>
          <p v-if="sessionFormError" class="error-message">{{ sessionFormError }}</p>
        </form>
      </div>
    </div>

    <!-- Delete Session Confirmation Modal -->
    <div v-if="sessionToDelete" class="modal-backdrop">
      <div class="modal confirmation-modal">
        <h2>Confirm Deletion</h2>
        <p>Are you sure you want to delete the session "{{ sessionToDelete.title }}"?</p>
        <div class="modal-actions">
          <button type="button" @click="sessionToDelete = null" class="btn btn-secondary">Cancel</button>
          <button type="button" @click="handleDeleteSession" class="btn btn-danger">Delete</button>
        </div>
        <p v-if="deleteSessionError" class="error-message">{{ deleteSessionError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, defineProps, toRefs } from 'vue';
import * as sessionsApi from '@/services/api/sessions';
import type { Session, SessionCreate, SessionUpdate } from '@/types/session';

// Interface for Session form data
interface SessionFormData {
  title: string;
  description: string | null;
  summary: string | null;
  date_time: string | null; // Use string to bind with datetime-local input
}

const props = defineProps<{
  campaignId: number | string; // Může být string z URL parametru
  isCurrentUserGM: boolean | null; // <--- Změna: Povolit null
}>();

// Použijeme toRefs, abychom zajistili reaktivitu props v watch
const { campaignId, isCurrentUserGM } = toRefs(props);

// State for Sessions
const sessions = ref<Session[]>([]);
const sessionsLoading = ref(false);
const sessionsError = ref<string | null>(null);
const showSessionModal = ref(false);
const editingSession = ref<Session | null>(null);
const sessionToDelete = ref<Session | null>(null);
const sessionFormError = ref<string | null>(null);
const deleteSessionError = ref<string | null>(null);

const sessionForm = reactive<SessionFormData>({
  title: '',
  description: null,
  summary: null,
  date_time: null,
});

// Formátování data (jednoduchý příklad)
const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return dateString; // Fallback
  }
};

// Formatter for Date and Time
const formatFullDateTime = (dateString: string | null | undefined) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    // Zde můžeme specifikovat formát, např. včetně času
    return date.toLocaleString('cs-CZ', { // Příklad lokalizace
      year: 'numeric', month: 'numeric', day: 'numeric',
      hour: '2-digit', minute: '2-digit' 
    });
  } catch (e) {
    console.error("Error formatting date:", e);
    return dateString; // Fallback
  }
};

// Function to load sessions
const loadSessions = async (id: number | string) => {
  if (!id) return;
  const numericCampaignId = Number(id); // Ujistíme se, že máme číslo
  if (isNaN(numericCampaignId)) {
      sessionsError.value = "Invalid Campaign ID.";
      return;
  }
  sessionsLoading.value = true;
  sessionsError.value = null;
  sessions.value = [];
  try {
    sessions.value = await sessionsApi.getSessionsByCampaign(numericCampaignId);
  } catch (err: any) {
    sessionsError.value = `Failed to load sessions: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
    console.error("Load Sessions Error:", err);
  } finally {
    sessionsLoading.value = false;
  }
};

// Session Modal Logic
const resetSessionForm = () => {
  sessionForm.title = '';
  sessionForm.description = null;
  sessionForm.summary = null;
  sessionForm.date_time = null;
  editingSession.value = null;
  sessionFormError.value = null;
};

const openAddSessionModal = () => {
  resetSessionForm();
  showSessionModal.value = true;
};

const openEditSessionModal = (session: Session) => {
  editingSession.value = session;
  sessionForm.title = session.title;
  sessionForm.description = session.description ?? null;
  sessionForm.summary = session.summary ?? null;
  // Zpracování pro datetime-local input, který očekává 'YYYY-MM-DDTHH:mm'
  sessionForm.date_time = session.date_time ? new Date(new Date(session.date_time).getTime() - (new Date().getTimezoneOffset() * 60000)).toISOString().slice(0, 16) : null;
  sessionFormError.value = null;
  showSessionModal.value = true;
};

const closeSessionModal = () => {
  showSessionModal.value = false;
  resetSessionForm();
};

const handleSaveSession = async () => {
  const numericCampaignId = Number(campaignId.value);
   if (isNaN(numericCampaignId)) {
     sessionFormError.value = "Invalid Campaign ID.";
     return;
   }
  sessionFormError.value = null;

  // Pokud je date_time prázdný string, pošli null. Jinak normalizuj na ISO string UTC.
  let dateTimeToSend: string | null = null;
  if (sessionForm.date_time) {
    try {
      // Převede lokální čas z inputu na UTC ISO string
      dateTimeToSend = new Date(sessionForm.date_time).toISOString();
    } catch (e) {
       console.error("Invalid date format:", sessionForm.date_time);
       sessionFormError.value = "Invalid date format provided.";
       return;
    }
  }


  try {
    if (editingSession.value) {
      // Update
      const payload: SessionUpdate = {};
      if (sessionForm.title !== editingSession.value.title) {
        payload.title = sessionForm.title;
      }
      if (sessionForm.description !== editingSession.value.description) {
        payload.description = sessionForm.description === undefined ? null : sessionForm.description;
      }
      if (sessionForm.summary !== editingSession.value.summary) {
        payload.summary = sessionForm.summary === undefined ? null : sessionForm.summary;
      }
      // Porovnávej normalizované ISO stringy nebo null
       let originalDateTimeISO: string | null = null;
       if (editingSession.value.date_time) {
           try {
               originalDateTimeISO = new Date(editingSession.value.date_time).toISOString();
           } catch {} // Ignoruj chybu, pokud původní datum není validní
       }
       if (dateTimeToSend !== originalDateTimeISO) {
          payload.date_time = dateTimeToSend;
       }


      if (Object.keys(payload).length > 0) {
        const updatedSession = await sessionsApi.updateSession(editingSession.value.id, payload);
        const index = sessions.value.findIndex(s => s.id === updatedSession.id);
        if (index !== -1) {
          sessions.value[index] = updatedSession;
        }
      } else {
        console.log("No changes detected for session update.");
      }
    } else {
      // Create
      if (!sessionForm.title.trim()) {
        sessionFormError.value = "Session title cannot be empty.";
        return;
      }
      const sessionCreateData: SessionCreate = {
        title: sessionForm.title,
        description: sessionForm.description,
        summary: sessionForm.summary,
        date_time: dateTimeToSend,
        campaign_id: numericCampaignId,
      };
      const newSession = await sessionsApi.createSession(sessionCreateData);
      sessions.value.unshift(newSession); // Přidáme na začátek seznamu
      sessions.value.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()); // Seřadíme znovu
    }
    closeSessionModal();
  } catch (err: any) {
    console.error("Save Session Error:", err);
    sessionFormError.value = `Failed to save session: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
  }
};

// Delete Session Logic
const confirmDeleteSession = (session: Session) => {
  sessionToDelete.value = session;
  deleteSessionError.value = null;
};

const handleDeleteSession = async () => {
  if (!sessionToDelete.value) return;
  deleteSessionError.value = null;
  try {
    await sessionsApi.deleteSession(sessionToDelete.value.id);
    sessions.value = sessions.value.filter(s => s.id !== sessionToDelete.value!.id);
    sessionToDelete.value = null; // Close confirmation modal
  } catch (err: any) {
    console.error("Delete Session Error:", err);
    deleteSessionError.value = `Failed to delete session: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
  }
};

// Watch for campaignId changes to load sessions
watch(
  campaignId,
  (newId) => {
    if (newId) {
      loadSessions(newId);
    } else {
        // Clear sessions if campaignId becomes invalid/null
        sessions.value = [];
        sessionsError.value = "No campaign selected.";
        sessionsLoading.value = false;
    }
  },
  { immediate: true } // Load sessions immediately when the component mounts
);

</script>

<style scoped>
/* Přesunuté a upravené styly specifické pro Session Manager */
.detail-section {
  /* margin-bottom: 2rem; Odstraněno, aby to nezpůsobovalo dvojitou mezeru */
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h2 {
  font-size: 1.2rem;
  color: #495057;
  margin-bottom: 0.75rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #e9ecef; /* Vráceno sem pro vizuální oddělení nadpisu sekce */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
   margin: 0;
   border-bottom: none; /* Zrušíme dvojité podtržení nadpisu */
}

.session-list {
    margin-top: 1rem;
}

.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.item-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* Změněno na flex-start pro lepší zarovnání */
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}

.item-list-item:last-child {
  border-bottom: none;
}

.item-link {
    text-decoration: none;
    color: inherit;
    flex-grow: 1; /* Odkaz zabere dostupný prostor */
    margin-right: 1rem; /* Mezera mezi odkazem a akcemi */
}

.item-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem; /* Mírně menší */
  font-weight: 600;
  color: #333;
}

.item-info p {
    margin: 0.3rem 0;
    color: #555;
    line-height: 1.5;
    font-size: 0.9rem; /* Mírně menší */
}

.item-info .session-date {
    font-weight: 500;
    color: #0056b3; /* Zvýraznění data */
    font-size: 0.85rem;
}

.item-info .session-description {
    color: #444;
}

.item-info .session-summary {
    font-style: italic;
    color: #666;
    margin-top: 0.5rem;
    font-size: 0.85rem;
}

.item-info .item-meta {
    font-size: 0.75rem;
    color: #777;
    margin-top: 0.5rem;
}

.item-actions {
    /* margin-left: 1rem; Odstraněno, použijeme margin-right na item-link */
    white-space: nowrap;
    display: flex;
    flex-direction: column; /* Tlačítka pod sebou */
    align-items: flex-end; /* Zarovnání tlačítek doprava */
    gap: 0.5rem;
    flex-shrink: 0; /* Akce se nesmrsknou */
}

/* Modal Styles - Zkopírováno a mírně upraveno */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000; /* Ujistíme se, že je nad ostatním obsahem */
}

.modal {
  background-color: white;
  padding: 2rem 2.5rem;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group input[type="text"],
.form-group input[type="datetime-local"],
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  box-sizing: border-box; /* Přidáno pro konzistentní velikost */
  font-size: 1rem;
}
.form-group input:focus,
.form-group textarea:focus {
    border-color: #80bdff;
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}


.form-group textarea {
    min-height: 80px; /* Mírně menší */
    resize: vertical; /* Povolit pouze vertikální změnu velikosti */
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem; /* Přidáno odsazení shora */
  border-top: 1px solid #e9ecef; /* Oddělovač */
}

.confirmation-modal p {
    margin-bottom: 1.5rem; /* Větší mezera pod textem */
    line-height: 1.6;
    color: #333;
}
/* .confirmation-modal p strong { */
    /* margin-right: 0.5em; - Není potřeba, název je v uvozovkách */
/* } */

/* Shared Error/Loading Styles */
.loading-state.small,
.error-message.small {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    text-align: left;
    margin-top: 0.5rem;
    border-radius: 0.25rem;
}
.loading-state.small {
    color: #6c757d;
    background-color: #f8f9fa;
}
.error-message { /* Obecná chybová zpráva (např. u formuláře) */
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 0.75rem 1rem;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
  font-size: 0.9rem;
}
.error-message.small { /* Menší verze pro seznam */
    padding: 0.5rem 1rem;
    margin-top: 1rem;
}

/* Button styles - zkopírováno pro konzistenci */
.btn { padding: 0.6rem 1.2rem; border-radius: 0.3rem; cursor: pointer; border: none; font-weight: 500; text-decoration: none; transition: background-color 0.2s ease, box-shadow 0.2s ease; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem; line-height: 1; }
.btn:disabled { opacity: 0.65; cursor: not-allowed; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:not(:disabled):hover { background-color: #0056b3; }
.btn-primary:focus { box-shadow: 0 0 0 0.2rem rgba(38,143,255,.5); outline: none; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:not(:disabled):hover { background-color: #5a6268; }
.btn-secondary:focus { box-shadow: 0 0 0 0.2rem rgba(130,138,145,.5); outline: none; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:not(:disabled):hover { background-color: #c82333; }
.btn-danger:focus { box-shadow: 0 0 0 0.2rem rgba(225,83,97,.5); outline: none; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; border-radius: 0.2rem; }

</style> 