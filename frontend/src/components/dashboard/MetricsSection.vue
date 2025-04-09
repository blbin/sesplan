<template>
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="metric-icon">📈</div>
      <div class="metric-content">
        <h3>Active Projects</h3>
        <p class="metric-value">8</p>
      </div>
    </div>
    <div class="metric-card">
      <div class="metric-icon">⏱️</div>
      <div class="metric-content">
        <h3>Time on Tasks</h3>
        <p class="metric-value">32h</p>
      </div>
    </div>
    <div class="metric-card">
      <div class="metric-icon">✅</div>
      <div class="metric-content">
        <h3>Completed Tasks</h3>
        <p class="metric-value">12</p>
      </div>
    </div>
    <div class="metric-card">
      <div class="metric-icon">🔄</div>
      <div class="metric-content">
        <h3>Pending Tasks</h3>
        <p class="metric-value">5</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'MetricsSection'
});
</script>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background-color: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  font-size: 2rem;
  margin-right: 15px;
  color: #7851a9;
}

.metric-content h3 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  font-weight: 500;
  color: #4a5568;
}

.metric-value {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #2c3e50;
}

/* Responsive Design */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
}

@media (max-width: 576px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style> 