<template>
  <div class="widget">
    <div class="widget-header">
      <h3>Upcoming Deadlines</h3>
      <button class="widget-action">View Calendar</button>
    </div>
    <div class="deadlines-list">
      <div class="deadline-item">
        <div class="deadline-date">
          <p class="date-day">15</p>
          <p class="date-month">APR</p>
        </div>
        <div class="deadline-content">
          <p class="deadline-title">Project Submission</p>
          <p class="deadline-project">Sesplan MVP</p>
        </div>
      </div>
      <div class="deadline-item">
        <div class="deadline-date">
          <p class="date-day">22</p>
          <p class="date-month">APR</p>
        </div>
        <div class="deadline-content">
          <p class="deadline-title">Code Review</p>
          <p class="deadline-project">Backend API</p>
        </div>
      </div>
      <div class="deadline-item">
        <div class="deadline-date">
          <p class="date-day">30</p>
          <p class="date-month">APR</p>
        </div>
        <div class="deadline-content">
          <p class="deadline-title">Client Presentation</p>
          <p class="deadline-project">Sesplan Beta</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'DeadlineWidget'
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

/* Deadlines List */
.deadlines-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.deadline-item {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.deadline-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #8e59d7, #634288);
  border-radius: 8px;
  margin-right: 15px;
  color: white;
}

.date-day {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.date-month {
  margin: 0;
  font-size: 0.7rem;
  font-weight: 500;
}

.deadline-content {
  flex: 1;
}

.deadline-title {
  margin: 0 0 5px 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: #2c3e50;
}

.deadline-project {
  margin: 0;
  font-size: 0.85rem;
  color: #7851a9;
}
</style> 