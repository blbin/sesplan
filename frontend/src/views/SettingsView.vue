<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="mb-6">
          <v-card-title>Profile Information</v-card-title>
          <v-card-text>
            <v-form ref="profileForm" @submit.prevent="handleUpdateProfile">
              <v-text-field
                v-model="profileData.firstName"
                label="First Name"
                :rules="[rules.required]"
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-text-field
                v-model="profileData.lastName"
                label="Last Name"
                :rules="[rules.required]"
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-text-field
                :model-value="authStore.currentUser?.email ?? ''"
                label="Email"
                readonly
                disabled
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-text-field
                :model-value="authStore.currentUser?.username ?? ''"
                label="Username"
                readonly
                disabled
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-btn type="submit" color="primary" :loading="loadingProfile" :disabled="!isProfileChanged">
                Update Profile
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title>Change Password</v-card-title>
          <v-card-text>
            <v-form ref="passwordForm" @submit.prevent="handleChangePassword">
              <v-text-field
                v-model="passwordData.currentPassword"
                label="Current Password"
                type="password"
                :rules="[rules.required]"
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-text-field
                v-model="passwordData.newPassword"
                label="New Password"
                type="password"
                :rules="[rules.required, rules.minLength(8)]"
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-text-field
                v-model="passwordData.confirmPassword"
                label="Confirm New Password"
                type="password"
                :rules="[rules.required, rules.passwordMatch(passwordData.newPassword)]"
                variant="outlined"
                class="mb-3"
              ></v-text-field>
              <v-btn type="submit" color="primary" :loading="loadingPassword">
                Change Password
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useAuthStore } from '@/store/auth.store';
import { updateUserMe, changePassword } from '@/services/api/users.ts';
import type { ChangePasswordPayload, UserUpdate, User } from '@/types/user';
import type { VForm } from 'vuetify/components'; // Import VForm type

const authStore = useAuthStore();
const profileForm = ref<InstanceType<typeof VForm> | null>(null);
const passwordForm = ref<InstanceType<typeof VForm> | null>(null);

const profileData = reactive({
  firstName: '',
  lastName: '',
});

const passwordData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
});

const loadingProfile = ref(false);
const loadingPassword = ref(false);
const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
});

// Pravidla validace
const rules = {
  required: (value: string) => !!value || 'Field is required.',
  minLength: (length: number) => (value: string) => (value && value.length >= length) || `Minimum ${length} characters required.`,
  passwordMatch: (newPassword: string) => (value: string) => value === newPassword || 'Passwords do not match.',
};

// Sledování změn v profilu
const isProfileChanged = computed(() => {
  return (
    profileData.firstName !== (authStore.currentUser?.first_name ?? '') ||
    profileData.lastName !== (authStore.currentUser?.last_name ?? '')
  );
});

// Funkce pro zobrazení snackbaru
const showSnackbar = (text: string, color: 'success' | 'error' = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
};

// Aktualizace profilu
const handleUpdateProfile = async () => {
  if (!profileForm.value) return;
  const { valid } = await profileForm.value.validate();

  if (valid) {
    loadingProfile.value = true;
    try {
      const updatePayload: UserUpdate = {
        first_name: profileData.firstName || null,
        last_name: profileData.lastName || null,
      };
      const updatedUser = await updateUserMe(updatePayload);
      // Aktualizace store - Přímá mutace s explicitním typem
      const finalUser: User = { ...authStore.user, ...updatedUser } as User;
      authStore.user = finalUser;
      showSnackbar('Profile updated successfully!');
    } catch (error) {
      console.error('Profile update failed:', error);
      showSnackbar('Failed to update profile.', 'error');
    } finally {
      loadingProfile.value = false;
    }
  }
};

// Změna hesla
const handleChangePassword = async () => {
  if (!passwordForm.value) return;
  const { valid } = await passwordForm.value.validate();

  if (valid) {
    loadingPassword.value = true;
    try {
      const payload: ChangePasswordPayload = {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      };
      await changePassword(payload);
      showSnackbar('Password changed successfully!');
      passwordForm.value.reset(); // Vyčistit formulář po úspěchu
    } catch (error: any) {
      console.error('Password change failed:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to change password.';
      showSnackbar(errorMessage, 'error');
    } finally {
      loadingPassword.value = false;
    }
  }
};

// Načtení počátečních dat při připojení komponenty
onMounted(() => {
  if (authStore.currentUser) {
    profileData.firstName = authStore.currentUser.first_name ?? '';
    profileData.lastName = authStore.currentUser.last_name ?? '';
  }
});

// Watcher pro případ, že se user načte později (např. po refresh)
watch(() => authStore.currentUser, (newUser) => {
  if (newUser) {
    profileData.firstName = newUser.first_name ?? '';
    profileData.lastName = newUser.last_name ?? '';
  }
}, { immediate: true });

</script>

<style scoped>
/* Můžeme přidat mezery mezi kartami */
.mb-6 {
  margin-bottom: 24px;
}
.mb-3 {
  margin-bottom: 12px !important; /* Vyšší specificita pro přepsání Vuetify */
}
</style> 