<template>
  <div class="text-center mt-4">
    <div class="d-flex justify-center flex-wrap gap-2">
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(0,0,0,0.05)"></span>
        <span class="legend-text">Neaktivní</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: white; border: 1px solid #ddd"></span>
        <span class="legend-text">Aktivní slot</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(76,175,80,0.3)"></span>
        <span class="legend-text">Jste dostupní</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(76,175,80,0.5)"></span>
        <span class="legend-text">Vybíráte dostupnost</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(244,67,54,0.2)"></span>
        <span class="legend-text">Odebíráte dostupnost</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(33, 150, 243, 0.3); border: 2px solid rgba(33, 150, 243, 0.8)"></span>
        <span class="legend-text">Začátek výběru</span>
      </div>
      <div class="legend-item">
        <span class="legend-color" style="background-color: rgba(156, 39, 176, 0.3); border: 2px solid rgba(156, 39, 176, 0.8)"></span>
        <span class="legend-text">Konec výběru</span>
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