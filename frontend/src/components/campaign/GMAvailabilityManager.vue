<template>
  <v-card variant="outlined">
    <v-card-title>Slot Management</v-card-title>
    <v-card-text>
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        Here you can add, edit, and delete time slots for availability submissions.
      </v-alert>

      <v-btn color="primary" @click="openAddDialog" class="mb-4">Add slot</v-btn>

      <v-list v-if="existingSlots.length > 0" density="compact" bg-color="grey-lighten-4" rounded>
        <v-list-subheader>Existing slots</v-list-subheader>
        <v-list-item 
          v-for="slot in existingSlots" 
          :key="slot.id"
          :title="`${formatDateTime(slot.slot_from)} - ${formatDateTime(slot.slot_to)}`"
          :subtitle="slot.note || ''"
        >
          <template v-slot:append>
            <v-btn icon="mdi-pencil" variant="text" size="small" @click="openEditDialog(slot)" class="mr-1"></v-btn>
            <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="confirmDelete(slot)"></v-btn>
          </template>
        </v-list-item>
      </v-list>
      <v-alert v-else type="info" variant="tonal" class="mt-3">
        No slots have been created yet. Create your first slot using the button above.
      </v-alert>

      <v-alert v-if="operationError" type="error" density="compact" class="mt-4">
        {{ operationError }}
      </v-alert>
      <v-alert v-if="operationSuccess" type="success" density="compact" class="mt-4">
        {{ operationSuccess }}
      </v-alert>
    </v-card-text>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="dialogOpen" max-width="600px">
      <v-card :loading="saving" :disabled="saving">
        <v-card-title>{{ editingSlot ? 'Edit' : 'Add' }} slot</v-card-title>
        <v-card-text>
          <v-form ref="slotForm" @submit.prevent="saveSlot">
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  label="Slot start (From)"
                  v-model="formData.slot_from"
                  type="datetime-local"
                  :rules="[rules.required, rules.dateTimeOrder]"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  label="Slot end (To)"
                  v-model="formData.slot_to"
                  type="datetime-local"
                  :rules="[rules.required, rules.dateTimeOrder]"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-textarea 
              label="Note (optional)" 
              v-model="formData.note"
              rows="2"
            ></v-textarea>
          </v-form>
          <v-alert v-if="formError" type="error" density="compact" class="mt-3">{{ formError }}</v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" @click="saveSlot" :loading="saving">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="confirmDeleteDialogOpen" max-width="400px">
      <v-card>
        <v-card-title>Delete slot?</v-card-title>
        <v-card-text>Are you sure you want to delete this time slot? This action is irreversible and will remove all user availability submissions.</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="confirmDeleteDialogOpen = false">Cancel</v-btn>
          <v-btn color="error" @click="executeDelete" :loading="deleting">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import type { SessionSlot, SessionSlotCreate, SessionSlotUpdate } from '@/types/session_slot';
import * as availabilityApi from '@/services/api/sessionAvailability';
import { format, parseISO, isValid } from 'date-fns';

const props = defineProps<{ 
  sessionId: number;
  existingSlots: SessionSlot[];
}>();

const emit = defineEmits<{ (e: 'slots-updated'): void }>();

const dialogOpen = ref(false);
const confirmDeleteDialogOpen = ref(false);
const editingSlot = ref<SessionSlot | null>(null);
const slotToDelete = ref<SessionSlot | null>(null);
const saving = ref(false);
const deleting = ref(false);
const formError = ref<string | null>(null);
const operationError = ref<string | null>(null);
const operationSuccess = ref<string | null>(null);
const slotForm = ref<HTMLFormElement | null>(null); // Ref for v-form validation

// datetime-local input provides value in "YYYY-MM-DDTHH:mm" format
const formData = reactive({
  slot_from: '', // Initialize as empty strings
  slot_to: '',
  note: ''
});

const rules = {
  required: (value: string) => !!value || 'This field is required.',
  dateTimeOrder: () => {
    if (formData.slot_from && formData.slot_to) {
      // Convert local datetime strings to Date objects for comparison
      const fromDate = new Date(formData.slot_from);
      const toDate = new Date(formData.slot_to);
      if (isValid(fromDate) && isValid(toDate) && fromDate >= toDate) {
        return 'Time "From" must be earlier than time "To".';
      }
    }
    return true;
  }
};

// Show success message
const showSuccessMessage = (message: string) => {
  operationSuccess.value = message;
  setTimeout(() => {
    operationSuccess.value = null;
  }, 5000);
};

// Show error message
const showErrorMessage = (message: string) => {
  operationError.value = message;
  setTimeout(() => {
    operationError.value = null;
  }, 7000);
};

// Date formatting for display
const formatDateTime = (dateString: string | undefined | null): string => {
  if (!dateString) return '';
  try {
    const date = parseISO(dateString);
    return format(date, 'dd.MM.yyyy HH:mm'); // Format for display
  } catch {
    console.warn(`Failed to format date: ${dateString}`);
    return '';
  }
};

// Convert local date to ISO string (for backend)
const toISOString = (localDateTimeString: string): string | null => {
  if (!localDateTimeString) return null;
  try {
    // Convert string from input type="datetime-local" to Date object
    const localDate = new Date(localDateTimeString);
    if (!isValid(localDate)) throw new Error('Invalid date');
    
    // Convert to ISO string (local time expressed as ISO)
    return localDate.toISOString();
  } catch (e) {
    console.error('Error converting to ISO string:', e);
    return null;
  }
};

// Convert ISO string to local format for datetime-local input
const fromISOString = (isoString: string | undefined | null): string => {
  if (!isoString) return '';
  try {
    const date = parseISO(isoString);
    if (!isValid(date)) throw new Error('Invalid ISO date');
    
    // Format for input type="datetime-local"
    return format(date, "yyyy-MM-dd'T'HH:mm");
  } catch (e) {
    console.error('Error converting from ISO string:', e);
    return '';
  }
};

const openAddDialog = () => {
  editingSlot.value = null;
  formData.slot_from = '';
  formData.slot_to = '';
  formData.note = '';
  formError.value = null;
  slotForm.value?.resetValidation(); // Reset validation state
  dialogOpen.value = true;
};

const openEditDialog = (slot: SessionSlot) => {
  editingSlot.value = slot;
  formData.slot_from = fromISOString(slot.slot_from);
  formData.slot_to = fromISOString(slot.slot_to);
  formData.note = slot.note || '';
  formError.value = null;
  slotForm.value?.resetValidation();
  dialogOpen.value = true;
};

const closeDialog = () => {
  dialogOpen.value = false;
};

const saveSlot = async () => {
  formError.value = null;
  
  // Trigger validation
  const validationResult = await slotForm.value?.validate();
  if (!validationResult?.valid) {
    return;
  }

  saving.value = true;
  try {
    const fromISO = toISOString(formData.slot_from);
    const toISO = toISOString(formData.slot_to);

    if (!fromISO || !toISO) {
      throw new Error("Invalid date or time format.");
    }

    if (editingSlot.value) {
      const updateData: SessionSlotUpdate = { 
        slot_from: fromISO, 
        slot_to: toISO, 
        note: formData.note || null 
      };
      await availabilityApi.updateSlot(props.sessionId, editingSlot.value.id, updateData);
      showSuccessMessage('Slot successfully updated.');
    } else {
      const createData: SessionSlotCreate = { 
        slot_from: fromISO, 
        slot_to: toISO, 
        note: formData.note || null 
      };
      await availabilityApi.createSlot(props.sessionId, createData);
      showSuccessMessage('New slot successfully created.');
    }
    emit('slots-updated');
    closeDialog();
  } catch (err: any) {
    formError.value = err.response?.data?.detail || err.message || 'Failed to save slot.';
    console.error("Save Slot Error:", err);
  } finally {
    saving.value = false;
  }
};

const confirmDelete = (slot: SessionSlot) => {
  slotToDelete.value = slot;
  confirmDeleteDialogOpen.value = true;
};

const executeDelete = async () => {
  if (!slotToDelete.value) return;
  deleting.value = true;
  try {
    await availabilityApi.deleteSlot(props.sessionId, slotToDelete.value.id);
    showSuccessMessage('Slot successfully deleted.');
    emit('slots-updated');
    confirmDeleteDialogOpen.value = false;
    slotToDelete.value = null;
  } catch (err: any) {
    showErrorMessage(err.response?.data?.detail || err.message || 'Failed to delete slot.');
    console.error("Delete Slot Error:", err);
    confirmDeleteDialogOpen.value = false;
  } finally {
    deleting.value = false;
  }
};
</script>

<style scoped>
/* We can add some styles if needed */
</style> 