<template>
  <v-container class="fill-height d-flex align-center justify-center">
    <v-card v-if="loading || message || error" class="pa-5 text-center" width="400">
      <v-progress-circular
        v-if="loading"
        indeterminate
        color="primary"
        size="64"
      ></v-progress-circular>
      <div v-if="message" class="mt-4 text-h6 text-success">{{ message }}</div>
      <div v-if="error" class="mt-4 text-h6 text-error">{{ error }}</div>
      <v-card-text v-if="loading" class="mt-2">
        Accepting invitation...
      </v-card-text>
      <v-card-actions v-if="error" class="justify-center mt-4">
        <v-btn color="primary" @click="goToDashboard">Go to Dashboard</v-btn>
      </v-card-actions>
    </v-card>
    <!-- Optionally, show something if neither loading, message nor error -->
    <div v-else>
      Preparing to accept invite...
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { acceptCampaignInvite } from '@/services/api/campaignInvites';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const message = ref<string | null>(null);
const error = ref<string | null>(null);
const token = ref<string | null>(null);

onMounted(async () => {
  const routeToken = route.params.token;
  if (typeof routeToken === 'string') {
    token.value = routeToken;
    await handleAcceptInvite();
  } else {
    error.value = 'Invalid invitation token.';
    loading.value = false;
  }
});

async function handleAcceptInvite() {
  if (!token.value) {
    error.value = 'Invitation token is missing.';
    loading.value = false;
    return;
  }

  loading.value = true;
  message.value = null;
  error.value = null;

  try {
    const response = await acceptCampaignInvite(token.value);
    message.value = response.message; // Show success message briefly

    // Wait a bit for user to see message, then redirect
    setTimeout(() => {
      if (response.character_id) {
        // Redirect to the character detail page
        router.push({ 
          name: 'CharacterDetail', 
          params: { characterId: response.character_id }
        });
      } else {
        // If character_id is missing (shouldn't happen on success, but fallback)
        // Redirect to the campaign page or dashboard
        console.warn('Character ID missing after invite acceptance, redirecting to campaign.');
        if (response.campaign_id) {
          router.push({ name: 'CampaignDetail', params: { campaignId: response.campaign_id } });
        } else {
          router.push({ name: 'dashboard' }); // Fallback to dashboard
        }
      }
    }, 1500); // Delay for 1.5 seconds

  } catch (err: any) {
    console.error("Error accepting invite:", err);
    const errorMessage = err.response?.data?.detail || 'Failed to accept invitation. Please try again later.';
    error.value = errorMessage;
  } finally {
    // Keep loading true until redirect happens or only set to false on error?
    // Let's set loading false only on error, otherwise user sees success msg until redirect.
    if (error.value) {
      loading.value = false; 
    }
    // If success, loading spinner is replaced by success message until redirect happens.
  }
}

function goToDashboard() {
  router.push({ name: 'dashboard' });
}

</script>

<style scoped>
/* Add any specific styles if needed */
</style> 