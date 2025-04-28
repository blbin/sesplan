<template>
  <div v-if="isDragging && selectionActive" class="selection-info">
    <v-chip :color="isAdding ? 'success' : 'error'" variant="tonal" size="small">
      <v-icon start size="small" :icon="isAdding ? 'mdi-plus' : 'mdi-minus'"></v-icon>
      {{ formattedRange }}
    </v-chip>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  isDragging: boolean;
  selectionActive: boolean;
  isAdding: boolean;
  formattedRange: string;
}>();
</script>

<style scoped>
@import '../styles/availability-grid.css';
</style> 