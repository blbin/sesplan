<template>
  <v-card :loading="loading">
    <v-card-title>Edit Your Profile</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="updateProfile">
        <v-text-field
          label="Username"
          v-model="username"
          readonly
          disabled
          class="mb-3"
          variant="outlined"
        ></v-text-field>

        <v-text-field
          label="Email"
          v-model="email"
          readonly
          disabled
          class="mb-3"
          variant="outlined"
        ></v-text-field>

        <v-text-field
          label="First Name"
          v-model="firstName"
          :error-messages="errors.first_name"
          variant="outlined"
          class="mb-3"
        ></v-text-field>

        <v-text-field
          label="Last Name"
          v-model="lastName"
          :error-messages="errors.last_name"
          variant="outlined"
          class="mb-3"
        ></v-text-field>

        <v-alert v-if="successMessage" type="success" class="mb-4">
          {{ successMessage }}
        </v-alert>
        <v-alert v-if="errorMessage" type="error" class="mb-4">
          {{ errorMessage }}
        </v-alert>

        <v-btn type="submit" color="primary" :loading="loading" :disabled="loading">
          Save Changes
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getUserMe, updateUserMe } from '@/services/api/users'; // Použití specifických funkcí
// import type { User } from '@/types/user'; // Odstraněn nepoužívaný import
import type { UserUpdate } from '@/types/user';

const loading = ref(false);
const username = ref('');
const email = ref('');
// const fullName = ref<string | null>(null); // Nahrazeno
const firstName = ref<string | null>(null);
const lastName = ref<string | null>(null);
const errors = ref<Record<string, any>>({}); // Upraveno pro potenciální vnořené chyby
const successMessage = ref<string | null>(null);
const errorMessage = ref<string | null>(null);

async function fetchUserData() {
  loading.value = true;
  errorMessage.value = null;
  successMessage.value = null;
  try {
    const user = await getUserMe(); // Nové volání pomocí service funkce
    username.value = user.username;
    email.value = user.email;
    // fullName.value = user.full_name ?? ''; // Nahrazeno
    firstName.value = user.first_name ?? '';
    lastName.value = user.last_name ?? '';

  } catch (error) {
    console.error('Failed to fetch user data:', error);
    errorMessage.value = 'Failed to load user data. Please try again later.';
  } finally {
    loading.value = false;
  }
}

async function updateProfile() {
  loading.value = true;
  errors.value = {};
  successMessage.value = null;
  errorMessage.value = null;

  const payload: UserUpdate = {
    // full_name: fullName.value || null, // Nahrazeno
    first_name: firstName.value || null,
    last_name: lastName.value || null,
  };

  try {
    await updateUserMe(payload); // Nové volání pomocí service funkce
    successMessage.value = 'Profile updated successfully!';
    // Optional: refetch data to confirm update
    // await fetchUserData();
  } catch (error: any) { // Použijeme 'any' pro zachycení AxiosError
    console.error('Failed to update profile:', error);
    if (error.response && error.response.data && error.response.data.detail) {
      // Handle FastAPI validation errors or specific detail messages
      if (typeof error.response.data.detail === 'string') {
          errorMessage.value = error.response.data.detail;
      } else if (Array.isArray(error.response.data.detail)) {
           // Assuming FastAPI validation errors format
           // Reset errors before populating
           errors.value = {}; 
           let generalError = false;
           error.response.data.detail.forEach((err: any) => {
               // Loc might be like ["body", "first_name"]
               const field = err.loc && err.loc.length > 1 ? err.loc[1] : 'general';
               if (!errors.value[field]) errors.value[field] = [];
               errors.value[field].push(err.msg);
               if(field === 'general') generalError = true;
           });
          errorMessage.value = generalError 
             ? 'An unexpected error occurred during validation.' 
             : 'Please correct the errors below.';

      } else {
          errorMessage.value = 'An unexpected error occurred.';
      }
    } else {
        errorMessage.value = 'Failed to update profile. Please try again later.';
    }
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchUserData();
});
</script>

<style scoped>
/* Add any specific styles if needed */
</style> 