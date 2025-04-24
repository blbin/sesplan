<template>
  <div class="grid-header">
    <div class="time-col-header">Čas</div>
    <div v-for="day in days" :key="day.toISOString()" class="day-col-header">
      {{ formatDayHeader(day) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { format } from 'date-fns';

interface Props {
  days: Date[];
}

defineProps<Props>();

function formatDayHeader(date: Date): string {
  return format(date, 'EEE dd/MM');
}
</script>

<style scoped>
.grid-header {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr); /* Adjust time col width as needed */
  font-weight: bold;
  text-align: center;
  position: sticky;
  top: 0; /* Stick to top when scrolling */
  background-color: white;
  z-index: 10; /* Keep header above content */
  border-bottom: 2px solid #ccc;
}

.time-col-header,
.day-col-header {
  padding: 8px 4px;
  border-left: 1px solid #eee;
}

.time-col-header {
  border-left: none;
}
</style> 