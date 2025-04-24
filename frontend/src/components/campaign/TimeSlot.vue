<template>
  <div
    class="time-slot"
    :class="slotClasses"
    @mousedown="emit('slot-mousedown', day, timeSlot)"
    @mouseover="emit('slot-mouseover', day, timeSlot)"
    @mouseup="emit('slot-mouseup')"
  >
    <span v-if="overlapCount > 0" class="overlap-count">
      {{ overlapCount }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  day: Date;
  timeSlot: number; // Minutes from midnight
  isSelected: boolean;
  isSelecting: boolean; // Needed for cursor style during selection
  overlapCount: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'slot-mousedown', day: Date, timeSlot: number): void;
  (e: 'slot-mouseover', day: Date, timeSlot: number): void;
  (e: 'slot-mouseup'): void;
}>();

const slotClasses = computed(() => ({
  selected: props.isSelected,
  selecting: props.isSelecting, // Apply cursor style if selection is happening anywhere
  overlap_1: props.overlapCount === 1,
  overlap_2: props.overlapCount === 2,
  overlap_3_plus: props.overlapCount >= 3,
}));

</script>

<style scoped>
.time-slot {
  border: 1px solid #eee;
  min-height: 25px; /* Adjust as needed */
  position: relative;
  cursor: pointer;
  background-color: #fff; /* Default */
  transition: background-color 0.1s ease-in-out;
  user-select: none; /* Prevent text selection during drag */
}

.time-slot.selecting {
  cursor: grabbing; /* Indicate selection in progress */
}

.time-slot.selected {
  background-color: #4CAF50; /* Green for selected */
}

.overlap-count {
  position: absolute;
  top: 1px;
  right: 3px;
  font-size: 0.7em;
  color: #555;
  font-weight: bold;
  pointer-events: none; /* Make sure it doesn't interfere with clicks */
}

/* Styles for different overlap counts */
.time-slot.overlap_1 {
  background-color: rgba(255, 235, 59, 0.3); /* Light Yellow */
}
.time-slot.overlap_2 {
  background-color: rgba(255, 193, 7, 0.4); /* Yellow */
}
.time-slot.overlap_3_plus {
  background-color: rgba(255, 152, 0, 0.5); /* Orange */
}

/* Selected slots always override overlap background */
.time-slot.selected {
  background-color: #4CAF50; /* Green */
}
.time-slot.selected .overlap-count {
    color: white; /* Make overlap count visible on green */
}

</style> 