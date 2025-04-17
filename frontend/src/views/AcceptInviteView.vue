<template>
  <div class="accept-invite-view">
    <div v-if="loading" class="status-message">Processing invite...</div>
    <div v-else-if="error" class="error-message">
      <h2>Error Accepting Invite</h2>
      <p>{{ error }}</p>
      <router-link to="/dashboard" class="btn btn-primary">Go to Dashboard</router-link>
    </div>
    <div v-else-if="successMessage" class="success-message">
      <h2>Invite Accepted!</h2>
      <p>{{ successMessage }}</p>
      <p>Redirecting you to the campaign...</p>
      <!-- Optional: Button to redirect manually if needed -->
      <!-- <router-link :to="`/dashboard/campaigns/${campaignId}`" class="btn btn-primary">Go to Campaign</router-link> -->
    </div>
    <div v-else class="status-message">Initializing...</div> <!-- Initial state -->
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import * as campaignInvitesApi from '@/services/api/campaignInvites';
import { useAuthStore } from '@/store/auth.store';

export default defineComponent({
  name: 'AcceptInviteView',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();

    const loading = ref(false);
    const error = ref<string | null>(null);
    const successMessage = ref<string | null>(null);
    const campaignId = ref<number | null>(null);

    const processInvite = async () => {
      const token = route.params.token as string;

      if (!token) {
        error.value = 'Invite token is missing.';
        return;
      }

      // Ensure user is logged in - router guard should handle redirect if not
      if (!authStore.isLoggedIn) {
         // Router guard should have redirected to login. If we get here, something is wrong
         // or the guard logic needs adjustment for this specific case.
         error.value = "You must be logged in to accept an invite. Redirecting to login...";
         // Optional: force redirect if guard didn't catch it
         // router.push({ name: 'login', query: { redirect: route.fullPath } });
         // Or simply display the message, assuming guard handles it.
         return;
      }

      loading.value = true;
      error.value = null;
      successMessage.value = null;
      campaignId.value = null;

      try {
        const response = await campaignInvitesApi.acceptCampaignInvite(token);
        successMessage.value = response.message;
        campaignId.value = response.campaign_id;

        // Redirect after a short delay
        setTimeout(() => {
          if (campaignId.value) {
            router.push({ name: 'dashboard-campaign-detail', params: { campaignId: campaignId.value } });
          }
        }, 2000); // 2 seconds delay

      } catch (err: any) {
        error.value = `Failed to accept invite: ${err.response?.data?.detail || err.message || 'Unknown error'}`;
        console.error("Accept Invite Error:", err);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      // Process invite as soon as the component mounts
      processInvite();
    });

    return {
      loading,
      error,
      successMessage,
      campaignId,
    };
  },
});
</script>

<style scoped>
.accept-invite-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh; /* Take up most of the viewport height */
  padding: 2rem;
  text-align: center;
}

.status-message,
.error-message,
.success-message {
  padding: 2rem;
  border-radius: 0.5rem;
  max-width: 500px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.status-message {
    color: #6c757d;
}

.error-message {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.success-message {
  color: #155724;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
}

h2 {
  margin-top: 0;
  margin-bottom: 1rem;
}

p {
  margin-bottom: 1.5rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  text-decoration: none;
  display: inline-block;
  margin-top: 1rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
}
</style> 