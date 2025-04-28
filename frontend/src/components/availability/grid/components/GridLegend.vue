<template>
  <div class="text-center mt-4">
    <div class="d-flex justify-center flex-wrap gap-2">
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(0,0,0,0.05)"></span>
        <span class="legend-text">Inactive</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: white; border: 1px solid #ddd"></span>
        <span class="legend-text">Active slot</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(76,175,80,0.3)"></span>
        <span class="legend-text">You are available</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(76,175,80,0.5)"></span>
        <span class="legend-text">Selecting availability</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(244,67,54,0.2)"></span>
        <span class="legend-text">Removing availability</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(33, 150, 243, 0.3); border: 2px solid rgba(33, 150, 243, 0.8)"></span>
        <span class="legend-text">Selection start</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(156, 39, 176, 0.3); border: 2px solid rgba(156, 39, 176, 0.8)"></span>
        <span class="legend-text">Selection end</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Komponenta legendy - bez dodatečné logiky
</script>

<style scoped>
@import '../styles/availability-grid.css';
</style> 