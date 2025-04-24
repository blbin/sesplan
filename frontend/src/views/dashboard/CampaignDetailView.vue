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
            <li><strong>Created:</strong> {{ formatDate(campaign.created_at) }}</li>
            <li><strong>Last Updated:</strong> {{ formatDate(campaign.updated_at) }}</li>
          </ul>
        </section>

        <!-- Správa členů a pozvánek -->
        <div v-if="!loading && campaign && currentUserId" class="management-section">

            <CampaignMemberList
              :members="members"
              :campaignId="campaign.id"
              :canManage="isCurrentUserGM"
              :currentUserId="currentUserId"
              :loading="membersLoading"
              :error="membersError"
              @members-updated="handleMembersUpdated"
            />

            <template v-if="isCurrentUserGM">
              <!-- Tlačítko pro otevření modálu -->
              <div class="section-header">
                <h2>Invites</h2>
                <button @click="openInviteModal" class="btn btn-primary btn-sm">Invite User</button>
              </div>
              <!-- Přesunuto do modálu -->
              <!-- <CreateCampaignInviteForm
                :campaignId="campaign.id"
                @invites-updated="handleInvitesUpdated"
              /> -->

              <CampaignInviteList
                :invites="invites"
                :campaignId="campaign.id"
                :canManage="isCurrentUserGM"
                :loading="invitesLoading"
                :error="invitesError"
                @invites-updated="handleInvitesUpdated"
              />
            </template>
            <div v-else-if="membersLoading && !membersError">
                <!-- Zobrazit jen pokud se načítají členové a není chyba -->
                <!-- Může být nahrazeno lepším indikátorem -->
            </div>

        </div>

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
      </div>
    </div>
    <div v-else class="not-found">
      Campaign not found.
    </div>

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

    <!-- New Invite Modal -->
    <div v-if="showInviteModal" class="modal-backdrop">
      <div class="modal">
        <h2>Invite User to Campaign</h2>
        <CreateCampaignInviteForm
          v-if="campaign" 
          :campaignId="campaign.id"
          @invite-sent="handleInviteSent"
          @cancel="closeInviteModal"
        />
        <!-- Přidáme cancel tlačítko i sem pro konzistenci, pokud formulář nemá vlastní -->
        <div class="modal-actions" v-if="!campaign"> <!-- Jen pokud se kampaň nenačetla -->
           <button type="button" @click="closeInviteModal" class="btn btn-secondary">Cancel</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, reactive } from 'vue';
import * as campaignsApi from '@/services/api/campaigns';
import * as worldsApi from '@/services/api/worlds'; // Pro načtení jména světa
import * as campaignMembersApi from '@/services/api/campaignMembers';
import * as campaignInvitesApi from '@/services/api/campaignInvites';
import * as sessionsApi from '@/services/api/sessions'; // Import sessions API
import type { Campaign } from '@/types/campaign';
import type { World } from '@/types/world';
import { useAuthStore } from '@/store/auth.store'; // Správný název souboru
import CampaignMemberList from '@/components/campaign/CampaignMemberList.vue';
import CampaignInviteList from '@/components/campaign/CampaignInviteList.vue';
import CreateCampaignInviteForm from '@/components/campaign/CreateCampaignInviteForm.vue';
import type { UserCampaignRead } from '@/types/user_campaign';
import type { CampaignInvite } from '@/types/campaign_invite';
import { CampaignRoleEnum } from '@/types/campaign_role';
import type { Session, SessionCreate, SessionUpdate } from '@/types/session'; // Import session types

// Interface for Session form data
interface SessionFormData {
    title: string;
    description: string | null;
    summary: string | null;
    date_time: string | null; // Use string to bind with datetime-local input
}

export default defineComponent({
  name: 'CampaignDetailView',
  components: {
      CampaignMemberList,
      CampaignInviteList,
      CreateCampaignInviteForm,
  },
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

    const authStore = useAuthStore();
    const currentUserId = computed(() => authStore.user?.id);

    const members = ref<UserCampaignRead[]>([]);
    const membersLoading = ref(false);
    const membersError = ref<string | undefined>(undefined);

    const invites = ref<CampaignInvite[]>([]);
    const invitesLoading = ref(false);
    const invitesError = ref<string | undefined>(undefined);

    // --- New state for Sessions ---
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

    // Computed property for the current user's full membership object
    const currentUserMembership = computed(() => {
      if (!currentUserId.value || !members.value) return null;
      return members.value.find(m => m.user_id === currentUserId.value) || null;
    });

    // Use currentUserMembership in isCurrentUserGM
    const isCurrentUserGM = computed(() => {
      return currentUserMembership.value?.role === CampaignRoleEnum.GM;
    });

    const loadMembers = async (id: number) => {
      if (!id) return;
      membersLoading.value = true;
      membersError.value = undefined;
      members.value = [];
      try {
        members.value = await campaignMembersApi.getCampaignMembers(id);
      } catch (err: any) {
        membersError.value = `Failed to load members: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Load Members Error:", err);
      } finally {
        membersLoading.value = false;
      }
    };

    const loadInvites = async (id: number) => {
      if (!id) return;
      invitesLoading.value = true;
      invitesError.value = undefined;
      invites.value = [];
      try {
        invites.value = await campaignInvitesApi.getCampaignInvites(id);
      } catch (err: any) {
        // Nepovažujeme za chybu stránky, pokud se nepodaří načíst pozvánky (může být 403)
        invitesError.value = `Failed to load invites: ${err.response?.data?.detail || err.message || 'Forbidden?'}`;
        console.warn("Load Invites Error:", err);
      } finally {
        invitesLoading.value = false;
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

    // --- New Formatter for Date and Time ---
    const formatFullDateTime = (dateString: string | null | undefined) => {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleString(); // Adjust options as needed
        } catch (e) {
            console.error("Error formatting date:", e);
            return dateString; // Fallback
      }
    };

    const worldName = computed(() => {
        if (loadingWorld.value) return 'Loading world...';
        return world.value ? world.value.name : `ID: ${campaign.value?.world_id}`;
    });

    // --- New function to load sessions ---
    const loadSessions = async (id: number) => {
        if (!id) return;
        sessionsLoading.value = true;
        sessionsError.value = null;
        sessions.value = [];
        try {
            sessions.value = await sessionsApi.getSessionsByCampaign(id);
        } catch (err: any) {
            sessionsError.value = `Failed to load sessions: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
            console.error("Load Sessions Error:", err);
        } finally {
            sessionsLoading.value = false;
        }
    };
    
    // --- Modified loadCampaignDetail to also load sessions ---
    const loadCampaignDetail = async (id: number) => {
      loading.value = true;
      error.value = null;
      campaign.value = null;
      world.value = null;
      loadingWorld.value = false;
      members.value = []; 
      invites.value = []; 
      sessions.value = []; // Reset sessions
      membersLoading.value = false;
      membersError.value = undefined;
      invitesLoading.value = false;
      invitesError.value = undefined;
      sessionsLoading.value = false; // Ensure reset
      sessionsError.value = null;

      try {
        campaign.value = await campaignsApi.getCampaignById(id);
        if (campaign.value) {
          await loadWorldDetail(campaign.value.world_id);
          await loadMembers(campaign.value.id); // Load members first (for GM check)
          await loadSessions(campaign.value.id); // Then load sessions
        }
      } catch (err: any) {
        error.value = typeof err === 'string' ? err : (err?.message || 'Failed to load campaign details.');
        console.error("Load Campaign Detail Error:", err);
      } finally {
        loading.value = false;
      }
    };

    // --- Session Modal Logic ---
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
        sessionForm.date_time = session.date_time ? new Date(session.date_time).toISOString().slice(0, 16) : null;
        sessionFormError.value = null;
        showSessionModal.value = true;
    };

    const closeSessionModal = () => {
        showSessionModal.value = false;
        resetSessionForm();
    };

    const handleSaveSession = async () => {
        if (!campaign.value) return;
        sessionFormError.value = null;

        const dateTimeToSend = sessionForm.date_time === '' ? null : sessionForm.date_time;

        try {
            if (editingSession.value) {
                // Update
                const payload: SessionUpdate = {};
                if (sessionForm.title !== editingSession.value.title) {
                    payload.title = sessionForm.title;
                }
                // Ensure type compatibility for optional fields
                if (sessionForm.description !== editingSession.value.description) {
                    payload.description = sessionForm.description === undefined ? null : sessionForm.description;
                }
                if (sessionForm.summary !== editingSession.value.summary) {
                    payload.summary = sessionForm.summary === undefined ? null : sessionForm.summary;
                }
                if (dateTimeToSend !== editingSession.value.date_time) { 
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
                // Create logic remains the same
                if (!sessionForm.title.trim()) {
                    sessionFormError.value = "Session title cannot be empty.";
                    return;
                }
                 const sessionCreateData: SessionCreate = {
                    title: sessionForm.title,
                    description: sessionForm.description,
                    summary: sessionForm.summary,
                    date_time: dateTimeToSend,
                    campaign_id: campaign.value.id,
                };
                const newSession = await sessionsApi.createSession(sessionCreateData);
                sessions.value.unshift(newSession);
            }
            closeSessionModal();
        } catch (err: any) {
            console.error("Save Session Error:", err);
            sessionFormError.value = `Failed to save session: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        }
    };

    // --- Delete Session Logic ---
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

    // --- State for Invite Modal ---
    const showInviteModal = ref(false);

    // --- Invite Modal Logic ---
    const openInviteModal = () => {
      showInviteModal.value = true;
    };

    const closeInviteModal = () => {
      showInviteModal.value = false;
    };

    const handleInviteSent = () => {
      // Pozvánka byla odeslána (předpokládáme úspěch z komponenty)
      closeInviteModal();
      handleInvitesUpdated(); // Refresh seznamu pozvánek
    };

    // --- Existing watchers and event handlers ---
     watch(isCurrentUserGM, (isGM) => {
        // Load invites only if GM
        if(isGM && campaign.value && !invitesLoading.value) {
            loadInvites(campaign.value.id);
        }
    });

    watch(
        () => props.campaignId,
        (newId) => {
            if (newId) {
            loadCampaignDetail(Number(newId));
            }
        },
      { immediate: true }
    );

    const handleMembersUpdated = () => {
        if (campaign.value) loadMembers(campaign.value.id);
    };
    const handleInvitesUpdated = () => {
        if (campaign.value && isCurrentUserGM.value) loadInvites(campaign.value.id);
    };

    return {
      campaign,
      loading,
      error,
      worldName,
      formatDate,
      members,
      membersLoading,
      membersError,
      invites,
      invitesLoading,
      invitesError,
      isCurrentUserGM,
      currentUserId,
      currentUserMembership,
      handleMembersUpdated,
      handleInvitesUpdated,

      // --- New properties for Sessions ---
      sessions,
      sessionsLoading,
      sessionsError,
      showSessionModal,
      editingSession,
      sessionToDelete,
      sessionForm,
      sessionFormError,
      deleteSessionError,
      openAddSessionModal,
      openEditSessionModal,
      closeSessionModal,
      handleSaveSession,
      confirmDeleteSession,
      handleDeleteSession,

      // --- New formatters ---
      formatFullDateTime,

      // --- Invite Modal properties/methods ---
      showInviteModal,
      openInviteModal,
      closeInviteModal,
      handleInviteSent,
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
  margin-bottom: 2rem; /* Consistent spacing */
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

.management-section {
    border-bottom: 1px solid #eee;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  /* Removed border-bottom here, using border on detail-section */
}

.section-header h2 {
   margin: 0;
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
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}

.item-list-item:last-child {
  border-bottom: none;
}

.item-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.item-info p {
    margin: 0.3rem 0;
    color: #555;
    line-height: 1.5;
    font-size: 0.95rem;
}

.item-info .session-date {
    font-weight: 500;
    color: #333;
}

.item-info .session-description {
    color: #444;
}

.item-info .session-summary {
    font-style: italic;
    color: #666;
    margin-top: 0.5rem;
    font-size: 0.9rem;
}

.item-info .item-meta {
    font-size: 0.8rem;
    color: #777;
    margin-top: 0.5rem;
}

.item-actions {
    margin-left: 1rem; 
    white-space: nowrap; 
    display: flex;
    flex-direction: column; 
    gap: 0.5rem; 
}

/* Modal Styles */
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
  z-index: 1000;
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
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="datetime-local"],
.form-group textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  box-sizing: border-box;
  font-size: 1rem;
}

.form-group textarea {
    min-height: 100px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.confirmation-modal p {
    margin-bottom: 1rem;
}
.confirmation-modal p strong {
    margin-right: 0.5em;
}

.loading-state,
.loading-state.small,
.error-message.small {
    padding: 0.5rem;
    font-size: 0.9rem;
    text-align: left;
    margin-top: 0.5rem;
}


/* Button styles */
.btn { padding: 0.6rem 1.2rem; border-radius: 0.3rem; cursor: pointer; border: none; font-weight: 500; text-decoration: none; transition: background-color 0.2s ease; }
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }
.btn-danger { background-color: #dc3545; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }

</style> 