<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <h1 class="text-h4 mb-4">User Settings</h1>
        <UserSettingsForm />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import UserSettingsForm from '@/components/settings/UserSettingsForm.vue';
</script> 