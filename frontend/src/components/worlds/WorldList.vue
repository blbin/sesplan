<template>
  <ul class="world-list">
    <li v-for="world in worlds" :key="world.id" class="world-list-item">
      <div class="world-info">
        <!-- Remove test span -->
        <!-- <span>DEBUG NAME: {{ world.name }}</span> --> 
        <router-link :to="{ name: 'dashboard-world-detail', params: { worldId: world.id } }" class="world-name-link">
           <h2>{{ world.name }}</h2>
        </router-link>
        <p class="world-description">{{ world.description || 'No description' }}</p>
        <!-- Zobrazení kampaní -->
        <div v-if="world.campaigns && world.campaigns.length > 0" class="world-campaigns">
          <strong>Campaigns:</strong>
          <ul>
            <li v-for="campaign in world.campaigns" :key="campaign.id">
               <!-- Ensure campaign object has id and name -->
              <router-link 
                  v-if="campaign.id && campaign.name" 
                  :to="{ name: 'CampaignDetail', params: { campaignId: campaign.id } }" 
                  class="campaign-link"
              >
                {{ campaign.name }}
              </router-link>
              <span v-else>Invalid campaign data</span>
            </li>
          </ul>
        </div>
        <div v-else class="world-campaigns-empty">
          No campaigns in this world yet.
        </div>
        <!-- Add other relevant info like owner, creation date etc. if needed -->
        <small class="world-meta">Created: {{ formatDate(world.created_at) }}</small>
      </div>
      <div class="world-actions">
        <button @click="$emit('edit-world', world)" class="btn btn-secondary btn-sm">Edit</button>
        <button @click="$emit('delete-world', world)" class="btn btn-danger btn-sm">Delete</button>
      </div>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { World } from '@/types/world';

// Define Props
defineProps<{
  worlds: World[];
}>();

// Define Emits
defineEmits<{
  (e: 'edit-world', world: World): void;
  (e: 'delete-world', world: World): void;
}>();

// Helper function for formatting date (can be moved to utils later)
const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return String(dateString); // Fallback
  }
};

</script>

<style scoped>
/* Styles specific to the World List */
.world-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.world-list-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* Align items to the top */
  padding: 1.5rem 0; /* Increased padding for more space */
  border-bottom: 1px solid #e9ecef;
}
.world-list-item:last-child {
  border-bottom: none;
}

.world-info {
    flex-grow: 1; /* Take available space */
    margin-right: 1rem; /* Space between info and actions */
}

.world-name-link {
    text-decoration: none;
    color: inherit; /* Link itself inherits color */
    display: block; /* Keep it block */
    margin-bottom: 0.25rem;
}
.world-name-link:hover {
   text-decoration: none; 
}

/* Apply styling to h2 inside the link */
.world-name-link h2 {
    margin: 0; /* Reset h2 margin */
    font-size: 1.2rem;
    font-weight: 600;
    color: #343a40; /* Set visible color here */
    transition: color 0.2s ease;
    display: inline-block; /* Allow hover effect */
}
.world-name-link:hover h2 {
    color: #7851a9; /* Highlight h2 on hover */
}

.world-description { /* Add a class for description paragraph */
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  color: #6c757d;
  line-height: 1.5;
}

.world-actions {
  display: flex;
  flex-direction: column; /* Stack buttons vertically */
  gap: 0.5rem;
  flex-shrink: 0; /* Prevent actions from shrinking */
}

.world-campaigns {
  margin-top: 0.75rem;
  font-size: 0.9rem;
}

.world-campaigns strong {
  color: #495057;
  font-weight: 500;
}

.world-campaigns ul {
  list-style: none; /* Changed from disc */
  margin: 0.25rem 0 0 0; /* Removed left margin */
  padding: 0;
}

.world-campaigns li {
   color: #6c757d;
   margin-top: 0.2rem;
}

.world-campaigns-empty {
    margin-top: 0.75rem;
    font-size: 0.9rem;
    color: #adb5bd; /* Lighter color */
    font-style: italic;
}

.campaign-link {
  color: #7851a9; /* Use app's primary color */
  text-decoration: none;
  font-weight: 500;
  font-size: 0.85rem;
}
.campaign-link:hover {
  text-decoration: underline;
  color: #5f3f87;
}

.world-meta {
    display: block; /* Ensure it takes its own line */
    margin-top: 0.75rem;
    font-size: 0.8rem;
    color: #adb5bd;
}


/* Button styles (assuming these might not be global) */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.2s ease;
  text-decoration: none;
}
.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn-danger {
  background-color: #dc3545;
  color: white;
}
.btn-danger:hover {
  background-color: #c82333;
}
</style> 