<template>
  <div v-if="show" class="modal-backdrop" @click.self="$emit('cancel')">
    <div class="modal confirmation-modal">
      <h2>Confirm Deletion</h2>
      <p>
        Are you sure you want to delete the {{ itemType }} 
        <strong v-if="itemName">"{{ itemName }}"</strong>?
        This action cannot be undone.
      </p>
      <slot name="additional-warning"></slot> <!-- Slot for extra warnings -->
      <div class="modal-actions">
        <button type="button" @click="$emit('cancel')" class="btn btn-secondary" :disabled="isDeleting">Cancel</button>
        <button type="button" @click="$emit('confirm')" class="btn btn-danger" :disabled="isDeleting">
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </button>
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

defineProps<{
  show: boolean;
  itemType: string; // e.g., 'world', 'campaign', 'character'
  itemName?: string; // Optional name of the item being deleted
  isDeleting: boolean;
  error: string | null;
}>();

defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

</script>

<style scoped>
/* Generic Modal Styles (can be shared or customized) */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); /* Darker backdrop */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050; /* Ensure it's above other modals if necessary */
}

.modal {
  background-color: white;
  padding: 2rem 2.5rem;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 450px; /* Slightly smaller max-width */
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.25);
}

.modal h2 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #343a40;
  font-size: 1.3rem;
  text-align: center;
}

.confirmation-modal p {
  margin-bottom: 1.5rem;
  color: #495057;
  line-height: 1.6;
  text-align: center;
  font-size: 1rem;
}

.confirmation-modal p strong {
  font-weight: 600; /* Make the name stand out */
  color: #dc3545; /* Danger color for emphasis */
}

.modal-actions {
  display: flex;
  justify-content: center; /* Center buttons */
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.error-message {
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 1rem;
  text-align: center;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

/* Button styles */
.btn {
  padding: 0.6rem 1.5rem; /* More padding */
  border: none;
  border-radius: 0.3rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}
.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:not(:disabled):hover {
  background-color: #5a6268;
}
.btn-danger {
  background-color: #dc3545;
  color: white;
}
.btn-danger:not(:disabled):hover {
  background-color: #c82333;
}
</style> 