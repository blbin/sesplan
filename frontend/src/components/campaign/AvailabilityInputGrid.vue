<template>
  <div class="availability-grid-container">
    <!-- Add loading/error specifically for fetching own availability -->
    <p v-if="isLoadingMine">Načítání mé dostupnosti...</p>
    <p v-if="loadErrorMine" class="text-error">Chyba při načítání mé dostupnosti: {{ loadErrorMine }}</p>

    <div v-if="!isLoadingMine" class="grid">
      <!-- Grid Header (Days/Dates) -->
      <div class="grid-header">
        <div class="time-col-header">Čas</div>
        <div v-for="day in days" :key="day.toISOString()" class="day-col-header">
          {{ formatDayHeader(day) }}
        </div>
      </div>

      <!-- Grid Body (Time Slots) -->
      <div class="grid-body">
        <!-- Time Column -->
        <div class="time-col">
          <div v-for="timeSlot in timeSlots" :key="timeSlot" class="time-slot-label">
            {{ formatTimeLabel(timeSlot) }}
          </div>
        </div>

        <!-- Day Columns -->
        <div v-for="day in days" :key="day.toISOString()" class="day-col">
          <div 
            v-for="timeSlot in timeSlots" 
            :key="timeSlot"
            class="time-slot"
            :class="getSlotClasses(day, timeSlot)"
            @mousedown="startSelection(day, timeSlot)"
            @mouseover="updateSelection(day, timeSlot)"
            @mouseup="endSelection"
          >
            <!-- Display number of available people from the passed prop -->
            <span v-if="getOverlapCount(day, timeSlot) > 0" class="overlap-count">
                {{ getOverlapCount(day, timeSlot) }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add loading/error for saving -->
    <p v-if="isSaving" class="saving-indicator">Ukládání...</p>
    <p v-if="saveError" class="text-error">Chyba při ukládání: {{ saveError }}</p>

    <div class="controls">
        <button @click="saveMyAvailability" color="primary" :loading="isSaving">Uložit moji dostupnost</button>
        <button @click="clearAvailability" :disabled="isSaving">Vymazat moji dostupnost</button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { availabilityService } from '@/services/api/availabilityService'; // Import service
import type { Availability, AvailabilityCreate } from '@/types/availability';
// Import date-fns functions
import { format, startOfDay, addDays, addMinutes, parseISO, isWithinInterval, isEqual, compareAsc } from 'date-fns';

interface Props {
  sessionId: number;
  allAvailabilities: Availability[]; // Received from parent
  currentUserId: number | undefined; // Needed to identify user
}

const props = defineProps<Props>();

// --- Emit definition ---
const emit = defineEmits(['availability-updated']);

// --- Local state for own availability --- 
const myAvailabilities = ref<Availability[]>([]);
const isLoadingMine = ref(false);
const loadErrorMine = ref<string | null>(null);
const isSaving = ref(false);
const saveError = ref<string | null>(null);

// --- Grid Configuration --- 
const days = ref<Date[]>([]); // Array of dates to display
const timeSlots = ref<number[]>([]); // Array of minutes from midnight (e.g., 0, 30, 60, ...)
const slotDurationMinutes = 30; // Duration of each time slot

// --- Selection State --- 
const isSelecting = ref(false); // Declare as ref
const selectionStartSlot = ref<{ day: Date, time: number } | null>(null); // Declare as ref
const selectedSlots = ref<Set<string>>(new Set()); // Declare as ref, Stores keys like "YYYY-MM-DDTHH:mm:ssZ_minutes"

// --- Lifecycle and Watchers --- 
onMounted(() => {
  initializeGrid();
  if (props.sessionId) {
    fetchMyAvailability(); // Fetch only own availability on mount
  }
});

watch(() => props.sessionId, (newSessionId) => {
  if (newSessionId) {
    initializeGrid();
    fetchMyAvailability(); // Fetch own availability for the new session
    selectedSlots.value.clear();
  }
});

// Watch the fetched availability to update the grid selection
watch(myAvailabilities, (newAvailabilities) => {
    updateSelectedSlotsFromMyAvailabilities(newAvailabilities);
}, { deep: true, immediate: true }); // Use deep watch for array changes

// --- API Calls --- 
async function fetchMyAvailability() {
    if (!props.sessionId) return;
    isLoadingMine.value = true;
    loadErrorMine.value = null;
    try {
        // Service function now returns a list
        myAvailabilities.value = await availabilityService.getMyAvailability(props.sessionId);
    } catch (err: any) {
        // API should return empty list if none found, not 404
        loadErrorMine.value = err.message || 'Failed to fetch my availability';
        console.error("Fetch My Availability Error:", err);
        myAvailabilities.value = []; // Reset on error
    } finally {
        isLoadingMine.value = false;
    }
}

// Renamed from submitAvailability to saveMyAvailability and updated logic
async function saveMyAvailability() {
    if (!props.sessionId) return;

    const availabilityBlocks = calculateAvailabilityBlocks();
    if (availabilityBlocks.length === 0) {
        // If user cleared selection, treat as delete
        await clearAvailability();
        return;
    }

    isSaving.value = true;
    saveError.value = null;
    try {
        // Use the updated service method that accepts a list
        // The service method itself should return the correct type (Availability[])
        const updatedList = await availabilityService.setMyAvailability(props.sessionId, availabilityBlocks);
        myAvailabilities.value = updatedList;
        emit('availability-updated'); // Notify parent
    } catch (err: any) {
        saveError.value = err.message || 'Failed to save availability';
        console.error("Save Availability Error:", err);
    } finally {
        isSaving.value = false;
    }
}

// Renamed from deleteMyAvailability to clearAvailability
async function clearAvailability() {
    if (!props.sessionId) return;
    // Only call delete if there's something to delete (i.e., user had previous availability)
    if (myAvailabilities.value.length === 0 && selectedSlots.value.size === 0) {
        return; // Nothing to clear
    }

    isSaving.value = true; 
    saveError.value = null;
    try {
        await availabilityService.deleteMyAvailability(props.sessionId);
        myAvailabilities.value = []; // Clear local state
        selectedSlots.value.clear(); // Clear selection visually
        emit('availability-updated'); // Notify parent
    } catch (err: any) {
        saveError.value = err.message || 'Failed to delete availability';
        console.error("Delete Availability Error:", err);
    } finally {
        isSaving.value = false;
    }
}

// --- Grid Initialization --- 
function initializeGrid() {
  const today = startOfDay(new Date());
  days.value = Array.from({ length: 7 }, (_, i) => addDays(today, i));
  timeSlots.value = [];
  for (let minutes = 8 * 60; minutes < 22 * 60; minutes += slotDurationMinutes) {
    timeSlots.value.push(minutes);
  }
  timeSlots.value.push(22 * 60);
}

// --- Formatting Helpers (using date-fns placeholders) --- 
function formatDayHeader(date: Date): string {
  return format(date, 'EEE dd/MM'); // Use imported format
  // return date.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'numeric' });
}

function formatTimeLabel(minutes: number): string {
  const date = startOfDay(new Date());
  const timeDate = addMinutes(date, minutes);
  return format(timeDate, 'HH:mm');
}

// --- Slot Calculation and Styling --- 
function getSlotKey(day: Date, time: number): string {
    const slotStartDateTime = addMinutes(startOfDay(day), time); // Ensure we use startOfDay
    // Use ISO string without milliseconds for consistency
    return `${slotStartDateTime.toISOString().split('.')[0]}Z_${time}`;
}

function parseSlotKey(key: string): { start: Date, time: number } | null {
    const parts = key.split('_');
    if (parts.length !== 2) return null;
    try {
        const start = parseISO(parts[0]);
        const time = parseInt(parts[1], 10);
        if (isNaN(time)) return null;
        return { start, time };
    } catch (e) {
        console.error("Error parsing slot key:", key, e);
        return null;
    }
}

function getSlotDateTimeRange(day: Date, time: number): { start: Date, end: Date } {
    const start = addMinutes(startOfDay(day), time); // Ensure we use startOfDay
    const end = addMinutes(start, slotDurationMinutes);
    return { start, end };
}

function getSlotClasses(day: Date, time: number): Record<string, boolean> {
  const key = getSlotKey(day, time);
  const overlap = getOverlapCount(day, time);

  return {
    selected: selectedSlots.value.has(key),
    selecting: isSelecting.value,
    overlap_1: overlap === 1,
    overlap_2: overlap === 2,
    overlap_3_plus: overlap >= 3,
  };
}

function getOverlapCount(day: Date, time: number): number {
    const { start, end } = getSlotDateTimeRange(day, time);
    let count = 0;
    for (const availability of props.allAvailabilities) {
        try {
            const availableFrom = parseISO(availability.available_from); // Use imported parseISO
            const availableTo = parseISO(availability.available_to); // Use imported parseISO
            
            // More robust interval overlap check needed. 
            // Check if the user's interval overlaps the slot's interval.
            // Overlap definition: max(start1, start2) < min(end1, end2)
            const intervalStart = start > availableFrom ? start : availableFrom;
            const intervalEnd = end < availableTo ? end : availableTo;

            if (intervalStart < intervalEnd) { // If they overlap
                count++;
            }
            
            // Simpler alternative (counts if slot START is within user availability):
            // if (isWithinInterval(start, { start: availableFrom, end: availableTo })) { // Use imported isWithinInterval
            //    count++;
            // }
        } catch (e) {
            console.error("Error parsing availability dates:", availability, e);
        }
    }
    return count;
}

// --- Selection Logic --- 
function startSelection(day: Date, time: number) {
    isSelecting.value = true;
    selectionStartSlot.value = { day, time };
    toggleSlotSelection(day, time); // Select the first slot immediately
}

function updateSelection(day: Date, time: number) {
    if (!isSelecting.value || !selectionStartSlot.value) return;
    
    // Clear previous temporary selection range (more complex logic needed for efficient range selection)
    // For now, just toggle the current slot - this makes drag selection additive/subtractive
    // A more robust implementation would calculate the rectangle and update selectedSlots accordingly.
    // Let's keep it simple: just toggle the slot on mouseover while dragging.
    toggleSlotSelection(day, time);

}

function endSelection() {
    isSelecting.value = false;
    selectionStartSlot.value = null;
}

// Helper to add/remove a single slot
function toggleSlotSelection(day: Date, time: number) {
    const key = getSlotKey(day, time);
    if (selectedSlots.value.has(key)) {
        selectedSlots.value.delete(key);
    } else {
        selectedSlots.value.add(key);
    }
}

// Helper function to populate selectedSlots based on fetched availability
// Renamed from updateSelectedSlotsFromMyAvailability
function updateSelectedSlotsFromMyAvailabilities(availabilities: Availability[]) {
    selectedSlots.value.clear();
    if (!availabilities || availabilities.length === 0) return;

    availabilities.forEach(avail => {
        try {
            const availStart = parseISO(avail.available_from);
            const availEnd = parseISO(avail.available_to);

            for (const day of days.value) {
                const currentDayStart = startOfDay(day);
                for (const time of timeSlots.value) {
                    const slotStart = addMinutes(currentDayStart, time);
                    // Removed unused slotEnd
                    // const slotEnd = addMinutes(slotStart, slotDurationMinutes);

                    // Check if the slot *center* is within the availability interval
                    // This avoids issues with exclusive end times
                    const slotCenter = addMinutes(slotStart, slotDurationMinutes / 2);
                    
                    if (isWithinInterval(slotCenter, { start: availStart, end: availEnd })) {
                        const key = getSlotKey(day, time);
                        selectedSlots.value.add(key);
                    }
                }
            }
        } catch(e) {
            console.error("Error processing availability record:", avail, e);
        }
    });
}

// --- Logic to Calculate Availability Blocks --- 
function calculateAvailabilityBlocks(): AvailabilityCreate[] {
    const blocks: AvailabilityCreate[] = [];
    if (selectedSlots.value.size === 0) {
        return blocks;
    }

    // 1. Parse all selected slot keys into date objects
    const parsedSlots = Array.from(selectedSlots.value)
        .map(parseSlotKey)
        .filter(slot => slot !== null) as { start: Date, time: number }[];

    // 2. Sort slots chronologically
    parsedSlots.sort((a, b) => compareAsc(a.start, b.start));

    // 3. Group consecutive slots into blocks
    let currentBlockStart: Date | null = null;
    let currentBlockEnd: Date | null = null;

    for (let i = 0; i < parsedSlots.length; i++) {
        const slot = parsedSlots[i];
        const slotEnd = addMinutes(slot.start, slotDurationMinutes);

        if (currentBlockStart === null) {
            // Start the first block
            currentBlockStart = slot.start;
            currentBlockEnd = slotEnd;
        } else if (currentBlockEnd !== null && isEqual(slot.start, currentBlockEnd)) {
            // Extend the current block if the current slot starts exactly where the previous one ended
            currentBlockEnd = slotEnd;
        } else {
            // Finish the previous block and start a new one
            if (currentBlockStart && currentBlockEnd) { // Type guard
                 // Ensure dates are converted to ISO strings for the AvailabilityCreate type
                blocks.push({
                    available_from: currentBlockStart.toISOString(),
                    available_to: currentBlockEnd.toISOString(),
                    note: null
                });
            }
            currentBlockStart = slot.start;
            currentBlockEnd = slotEnd;
        }
    }

    // Add the last block if it exists
    if (currentBlockStart !== null && currentBlockEnd !== null) {
         // Ensure dates are converted to ISO strings for the AvailabilityCreate type
        blocks.push({
            available_from: currentBlockStart.toISOString(),
            available_to: currentBlockEnd.toISOString(),
            note: null
        });
    }

    return blocks;
}

</script>

<style scoped>
.availability-grid-container {
  /* Basic styling */
  font-family: sans-serif;
  position: relative; /* For potential absolute positioned saving indicators */
}

.grid {
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  margin-bottom: 1rem;
  user-select: none; /* Prevent text selection during drag */
}

.grid-header {
  display: flex;
  background-color: #f0f0f0;
  font-weight: bold;
}

.grid-body {
  display: flex;
}

.time-col-header,
.day-col-header {
  padding: 0.5rem;
  text-align: center;
  border-left: 1px solid #ccc;
  flex: 1;
}

.time-col-header {
  flex: 0 0 80px; /* Fixed width for time labels */
  border-left: none;
}

.time-col,
.day-col {
  display: flex;
  flex-direction: column;
  border-left: 1px solid #ccc;
}

.time-col {
  flex: 0 0 80px; /* Fixed width for time labels */
  border-left: none;
  background-color: #f8f8f8;
}

.day-col {
  flex: 1;
}

.time-slot-label {
  padding: 0.3rem 0.5rem;
  height: 25px; /* Match time-slot height */
  box-sizing: border-box;
  text-align: right;
  font-size: 0.8em;
  color: #555;
  border-top: 1px solid #eee;
}

.time-slot {
  height: 25px;
  border-top: 1px solid #eee;
  background-color: #fff;
  cursor: pointer;
  position: relative; /* For overlap count positioning */
  transition: background-color 0.1s ease-in-out;
}

.time-slot:hover {
  background-color: #e0e0e0; 
}

.time-slot.selected {
  background-color: #a5d6a7; /* Light green */
  border-color: #66bb6a; /* Darker green border */
}

/* Overlap styling */
.time-slot.overlap_1 {
   background-color: #e6f7e6; /* Very light green */
}
.time-slot.overlap_2 {
   background-color: #c0ebc0;
}
.time-slot.overlap_3_plus {
   background-color: #99df99;
}

.time-slot.selected.overlap_1,
.time-slot.selected.overlap_2,
.time-slot.selected.overlap_3_plus {
    background-color: #4caf50; /* Darker green when selected and overlapping */
    border: 1px dashed #388e3c;
}

.overlap-count {
    position: absolute;
    top: 1px;
    right: 2px;
    font-size: 0.7em;
    color: #555;
    background-color: rgba(255, 255, 255, 0.6);
    padding: 0 2px;
    border-radius: 2px;
}

.controls {
    margin-top: 1rem;
    display: flex;
    gap: 1rem;
}

.saving-indicator {
    font-style: italic;
    color: #555;
    margin-top: 0.5rem;
}

.text-error {
    color: rgb(var(--v-theme-error));
}

</style> 