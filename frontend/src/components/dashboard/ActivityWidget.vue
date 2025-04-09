<template>
  <div class="widget">
    <div class="widget-header">
      <h3>Recent Activities</h3>
      <button class="widget-action">View All</button>
    </div>
    <div class="activity-list">
      <div class="activity-item">
        <div class="activity-icon">📝</div>
        <div class="activity-content">
          <p class="activity-text">New task created: Complete dashboard design</p>
          <p class="activity-time">1 hour ago</p>
        </div>
      </div>
      <div class="activity-item">
        <div class="activity-icon">✅</div>
        <div class="activity-content">
          <p class="activity-text">Task completed: Authentication implementation</p>
          <p class="activity-time">3 hours ago</p>
        </div>
      </div>
      <div class="activity-item">
        <div class="activity-icon">👤</div>
        <div class="activity-content">
          <p class="activity-text">New team member: Jane Smith</p>
          <p class="activity-time">Yesterday</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ActivityWidget'
});
</script>

<style scoped>
.widget {
  background-color: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.widget:hover {
  box-shadow: 0 5px 12px rgba(0, 0, 0, 0.08);
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.widget-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.widget-action {
  background: none;
  border: none;
  color: #7851a9;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.widget-action:hover {
  color: #634288;
  text-decoration: underline;
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-icon {
  margin-right: 12px;
  font-size: 1.2rem;
  color: #7851a9;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 5px 0;
  font-size: 0.95rem;
  color: #2c3e50;
}

.activity-time {
  margin: 0;
  font-size: 0.8rem;
  color: #94a3b8;
}
</style> 