<template>
  <div class="availability-grid-container" @mouseup="endSelection" @mouseleave="endSelection">
    <!-- Loading/Error for own availability -->
    <p v-if="isLoadingMine">Načítání mé dostupnosti...</p>
    <p v-if="loadErrorMine" class="text-error">Chyba při načítání mé dostupnosti: {{ loadErrorMine }}</p>

    <div v-if="!isLoadingMine && days.length > 0 && timeSlots.length > 0" class="grid-wrapper">
        <AvailabilityGridHeader :days="days" />
        <div class="grid-body-wrapper">
            <AvailabilityGridTimeColumn :time-slots="timeSlots" />
            <!-- Main Grid Area -->
            <div class="grid-days-area">
                <div v-for="day in days" :key="day.toISOString()" class="day-col">
                    <TimeSlot
                        v-for="timeSlot in timeSlots"
                        :key="timeSlot"
                        :day="day"
                        :time-slot="timeSlot"
                        :is-selected="selectedSlots.has(getSlotKey(day, timeSlot))"
                        :overlap-count="getOverlapCount(day, timeSlot)"
                        :is-selecting="isSelecting"
                        @slot-mousedown="startSelection"
                        @slot-mouseover="updateSelection"
                        @slot-mouseup="endSelection"
                    />
                </div>
            </div>
        </div>
    </div>
    <div v-else-if="!isLoadingMine">
        <p>Nelze inicializovat mřížku.</p>
    </div>

    <!-- Saving Indicator/Error -->
    <p v-if="isSaving" class="saving-indicator">Ukládání...</p>
    <p v-if="saveError" class="text-error">Chyba při ukládání: {{ saveError }}</p>

    <!-- Controls -->
    <div class="controls">
        <button @click="handleSave" :disabled="isSaving">Uložit moji dostupnost</button>
        <button @click="handleClear" :disabled="isSaving">Vymazat moji dostupnost</button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, toRef } from 'vue';
import { startOfDay, addDays, addMinutes, parseISO } from 'date-fns';
import type { Availability } from '@/types/availability';

// Import composables and components
import { useMyAvailabilityApi } from '@/composables/useMyAvailabilityApi';
import { useAvailabilitySelection } from '@/composables/useAvailabilitySelection';
import AvailabilityGridHeader from './AvailabilityGridHeader.vue';
import AvailabilityGridTimeColumn from './AvailabilityGridTimeColumn.vue';
import TimeSlot from './TimeSlot.vue';

interface Props {
  sessionId: number;
  allAvailabilities: Availability[]; // Received from parent
  // currentUserId: number | undefined; // No longer directly needed here if API logic is self-contained
}

const props = defineProps<Props>();
const emit = defineEmits(['availability-updated']);

// --- Grid Configuration --- 
const days = ref<Date[]>([]); // Array of dates to display
const timeSlots = ref<number[]>([]); // Array of minutes from midnight (e.g., 0, 30, 60, ...)
const slotDurationMinutes = 30; // Duration of each time slot

// --- Use Composables ---
const sessionIdRef = toRef(props, 'sessionId'); // Pass sessionId as a Ref
const { 
    myAvailabilities, 
    isLoadingMine, 
    loadErrorMine, 
    isSaving, 
    saveError, 
    saveMyAvailability, 
    clearMyAvailabilityOnServer 
} = useMyAvailabilityApi(sessionIdRef);

const { 
    isSelecting, 
    selectedSlots, 
    startSelection, 
    updateSelection, 
    endSelection, 
    updateSelectedSlotsFromMyAvailabilities, 
    calculateAvailabilityBlocks,
    getSlotKey,
    clearLocalSelection
} = useAvailabilitySelection(myAvailabilities, slotDurationMinutes);

// --- Lifecycle and Watchers --- 
onMounted(() => {
  initializeGrid();
  // API call is now handled within useMyAvailabilityApi based on sessionIdRef changes
});

// Watch for changes in sessionId from props to potentially re-initialize grid or clear state if needed
watch(() => props.sessionId, (newSessionId) => {
  if (newSessionId) {
    initializeGrid();
    // Data fetching is reactive via the composable
    // Clear local selection when session changes
    clearLocalSelection(); 
  } else {
    // Clear grid if session becomes invalid
    days.value = [];
    timeSlots.value = [];
    clearLocalSelection();
  }
});

// Watch the API-fetched availability to update the selection state
watch(myAvailabilities, (newAvailabilities) => {
    updateSelectedSlotsFromMyAvailabilities(newAvailabilities);
}, { deep: true }); // No immediate needed as composable handles initial load

// --- Grid Initialization --- 
function initializeGrid() {
  // TODO: Potentially make the start day dynamic (e.g., based on session start?)
  const gridStartDate = startOfDay(new Date()); 
  days.value = Array.from({ length: 7 }, (_, i) => addDays(gridStartDate, i));
  
  const startTimeMinutes = 8 * 60; // 8:00 AM
  const endTimeMinutes = 22 * 60; // 10:00 PM
  
  const generatedTimeSlots = [];
  for (let minutes = startTimeMinutes; minutes < endTimeMinutes; minutes += slotDurationMinutes) {
    generatedTimeSlots.push(minutes);
  }
  timeSlots.value = generatedTimeSlots; 
}

// --- Slot Calculation and Styling --- 
function getSlotDateTimeRange(day: Date, time: number): { start: Date, end: Date } {
    const start = addMinutes(startOfDay(day), time);
    const end = addMinutes(start, slotDurationMinutes);
    return { start, end };
}

// Recalculate overlap based on props
function getOverlapCount(day: Date, time: number): number {
    const { start: slotStart, end: slotEnd } = getSlotDateTimeRange(day, time);
    let count = 0;
    // Filter out own availability from the count if needed, but API should handle this separation
    const otherAvailabilities = props.allAvailabilities; //.filter(a => a.user_id !== props.currentUserId);

    for (const availability of otherAvailabilities) {
        try {
            const availableFrom = parseISO(availability.available_from);
            const availableTo = parseISO(availability.available_to);
            
            // Check for overlap: (AvailStart < SlotEnd) and (AvailEnd > SlotStart)
            if (availableFrom < slotEnd && availableTo > slotStart) {
                count++;
            }
        } catch (e) {
            console.error("Error parsing availability for overlap:", availability, e);
        }
    }
    return count;
}

// --- Control Handlers ---
async function handleSave() {
    const blocks = calculateAvailabilityBlocks();
    
    // If selection resulted in empty blocks (e.g., user deselected everything that was previously saved)
    // treat it as a clear operation.
    if (blocks.length === 0 && myAvailabilities.value.length > 0) { 
        const success = await clearMyAvailabilityOnServer();
        if (success) {
            clearLocalSelection(); // Ensure visual consistency after successful clear
            emit('availability-updated');
        }
    } else if (blocks.length > 0) {
        const success = await saveMyAvailability(blocks);
        if (success) {
             emit('availability-updated');
        }
    } else {
        // No blocks to save and nothing previously saved, do nothing.
        console.log("No changes to save.");
    }
}

async function handleClear() {
    // Check if there's anything selected locally or saved remotely
    if (selectedSlots.value.size > 0 || myAvailabilities.value.length > 0) {
        const success = await clearMyAvailabilityOnServer();
        if (success) {
            clearLocalSelection(); // Clear visual selection
            emit('availability-updated');
        }
    }
}

</script>

<style scoped>
.availability-grid-container {
  /* Container styling */
  margin: 1em 0;
  /* Add mouseup/mouseleave listeners here to catch selection end */
}

.grid-wrapper {
  /* Wrapper for header and body */
  border: 1px solid #ccc;
  position: relative; /* Needed for sticky header */
}

.grid-body-wrapper {
    display: grid;
    grid-template-columns: 60px 1fr; /* Time column + Main grid area */
    /* Consider overflow for scrolling if the grid is too tall */
    max-height: 60vh; 
    overflow-y: auto;
}

.grid-days-area {
    display: grid;
    grid-template-columns: repeat(7, 1fr); /* 7 day columns */
}

.day-col {
  display: flex;
  flex-direction: column;
  border-left: 1px solid #eee;
}
.day-col:first-child {
    border-left: none;
}


.controls {
  margin-top: 1em;
  display: flex;
  gap: 1em;
}

.saving-indicator,
.text-error {
  margin-top: 0.5em;
  font-size: 0.9em;
}

.text-error {
  color: red;
}

/* Inherited styles from sub-components will apply unless overridden */
/* Ensure sub-component styles are not scoped if they need to be global or use :deep() */

</style> 