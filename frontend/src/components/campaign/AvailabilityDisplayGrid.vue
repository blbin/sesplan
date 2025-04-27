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
            <thead>
              <tr>
                <th class="time-header">Čas</th>
                <th v-for="day in days" :key="day.date" class="day-header">
                  {{ day.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="time in timeSlots" :key="time">
                <td class="time-cell">{{ time }}</td>
                <td
                  v-for="day in days"
                  :key="`${day.date}-${time}`"
                  :class="cellClass(day.date, time)"
                  @mousedown.prevent="handleMouseDown(day.date, time)"
                  @mouseover="handleMouseOver(day.date, time)"
                  @mouseup="handleMouseUp"
                  @click="handleClick(day.date, time)"
                >
                  <div class="cell-content">
                    <span v-if="getAvailableUsersCount(day.date, time)" class="user-count">
                      {{ getAvailableUsersCount(day.date, time) }}
                    </span>
                    <v-tooltip activator="parent" location="top">
                      {{ getTooltipText(day.date, time) }}
                    </v-tooltip>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center pa-5 text-disabled">
          Nejsou definovány žádné časové sloty.
        </div>
  
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

        <div v-if="!isGm" class="text-center mt-4">
          <div class="d-flex justify-center flex-wrap gap-2">
            <div class="legend-item">
              <span class="legend-color" style="background-color: rgba(0,0,0,0.05)"></span>
              <span class="legend-text">Neaktivní</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: white; border: 1px solid #ddd"></span>
              <span class="legend-text">Aktivní slot</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: rgba(76,175,80,0.3)"></span>
              <span class="legend-text">Jste dostupní</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: rgba(76,175,80,0.5)"></span>
              <span class="legend-text">Vybíráte dostupnost</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: rgba(244,67,54,0.2)"></span>
              <span class="legend-text">Odebíráte dostupnost</span>
            </div>
          </div>
        </div>

        <v-overlay v-model="isProcessing" class="align-center justify-center" persistent>
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        </v-overlay>
      </v-card-text>
    </v-card>
  </template>
  
  <script setup lang="ts">
  import { ref, computed, shallowReactive, watch } from 'vue';
  import { format, parseISO, addMinutes } from 'date-fns';
  import type { SessionSlot } from '@/types/session_slot';
  import type { UserAvailability } from '@/types/user_availability';
  import type { UserSimple } from '@/types/user';
  import * as availabilityApi from '@/services/api/sessionAvailability';
  
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
  
  // Stav komponenty
  type SlotMap = Map<string, Map<string, number>>;
  type AvailabilityMap = Map<string, Map<string, Map<number, UserSimple[]>>>;
  type UserAvailabilityMap = Map<string, Map<string, Set<number>>>;
  
  const error = ref('');
  const successMessage = ref('');
  const isProcessing = ref(false);
  const isDragging = ref(false);
  
  // Mapy: react. sledování pouze první úrovně
  const slotMap = shallowReactive<SlotMap>(new Map());
  const availabilityMap = shallowReactive<AvailabilityMap>(new Map());
  const userAvailabilityMap = shallowReactive<UserAvailabilityMap>(new Map());
  
  // Výběr při tažení
  const selection = shallowReactive({
    startCell: null as { date: string; time: string } | null,
    cells: new Set<string>(),
    slotId: null as number | null,
    isAdding: true,
  });
  
  const TIME_INCREMENT = 30;
  
  // Hlavičky
  const days = computed(() => {
    const daysArr: { date: string; label: string }[] = [];
    const seen = new Set<string>();
    for (const slot of props.slots) {
      const dt = parseISO(slot.slot_from);
      if (isNaN(dt.getTime())) continue;
      const date = format(dt, 'yyyy-MM-dd');
      if (!seen.has(date)) {
        seen.add(date);
        daysArr.push({ date, label: format(dt, 'EEE d.M.') });
      }
    }
    return daysArr.sort((a, b) => a.date.localeCompare(b.date));
  });
  
  // Časové sloty
  const timeSlots = computed<string[]>(() => {
    let minHour = 24, maxHour = 0;
    
    for (const slot of props.slots) {
      const start = parseISO(slot.slot_from);
      const end = parseISO(slot.slot_to);
      if (isNaN(start.getTime()) || isNaN(end.getTime())) continue;
      
      const startHour = start.getHours();
      const endHour = end.getHours() + (end.getMinutes() > 0 ? 1 : 0);
      
      minHour = Math.min(minHour, startHour);
      maxHour = Math.max(maxHour, endHour);
    }
    
    if (minHour > maxHour) {
      minHour = 8;
      maxHour = 22;
    }
    
    const times = [];
    for (let h = minHour; h < maxHour; h++) {
      for (let m = 0; m < 60; m += TIME_INCREMENT) {
        const hh = String(h).padStart(2, '0');
        const mm = String(m).padStart(2, '0');
        times.push(`${hh}:${mm}`);
      }
    }
    return times;
  });
  
  // Inicializace
  watch([() => props.slots, () => props.userAvailabilities], () => {
    buildSlotMap();
    buildAvailability();
  }, { immediate: true });
  
  function buildSlotMap() {
    slotMap.clear();
    for (const slot of props.slots) {
      const start = parseISO(slot.slot_from);
      const end = parseISO(slot.slot_to);
      if (isNaN(start.getTime())||isNaN(end.getTime())) continue;
      const day = format(start, 'yyyy-MM-dd');
      const mapRow = slotMap.get(day) ?? new Map<string, number>();
      slotMap.set(day, mapRow);
      let cur = start;
      while (cur < end) {
        mapRow.set(format(cur, 'HH:mm'), slot.id);
        cur = addMinutes(cur, TIME_INCREMENT);
      }
    }
  }
  
  function buildAvailability() {
    availabilityMap.clear();
    userAvailabilityMap.clear();
    for (const avail of props.userAvailabilities) {
      const start = parseISO(avail.available_from);
      const end = parseISO(avail.available_to);
      if (isNaN(start.getTime())||isNaN(end.getTime())) continue;
      const day = format(start,'yyyy-MM-dd');
      const rowAll = availabilityMap.get(day) ?? new Map();
      const rowUser = userAvailabilityMap.get(day) ?? new Map();
      availabilityMap.set(day,rowAll);
      userAvailabilityMap.set(day,rowUser);
      let cur = start;
      while (cur < end) {
        const t = format(cur,'HH:mm');
        const slotId = avail.slot_id;
        const slotMapTimes = rowAll.get(t) ?? new Map<number,UserSimple[]>();
        if (!rowAll.has(t)) rowAll.set(t, slotMapTimes);
        const users = slotMapTimes.get(slotId) ?? [];
        if (!slotMapTimes.has(slotId)) slotMapTimes.set(slotId, users);
        if (!users.some((u: UserSimple) => u.id === avail.user.id)) users.push(avail.user);
        if (avail.user_id===props.currentUserId) {
          const userSet = rowUser.get(t) ?? new Set<number>();
          if (!rowUser.has(t)) rowUser.set(t,userSet);
          userSet.add(slotId);
        }
        cur = addMinutes(cur, TIME_INCREMENT);
      }
    }
  }
  
  // Stav buňky
  function isActiveCell(date: string, time: string) {
    return slotMap.has(date) && slotMap.get(date)!.has(time);
  }
  
  function getSlotId(date: string, time: string) {
    return isActiveCell(date, time) ? slotMap.get(date)!.get(time)! : null;
  }
  
  function isUserAvailable(date: string, time: string) {
    const sid = getSlotId(date, time);
    return sid !== null && userAvailabilityMap.get(date)?.get(time)?.has(sid) === true;
  }
  
  function getAvailableUsersCount(date: string, time: string) {
    const sid = getSlotId(date, time);
    return sid !== null ? availabilityMap.get(date)?.get(time)?.get(sid)?.length || 0 : 0;
  }
  
  function getTooltipText(date: string, time: string) {
    const sid = getSlotId(date, time);
    if (sid === null) return 'Mimo definovaný slot';
    const users = availabilityMap.get(date)?.get(time)?.get(sid) || [];
    return users.length ? `Dostupní: ${users.map(u => u.username).join(', ')}` : 'Nikdo není dostupný';
  }
  
  // Třída pro buňku
  function cellClass(date: string, time: string) {
    const classes = ['grid-cell'];
    if (isActiveCell(date, time)) classes.push('active-slot');
    else classes.push('inactive-cell');
    
    if (isUserAvailable(date, time)) classes.push('current-user-available');
    
    if (!props.isGm && isActiveCell(date, time)) {
      classes.push('interactive-cell');
    }
    
    // Zvýraznění výběru během tažení
    if (isDragging.value && selection.cells.has(`${date}-${time}`)) {
      classes.push(selection.isAdding ? 'selecting' : 'deselecting');
    }
      
    return classes;
  }
  
  // Zobrazení zprávy o úspěchu
  function showSuccessMessage(message: string) {
    successMessage.value = message;
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  }
  
  // Obsluha kliknutí pro jednoduchý výběr buňky
  function handleClick(date: string, time: string) {
    if (isDragging.value) return;
    if (!isActiveCell(date, time) || props.isGm || isProcessing.value) return;
    
    const sid = getSlotId(date, time);
    if (sid === null) return;
    
    const isAdding = !isUserAvailable(date, time);
    
    selection.cells.clear();
    selection.cells.add(`${date}-${time}`);
    selection.slotId = sid;
    selection.isAdding = isAdding;
    
    setUserAvailability(date, time, sid, isAdding);
  }
  
  // Logika nastavení dostupnosti uživatele
  async function setUserAvailability(date: string, time: string, slotId: number, isAdding: boolean) {
    isProcessing.value = true;
    error.value = '';
    
    try {
      // Ověření platnosti data
      if (!date || !time) {
        throw new Error('Neplatné datum nebo čas');
      }
      
      const year = parseInt(date.split('-')[0]);
      const month = parseInt(date.split('-')[1]) - 1;
      const day = parseInt(date.split('-')[2]);
      const hour = parseInt(time.split(':')[0]);
      const minute = parseInt(time.split(':')[1]);
      
      if (isNaN(year) || isNaN(month) || isNaN(day) || isNaN(hour) || isNaN(minute)) {
        throw new Error('Neplatný formát data nebo času');
      }
      
      const startDate = new Date(year, month, day, hour, minute);
      
      if (isNaN(startDate.getTime())) {
        throw new Error('Neplatné datum');
      }
      
      const endDate = new Date(startDate.getTime() + TIME_INCREMENT * 60 * 1000);
      
      if (isAdding) {
        await availabilityApi.setMyAvailability(
          props.sessionId, 
          slotId,
          {
            available_from: startDate.toISOString(),
            available_to: endDate.toISOString(),
            note: null
          }
        );
        showSuccessMessage('Dostupnost byla úspěšně uložena');
      } else {
        await availabilityApi.deleteMyAvailability(
          props.sessionId, 
          slotId, 
          startDate.toISOString(), 
          endDate.toISOString()
        );
        showSuccessMessage('Dostupnost byla úspěšně odstraněna');
      }
      
      emit('availability-changed');
    } catch (e: any) {
      console.error('Chyba při nastavování dostupnosti:', e);
      error.value = e.response?.data?.detail || e.message || 'Chyba při ukládání dostupnosti';
    } finally {
      isProcessing.value = false;
      reset();
    }
  }
  
  // Výběr drag & drop
  function handleMouseDown(date: string, time: string) {
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
    selection.isAdding = !isUserAvailable(date, time);
    document.addEventListener('mouseup', handleMouseUp, { once: true });
  }
  
  function handleMouseOver(date: string, time: string) {
    if (!isDragging.value || !selection.startCell) return;
    
    // Kontrola, zda jsme ve stejném slotu
    const currentSlotId = getSlotId(date, time);
    if (currentSlotId !== selection.slotId) return;
    
    // Aktualizace výběru
    updateSelection(selection.startCell, { date, time });
  }
  
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
    processSelection();
  }
  
  async function processSelection() {
    if (selection.cells.size === 0) return reset();
    
    isProcessing.value = true;
    error.value = '';
    
    try {
      // Vybraná data - organizovaná podle dnů
      const selectionByDay = new Map<string, string[]>();
      
      // Roztřídění podle data
      for (const cellKey of selection.cells) {
        const parts = cellKey.split('-');
        if (parts.length < 2) {
          console.error("Neplatný formát klíče buňky:", cellKey);
          continue;
        }
        
        // Rekonstrukce data a času (může být více pomlček v datu)
        const time = parts.pop()!; // Poslední část je čas
        const date = parts.join('-'); // Zbytek je datum
        
        if (!date || !time) {
          console.error("Nepodařilo se extrahovat datum a čas z klíče:", cellKey);
          continue;
        }
        
        if (!selectionByDay.has(date)) {
          selectionByDay.set(date, []);
        }
        selectionByDay.get(date)!.push(time);
      }
      
      // Zpracování pro každý den zvlášť
      for (const [date, times] of selectionByDay.entries()) {
        // Ověření formátu data
        if (date.split('-').length !== 3) {
          console.error("Neplatný formát data:", date);
          continue;
        }
        
        // Seřadíme časy pro konzistentní zpracování
        times.sort();
        
        // Vytvoříme půlhodinové intervaly z vybraných časů
        const intervals: { start: Date; end: Date }[] = [];
        let currentStart: Date | null = null;
        let currentEnd: Date | null = null;
        
        for (const time of times) {
          try {
            // Ověření formátu času
            if (time.split(':').length !== 2) {
              console.error("Neplatný formát času:", time);
              continue;
            }
            
            const year = parseInt(date.split('-')[0]);
            const month = parseInt(date.split('-')[1]) - 1;
            const day = parseInt(date.split('-')[2]);
            const hour = parseInt(time.split(':')[0]);
            const minute = parseInt(time.split(':')[1]);
            
            // Ověření platnosti složek data a času
            if (isNaN(year) || isNaN(month) || isNaN(day) || isNaN(hour) || isNaN(minute)) {
              console.error("Neplatné složky data a času:", { date, time, year, month, day, hour, minute });
              continue;
            }
            
            const timePoint = new Date(year, month, day, hour, minute);
            
            // Ověření platnosti data
            if (isNaN(timePoint.getTime())) {
              console.error("Invalid date created:", { date, time, year, month, day, hour, minute });
              continue;
            }
            
            const endPoint = new Date(timePoint.getTime() + TIME_INCREMENT * 60 * 1000);
            
            if (!currentStart) {
              // První interval
              currentStart = timePoint;
              currentEnd = endPoint;
            } else if (timePoint.getTime() === currentEnd!.getTime()) {
              // Navazující interval - rozšíříme existující
              currentEnd = new Date(timePoint.getTime() + TIME_INCREMENT * 60 * 1000);
            } else {
              // Nový nespojitý interval - uložíme předchozí a začneme nový
              intervals.push({ start: currentStart, end: currentEnd! });
              currentStart = timePoint;
              currentEnd = endPoint;
            }
          } catch (err) {
            console.error("Error processing time:", { date, time, error: err });
          }
        }
        
        // Přidáme poslední interval, pokud existuje
        if (currentStart && currentEnd) {
          intervals.push({ start: currentStart, end: currentEnd });
        }
        
        // Pro každý interval zpracujeme dle režimu (přidání/odebrání)
        for (const interval of intervals) {
          if (selection.isAdding) {
            // Přidání nového intervalu
            try {
              await availabilityApi.setMyAvailability(
                props.sessionId, 
                selection.slotId!,
                {
                  available_from: interval.start.toISOString(),
                  available_to: interval.end.toISOString(),
                  note: null
                }
              );
            } catch (e: any) {
              // Pokud dojde k chybě překryvu (409), ignorujeme ji a pokračujeme dál
              if (e.response?.status !== 409) {
                throw e; // Ostatní chyby přeposíláme dál
              }
            }
          } else {
            // Přímo použijeme novou funkci API pro mazání v časovém intervalu
            await availabilityApi.deleteMyAvailability(
              props.sessionId, 
              selection.slotId!,
              interval.start.toISOString(),
              interval.end.toISOString()
            );
          }
        }
      }
      
      // Aktualizujeme zobrazení
      showSuccessMessage(selection.isAdding ? 'Dostupnost byla úspěšně uložena' : 'Dostupnost byla úspěšně odstraněna');
      emit('availability-changed');
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Chyba při ukládání dostupnosti';
    } finally {
      isProcessing.value = false;
      reset();
    }
  }
  
  function updateSelection(from: {date: string; time: string}, to: {date: string; time: string}) {
    selection.cells.clear();
    const daysList = days.value.map(d => d.date);
    const timesList = timeSlots.value;
    
    const d0 = daysList.indexOf(from.date);
    const d1 = daysList.indexOf(to.date);
    const t0 = timesList.indexOf(from.time);
    const t1 = timesList.indexOf(to.time);
    
    // Kontrola platnosti indexů
    if (d0 === -1 || d1 === -1 || t0 === -1 || t1 === -1) {
      console.error("Invalid indices in selection:", { from, to, d0, d1, t0, t1 });
      return;
    }
    
    for (let d = Math.min(d0, d1); d <= Math.max(d0, d1); d++) {
      for (let t = Math.min(t0, t1); t <= Math.max(t0, t1); t++) {
        const dateStr = daysList[d];
        const timeStr = timesList[t];
        if (isActiveCell(dateStr, timeStr) && getSlotId(dateStr, timeStr) === selection.slotId) {
          selection.cells.add(`${dateStr}-${timeStr}`);
        }
      }
    }
  }
  
  function reset() {
    selection.startCell = null;
    selection.cells.clear();
    selection.slotId = null;
  }
  </script>
  
  <style scoped>
  .availability-grid-container { 
    overflow-x: auto; 
    width: 100%; 
    border: 1px solid rgba(0,0,0,0.1); 
    border-radius: 8px; 
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  }
  
  .availability-grid { 
    width:100%; 
    min-width:max-content; 
    border-collapse:collapse; 
    user-select:none; 
  }
  
  .availability-grid th, .availability-grid td { 
    border:1px solid rgba(0,0,0,0.1); 
    padding:8px; 
    text-align:center; 
    min-width: 80px;
    height: 40px;
  }
  
  .time-header {
    position: sticky;
    left: 0;
    background: #f8f8f8;
    z-index: 2;
    border-bottom: 2px solid rgba(0,0,0,0.2);
    font-weight: bold;
  }
  
  .day-header {
    border-bottom: 2px solid rgba(0,0,0,0.2);
    font-weight: bold;
  }
  
  .time-cell {
    position: sticky;
    left: 0;
    background: #f8f8f8;
    font-size: .85rem;
    font-weight: 500;
    z-index: 1;
    border-right: 2px solid rgba(0,0,0,0.2);
  }
  
  .inactive-cell {
    background: rgba(0,0,0,0.05);
    color: rgba(0,0,0,0.4);
  }
  
  .active-slot {
    background: #fff;
  }
  
  .interactive-cell {
    cursor: pointer;
    transition: background-color 0.15s ease;
  }
  
  .interactive-cell:hover {
    background: rgba(0,0,0,0.02);
  }
  
  .current-user-available {
    background: rgba(76,175,80,0.3);
  }
  
  .selecting {
    background: rgba(76,175,80,0.5) !important;
    box-shadow: inset 0 0 0 2px rgba(76,175,80,0.8);
    position: relative;
    z-index: 1;
  }
  
  .deselecting {
    background: rgba(244,67,54,0.2) !important;
    box-shadow: inset 0 0 0 2px rgba(244,67,54,0.5);
    position: relative;
    z-index: 1;
  }
  
  .text-error {
    color: rgb(var(--v-theme-error));
    font-size: .9rem;
  }
  
  .text-success {
    color: rgb(var(--v-theme-success));
    font-size: .9rem;
  }
  
  .user-count {
    display: inline-block;
    min-width: 24px;
    height: 24px;
    line-height: 24px;
    border-radius: 50%;
    background-color: rgba(0,0,0,0.1);
    color: rgba(0,0,0,0.7);
    font-weight: bold;
    font-size: 0.85rem;
  }
  
  /* Styly pro legendu */
  .legend-item {
    display: flex;
    align-items: center;
    margin-right: 10px;
    margin-bottom: 5px;
  }
  
  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    margin-right: 5px;
    display: inline-block;
  }
  
  .legend-text {
    font-size: 0.85rem;
    color: rgba(0,0,0,0.7);
  }
  </style>
  