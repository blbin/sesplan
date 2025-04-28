<template>
  <tr>
    <td class="time-cell">{{ time }}</td>
    <GridCell
      v-for="day in days"
      :key="`${day.date}-${time}`"
      :date="day.date"
      :time="time"
      :is-active="isActiveCell(day.date, time)"
      :user-available="isUserAvailable(day.date, time)"
      :available-users-count="getAvailableUsersCount(day.date, time)"
      :tooltip-text="getTooltipText(day.date, time)"
      :is-gm="isGm"
      :is-dragging="isDragging"
      :selection-state="getSelectionState(day.date, time)"
      @mousedown="onCellMouseDown"
      @mouseover="onCellMouseOver"
      @mouseup="onCellMouseUp"
      @click="onCellClick"
    />
  </tr>
</template>

<script setup lang="ts">
import GridCell from './GridCell.vue';

// Typy dat a parametry
interface DayInfo {
  date: string;
  label: string;
}

const props = defineProps<{
  time: string;
  days: DayInfo[];
  isGm: boolean;
  isDragging: boolean;
  isActiveCell: (date: string, time: string) => boolean;
  isUserAvailable: (date: string, time: string) => boolean;
  getAvailableUsersCount: (date: string, time: string) => number;
  getTooltipText: (date: string, time: string) => string;
  getSelectionState: (date: string, time: string) => { 
    isInSelection: boolean; 
    isSelectionStart: boolean; 
    isSelectionEnd: boolean; 
    isAdding: boolean 
  } | null;
}>();

// Použití props pro odstranění TS6133 varování
const { time, days, isGm, isDragging, isActiveCell, isUserAvailable, getAvailableUsersCount, getTooltipText, getSelectionState } = props;

// Emity pro propagaci událostí nahoru
const emit = defineEmits<{
  (e: 'cell-mousedown', date: string, time: string): void;
  (e: 'cell-mouseover', date: string, time: string): void;
  (e: 'cell-mouseup'): void;
  (e: 'cell-click', date: string, time: string): void;
}>();

// Handlery událostí
const onCellMouseDown = (date: string, time: string) => {
  emit('cell-mousedown', date, time);
};

const onCellMouseOver = (date: string, time: string) => {
  emit('cell-mouseover', date, time);
};

const onCellMouseUp = () => {
  emit('cell-mouseup');
};

const onCellClick = (date: string, time: string) => {
  emit('cell-click', date, time);
};
</script>

<style scoped>
@import '../styles/availability-grid.css';
</style> 