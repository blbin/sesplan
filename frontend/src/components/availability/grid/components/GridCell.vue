<template>
  <td
    :class="cellClasses"
    @mousedown.prevent="onMouseDown"
    @mouseover="onMouseOver"
    @mouseup="onMouseUp"
    @click="onClick"
  >
    <div class="cell-content">
      <span v-if="availableUsersCount" class="user-count">
        {{ availableUsersCount }}
      </span>
      <v-tooltip activator="parent" location="top">
        {{ tooltipText }}
      </v-tooltip>
    </div>
  </td>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  date: string;
  time: string;
  isActive: boolean;
  userAvailable: boolean;
  availableUsersCount: number;
  tooltipText: string;
  isGm: boolean;
  isDragging: boolean;
  selectionState: {
    isInSelection: boolean;
    isSelectionStart: boolean;
    isSelectionEnd: boolean;
    isAdding: boolean;
  } | null;
}>();

const emit = defineEmits<{
  (e: 'mousedown', date: string, time: string): void;
  (e: 'mouseover', date: string, time: string): void;
  (e: 'mouseup'): void;
  (e: 'click', date: string, time: string): void;
}>();

// Sestavení tříd pro buňku na základě jejího stavu
const cellClasses = computed(() => {
  const classes = ['grid-cell'];
  
  // Základní třídy
  if (props.isActive) classes.push('active-slot');
  else classes.push('inactive-cell');
  
  if (props.userAvailable) classes.push('current-user-available');
  
  if (!props.isGm && props.isActive) {
    classes.push('interactive-cell');
  }
  
  // Třídy pro výběr a tažení
  if (props.selectionState) {
    classes.push(props.selectionState.isAdding ? 'selecting' : 'deselecting');
    
    if (props.selectionState.isSelectionStart) {
      classes.push('selection-start');
    }
    
    if (props.selectionState.isSelectionEnd) {
      classes.push('selection-end');
    }
    
    classes.push('selection-animating');
  }
  
  return classes;
});

// Obsluha událostí
const onMouseDown = () => {
  emit('mousedown', props.date, props.time);
};

const onMouseOver = () => {
  emit('mouseover', props.date, props.time);
};

const onMouseUp = () => {
  emit('mouseup');
};

const onClick = () => {
  emit('click', props.date, props.time);
};
</script>

<style scoped>
@import '../styles/availability-grid.css';
</style> 