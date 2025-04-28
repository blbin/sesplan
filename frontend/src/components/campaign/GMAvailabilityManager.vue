<template>
  <v-card variant="outlined">
    <v-card-title>Slot Management</v-card-title>
    <v-card-text>
      <v-alert type="info" variant="tonal" density="compact" class="mb-4">
        Here you can add, edit, and delete time slots for availability submissions.
      </v-alert>

      <v-btn color="primary" @click="openAddDialog" class="mb-4">Add slot</v-btn>

      <v-list v-if="localExistingSlots.length > 0" density="compact" bg-color="grey-lighten-4" rounded>
        <v-list-subheader>Existing slots</v-list-subheader>
        <v-list-item 
          v-for="slot in localExistingSlots" 
          :key="slot.id"
          :title="formatSlotTitle(slot)"
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
    <v-dialog v-model="dialogOpen" max-width="600px" persistent>
      <v-card :loading="saving" :disabled="saving">
        <v-card-title>{{ editingSlot ? 'Edit' : 'Add' }} slot</v-card-title>
        <v-card-text>
          <v-form ref="slotFormRef" @submit.prevent="saveSlot">
            <v-row>
              <v-col cols="12">
                <v-menu
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formattedDate"
                      label="Date"
                      prepend-inner-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                      :rules="[rules.required]"
                      required
                    ></v-text-field>
                  </template>
                  <v-date-picker 
                    v-model="formData.date"
                    @update:modelValue="dateMenu = false" 
                    :allowed-dates="allowedDates"
                  ></v-date-picker>
                </v-menu>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="6">
                <v-menu
                  ref="startTimeMenuRef"
                  v-model="startTimeMenu"
                  :close-on-content-click="false"
                  :nudge-right="40"
                  :return-value.sync="formData.startTime"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="290px"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formData.startTime"
                      label="Start time"
                      prepend-inner-icon="mdi-clock-time-four-outline"
                      placeholder="HH:mm"
                      v-bind="props"
                      :rules="[rules.required, rules.timeFormat, rules.timeOrder]"
                      required
                    ></v-text-field>
                  </template>
                  <v-time-picker
                    v-if="startTimeMenu"
                    v-model="formData.startTime"
                    full-width
                    format="24hr"
                    @click:minute="startTimeMenu = false"
                  ></v-time-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" sm="6">
                <v-menu
                  ref="endTimeMenuRef"
                  v-model="endTimeMenu"
                  :close-on-content-click="false"
                  :nudge-right="40"
                  :return-value.sync="formData.endTime"
                  transition="scale-transition"
                  offset-y
                  max-width="290px"
                  min-width="290px"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formData.endTime"
                      label="End time"
                      prepend-inner-icon="mdi-clock-time-four-outline"
                      placeholder="HH:mm"
                      v-bind="props"
                      :rules="[rules.required, rules.timeFormat, rules.timeOrder]"
                      required
                    ></v-text-field>
                  </template>
                  <v-time-picker
                    v-if="endTimeMenu"
                    v-model="formData.endTime"
                    full-width
                    format="24hr"
                    :min="formData.startTime" 
                    @click:minute="endTimeMenu = false"
                  ></v-time-picker>
                </v-menu>
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
import { ref, reactive, computed, watch } from 'vue';
import type { SessionSlot, SessionSlotCreate, SessionSlotUpdate } from '@/types/session_slot';
import * as availabilityApi from '@/services/api/sessionAvailability';
import { format, parseISO, isValid, setHours, setMinutes, setSeconds, setMilliseconds } from 'date-fns';

// Type for Vuetify form validation
type VForm = {
  validate: () => Promise<{ valid: boolean }>;
  reset: () => void;
  resetValidation: () => void;
};

const props = defineProps<{ 
  sessionId: number;
  existingSlots: SessionSlot[];
}>();

// const emit = defineEmits<{ (e: 'slots-updated'): void }>(); // Commented out as it's unused

// Make existingSlots locally reactive for easier updates after API calls
const localExistingSlots = ref<SessionSlot[]>([...props.existingSlots]);
watch(() => props.existingSlots, (newSlots) => {
  localExistingSlots.value = [...newSlots];
});

const dialogOpen = ref(false);
const confirmDeleteDialogOpen = ref(false);
const editingSlot = ref<SessionSlot | null>(null);
const slotToDelete = ref<SessionSlot | null>(null);
const saving = ref(false);
const deleting = ref(false);
const formError = ref<string | null>(null);
const operationError = ref<string | null>(null);
const operationSuccess = ref<string | null>(null);
const slotFormRef = ref<VForm | null>(null); // Ref for v-form validation

// Menu states
const dateMenu = ref(false);
const startTimeMenu = ref(false);
const endTimeMenu = ref(false);

// Form data
const formData = reactive({
  date: null as Date | null, // Store date as Date object
  startTime: '', // HH:mm
  endTime: '', // HH:mm
  note: ''
});

// Computed property for formatted date display in text field
const formattedDate = computed(() => {
  return formData.date ? format(formData.date, 'dd.MM.yyyy') : '';
});

// Prevent selecting past dates
const allowedDates = (val: any): boolean => {
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Set time to beginning of day
  // Ensure val is treated as a Date object for comparison
  // v-date-picker might pass Date objects or date strings
  const dateVal = val instanceof Date ? val : new Date(val);
  if (!isValid(dateVal)) return false; // Reject invalid dates
  return dateVal >= today;
};

const rules = {
  required: (value: any) => !!value || 'This field is required.',
  timeFormat: (value: string) => {
    const pattern = /^([01]\d|2[0-3]):([0-5]\d)$/;
    return pattern.test(value) || 'Invalid format. Use HH:mm (e.g., 09:30 or 14:00).';
  },
  timeOrder: () => {
    if (formData.startTime && formData.endTime) {
      const [startH, startM] = formData.startTime.split(':').map(Number);
      const [endH, endM] = formData.endTime.split(':').map(Number);
      if (startH > endH || (startH === endH && startM >= endM)) {
        return 'Start time must be earlier than end time.';
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

// Date/Time formatting and conversion

// Format slot title for display in the list
const formatSlotTitle = (slot: SessionSlot): string => {
  if (!slot.slot_from || !slot.slot_to) return 'Invalid slot data';
  try {
    const fromDate = parseISO(slot.slot_from);
    const toDate = parseISO(slot.slot_to);
    const dateStr = format(fromDate, 'dd.MM.yyyy');
    const fromTimeStr = format(fromDate, 'HH:mm');
    const toTimeStr = format(toDate, 'HH:mm');
    return `Date: ${dateStr}, Time: ${fromTimeStr} - ${toTimeStr}`;
  } catch (e) {
    console.error("Error formatting slot title:", e);
    return 'Error formatting slot';
  }
};

// Combine date and time string (HH:mm) into a Date object
const combineDateTime = (date: Date | null, timeString: string): Date | null => {
  if (!date || !timeString) return null;
  try {
    const [hours, minutes] = timeString.split(':').map(Number);
    if (isNaN(hours) || isNaN(minutes)) return null;
    let combined = setHours(date, hours);
    combined = setMinutes(combined, minutes);
    combined = setSeconds(combined, 0);
    combined = setMilliseconds(combined, 0);
    return combined;
  } catch (e) {
    console.error("Error combining date and time:", e);
    return null;
  }
};

const openAddDialog = () => {
  editingSlot.value = null;
  // Reset form data
  formData.date = new Date(); // Default to today
  formData.date.setHours(0, 0, 0, 0); // Clear time part for date picker
  formData.startTime = '12:00'; // Default start time
  formData.endTime = '20:00'; // Default end time
  formData.note = '';
  formError.value = null;
  slotFormRef.value?.resetValidation(); // Reset validation state
  dialogOpen.value = true;
};

const openEditDialog = (slot: SessionSlot) => {
  editingSlot.value = slot;
  formError.value = null;
  try {
    const fromDate = parseISO(slot.slot_from);
    const toDate = parseISO(slot.slot_to);
    
    // Set date (without time part for date picker)
    const datePart = new Date(fromDate);
    datePart.setHours(0,0,0,0);
    formData.date = datePart;
    
    formData.startTime = format(fromDate, 'HH:mm');
    formData.endTime = format(toDate, 'HH:mm');
    formData.note = slot.note || '';
    
    slotFormRef.value?.resetValidation();
    dialogOpen.value = true;
  } catch (e) {
    console.error("Error parsing slot dates for editing:", e);
    showErrorMessage("Failed to load slot data for editing.");
    formData.date = null;
    formData.startTime = '';
    formData.endTime = '';
    formData.note = '';
  }
};

const closeDialog = () => {
  dialogOpen.value = false;
};

const saveSlot = async () => {
  formError.value = null;
  
  // Trigger validation
  const validationResult = await slotFormRef.value?.validate();
  if (!validationResult?.valid) {
    formError.value = "Please fill in all required fields correctly.";
    return;
  }

  const fromDateTime = combineDateTime(formData.date, formData.startTime);
  const toDateTime = combineDateTime(formData.date, formData.endTime);

  if (!fromDateTime || !toDateTime) {
    formError.value = "Invalid date or time selected.";
    return;
  }

  if (fromDateTime >= toDateTime) { // Double check order after combining
    formError.value = "Start time must be strictly earlier than end time.";
    return;
  }

  saving.value = true;
  try {
    const fromISO = fromDateTime.toISOString();
    const toISO = toDateTime.toISOString();

    let savedSlot: SessionSlot | null = null;

    if (editingSlot.value) {
      const updateData: SessionSlotUpdate = { 
        slot_from: fromISO, 
        slot_to: toISO, 
        note: formData.note || null 
      };
      savedSlot = await availabilityApi.updateSlot(props.sessionId, editingSlot.value.id, updateData);
      showSuccessMessage('Slot successfully updated.');
      // Update local list
      const index = localExistingSlots.value.findIndex(s => s.id === savedSlot?.id);
      if (index !== -1 && savedSlot) {
        localExistingSlots.value[index] = savedSlot;
      }
    } else {
      const createData: SessionSlotCreate = {
        slot_from: fromISO,
        slot_to: toISO,
        note: formData.note || null
      };
      savedSlot = await availabilityApi.createSlot(props.sessionId, createData);
      showSuccessMessage('Slot successfully created.');
      // Add to local list
      if(savedSlot) {
        localExistingSlots.value.push(savedSlot);
      }
    }
    
    closeDialog();
    // Ensure parent is notified AFTER local state is updated
    // emit('slots-updated'); // Emitting might cause immediate re-render with old props
  } catch (err: any) {
    console.error("Save Slot Error:", err);
    formError.value = err.response?.data?.detail || err.message || 'Failed to save slot.';
    // Ensure error message is a string
    showErrorMessage(formError.value ?? 'An unknown error occurred.'); // Show error in main area too
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
  operationError.value = null; // Clear previous errors
  try {
    await availabilityApi.deleteSlot(props.sessionId, slotToDelete.value.id);
    showSuccessMessage('Slot successfully deleted.');
    confirmDeleteDialogOpen.value = false;
    // Remove from local list
    localExistingSlots.value = localExistingSlots.value.filter(s => s.id !== slotToDelete.value?.id);
    slotToDelete.value = null;
    // emit('slots-updated'); // Notify parent AFTER local state update
  } catch (err: any) {
    console.error("Delete Slot Error:", err);
    showErrorMessage(err.response?.data?.detail || err.message || 'Failed to delete slot.');
    confirmDeleteDialogOpen.value = false; // Close confirm dialog even on error
  } finally {
    deleting.value = false;
  }
};
</script>

<style scoped>
.v-card-text {
  padding-bottom: 16px; /* Ensure padding below content */
}
/* Add more specific styles if needed */
</style> 