<template>
  <div class="time-col">
    <div v-for="timeSlot in timeSlots" :key="timeSlot" class="time-slot-label">
      {{ formatTimeLabel(timeSlot) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { format, startOfDay, addMinutes } from 'date-fns';

interface Props {
  timeSlots: number[]; // Array of minutes from midnight
}

defineProps<Props>();

function formatTimeLabel(minutes: number): string {
  const date = startOfDay(new Date());
  const timeDate = addMinutes(date, minutes);
  return format(timeDate, 'HH:mm');
}
</script>

<style scoped>
.time-col {
  /* Styles for the time column container itself */
}

.time-slot-label {
  height: 25px; /* Should match time-slot height */
  line-height: 25px; /* Vertically center */
  text-align: center;
  font-size: 0.8em;
  color: #555;
  border-bottom: 1px solid #eee;
  box-sizing: border-box; /* Ensure border is included in height */
}

/* Remove bottom border for the last label to align with grid */
.time-slot-label:last-child {
    border-bottom: none;
}

</style> 