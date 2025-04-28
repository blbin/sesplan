<template>
  <thead>
    <tr>
      <th class="time-header">Time</th>
      <th v-for="day in days" :key="day.date" class="day-header">
        {{ day.label }}
      </th>
    </tr>
  </thead>
</template>

<script setup lang="ts">
// Typy dat a parametry
interface DayInfo {
  date: string;
  label: string;
}

defineProps<{
  days: DayInfo[];
}>();
</script>

<style scoped>
@import '../styles/availability-grid.css';
</style> 