<template>
  <!-- Adaptér využívající refaktorovanou komponentu -->
  <AvailabilityGrid
    :session-id="sessionId"
    :current-user-id="currentUserId"
    :is-gm="isGm"
    :slots="slots"
    :user-availabilities="userAvailabilities"
    @availability-changed="onAvailabilityChanged"
  />
</template>

<script setup lang="ts">
import AvailabilityGrid from '../availability/grid/AvailabilityGrid.vue';
import type { SessionSlot } from '@/types/session_slot';
import type { UserAvailability } from '@/types/user_availability';

/**
 * Tento soubor je adaptér, který poskytuje kompatibilitu se starší verzí komponenty.
 * Nová implementace se nachází v /components/availability/grid/AvailabilityGrid.vue
 * 
 * @deprecated - Použijte místo toho AvailabilityGrid
 */

const props = defineProps<{
  sessionId: number;
  currentUserId: number;
  isGm: boolean;
  slots: SessionSlot[];
  userAvailabilities: UserAvailability[];
}>();

// Použití props pro odstranění TS6133 varování
const { sessionId, currentUserId, isGm, slots, userAvailabilities } = props;

const emit = defineEmits<{
  (e: 'availability-changed'): void;
}>();

function onAvailabilityChanged() {
  emit('availability-changed');
}
</script>
  