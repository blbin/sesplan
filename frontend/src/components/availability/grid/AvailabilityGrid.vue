<template>
  <v-card variant="tonal">
    <v-card-text>
      <v-alert v-if="!isGm" type="info" density="compact" class="mb-4" variant="tonal" border="start">
        <v-icon start icon="mdi-information" class="mr-2"></v-icon>
        Kliknutím nebo tažením myši v aktivních slotech označte časy, kdy jste dostupní.
        Opětovným kliknutím/tažením označenou oblast odstraníte.
      </v-alert>

      <div v-if="days.length" class="availability-grid-container">
        <table class="availability-grid">
          <!-- Hlavička s dny -->
          <GridHeader :days="days" />
          
          <!-- Tělo tabulky s řádky pro každý časový slot -->
          <tbody>
            <GridRow
              v-for="time in timeSlots"
              :key="time"
              :time="time"
              :days="days"
              :is-gm="isGm"
              :is-dragging="isDragging"
              :is-active-cell="isActiveCell"
              :is-user-available="isUserAvailableWrapper"
              :get-available-users-count="getAvailableUsersCount"
              :get-tooltip-text="getTooltipText"
              :get-selection-state="getSelectionState"
              @cell-mousedown="handleCellMouseDown"
              @cell-mouseover="handleCellMouseOver"
              @cell-mouseup="handleMouseUp"
              @cell-click="handleCellClick"
            />
          </tbody>
        </table>
      </div>
      <div v-else class="text-center pa-5 text-disabled">
        Nejsou definovány žádné časové sloty.
      </div>

      <!-- Zpětná vazba (chyby a úspěchy) -->
      <div v-if="error" class="text-error mt-3">
        <v-alert type="error" density="compact" variant="tonal">
          {{ error }}
        </v-alert>
      </div>
      <div v-if="successMessage" class="text-success mt-3">
        <v-alert type="success" density="compact" variant="tonal">
          {{ successMessage }}
        </v-alert>
      </div>

      <!-- Legenda -->
      <GridLegend v-if="!isGm" />

      <!-- Překrytí při zpracování požadavku -->
      <v-overlay v-model="isProcessing" class="align-center justify-center" persistent>
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-overlay>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue';
import { useGridData } from './composables/useGridData';
import { useSelectionState } from './composables/useSelectionState';
import { useAvailabilityActions } from './composables/useAvailabilityActions';
import type { SessionSlot } from '@/types/session_slot';
import type { UserAvailability } from '@/types/user_availability';

// Podkomponenty
import GridHeader from './components/GridHeader.vue';
import GridRow from './components/GridRow.vue';
import GridLegend from './components/GridLegend.vue';

// Props a emity
const props = defineProps<{
  sessionId: number;
  currentUserId: number;
  isGm: boolean;
  slots: SessionSlot[];
  userAvailabilities: UserAvailability[];
}>();

const emit = defineEmits<{
  (e: 'availability-changed'): void;
}>();

// Composables
const gridData = useGridData({
  slots: props.slots,
  userAvailabilities: props.userAvailabilities
});

const selectionState = useSelectionState();
const { 
  isDragging, 
  selection, 
  reset, 
  updateSelection, 
  getSelectionClassification 
} = selectionState;

const availabilityActions = useAvailabilityActions();
const { 
  error, 
  successMessage, 
  isProcessing, 
  setUserAvailability, 
  processSelection 
} = availabilityActions;

// Pomocné funkce, které zapouzdřují volání z gridData
const { 
  days,
  timeSlots,
  isActiveCell, 
  getSlotId, 
  getAvailableUsersCount, 
  getTooltipText 
} = gridData;

// Wrapper pro isUserAvailable, který automaticky předá currentUserId
const isUserAvailableWrapper = (date: string, time: string) => {
  return gridData.isUserAvailable(date, time, props.currentUserId);
};

// Získání klasifikace stavu výběru pro buňku
const getSelectionState = (date: string, time: string) => {
  return getSelectionClassification(date, time);
};

// Obsluha kliknutí na buňku (jeden výběr)
async function handleCellClick(date: string, time: string) {
  if (isDragging.value) return;
  if (!isActiveCell(date, time) || props.isGm || isProcessing.value) return;
  
  const sid = getSlotId(date, time);
  if (sid === null) return;
  
  const isAdding = !isUserAvailableWrapper(date, time);
  
  selection.cells.clear();
  selection.cells.add(`${date}-${time}`);
  selection.slotId = sid;
  selection.isAdding = isAdding;
  
  const success = await setUserAvailability(date, time, sid, isAdding, props.sessionId);
  if (success) {
    emit('availability-changed');
  }
  reset();
}

// Obsluha stisknutí myši na buňce (zahájení tažení)
function handleCellMouseDown(date: string, time: string) {
  if (!isActiveCell(date, time) || props.isGm || isProcessing.value) return;
  
  // Kontrola platnosti data a času
  if (!date || !time || date.split('-').length !== 3 || time.split(':').length !== 2) {
    console.error('Neplatný formát data nebo času při mousedown:', { date, time });
    return;
  }
  
  isDragging.value = true;
  const key = `${date}-${time}`;
  const sid = getSlotId(date, time);
  selection.startCell = { date, time };
  selection.cells.clear();
  selection.cells.add(key);
  selection.slotId = sid;
  selection.isAdding = !isUserAvailableWrapper(date, time);
  document.addEventListener('mouseup', handleMouseUp, { once: true });
}

// Obsluha přejetí myši nad buňkou (rozšíření tažení)
function handleCellMouseOver(date: string, time: string) {
  if (!isDragging.value || !selection.startCell) return;
  
  // Kontrola, zda jsme ve stejném slotu
  const currentSlotId = getSlotId(date, time);
  if (currentSlotId !== selection.slotId) return;
  
  // Aktualizace výběru
  selection.endCell = { date, time };
  
  // Zajistíme, že se výběr vždy aktualizuje
  const oldSize = selection.cells.size;
  updateSelection(
    selection.startCell, 
    selection.endCell, 
    days.value.map(d => d.date), 
    timeSlots.value, 
    isActiveCell, 
    getSlotId
  );
  
  // Force reaktivitu
  if (oldSize === selection.cells.size) {
    // Pokud se velikost nezměnila, přesto oznámíme změnu
    // Tím zajistíme, že se znovu vykreslí vizuální stav výběru
    const temp = [...selection.cells];
    selection.cells.clear();
    temp.forEach(cell => selection.cells.add(cell));
  }
}

// Obsluha uvolnění myši (dokončení tažení)
async function handleMouseUp() {
  if (!isDragging.value || selection.cells.size === 0) {
    reset();
    isDragging.value = false;
    return;
  }
  
  if (!selection.startCell || !selection.slotId) {
    reset();
    isDragging.value = false;
    return;
  }
  
  isDragging.value = false;
  const success = await processSelection(
    selection.cells, 
    selection.isAdding, 
    selection.slotId, 
    props.sessionId
  );
  
  if (success) {
    emit('availability-changed');
  }
  
  reset();
}

// Inicializace při změně props
function initializeData() {
  gridData.initializeData(props.currentUserId);
}

// Lifecycle hooks
onMounted(() => {
  initializeData();
});

// Watchers
watch(
  [() => props.slots, () => props.userAvailabilities],
  () => {
    initializeData();
  }
);
</script>

<style scoped>
@import './styles/availability-grid.css';
</style> 