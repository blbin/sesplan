<template>
    <v-card variant="tonal">
      <v-card-text>
        <v-alert v-if="!isGm" type="info" density="compact" class="mb-4">
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
                >
                  <div class="cell-content">
                    {{ getAvailableUsersCount(day.date, time) || '' }}
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
  
        <div v-if="error" class="text-error mt-3">{{ error }}</div>
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
    const times = [];
    for (let h = 0; h < 24; h++) {
      for (let m = 0; m < 60; m += TIME_INCREMENT) { // Generování přímo HH:mm
        const hh = String(h).padStart(2, '0');
        const mm = String(m).padStart(2, '0');
        times.push(`${hh}:${mm}`);
      }
    }
    return times;
  });
  
  // Inicializace při změně props
  dependency: watch([() => props.slots, () => props.userAvailabilities], () => {
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
  function isActiveCell(date:string,time:string) {
    return slotMap.has(date)&& slotMap.get(date)!.has(time);
  }
  function getSlotId(date:string,time:string) {
    return isActiveCell(date,time)?slotMap.get(date)!.get(time)!:null;
  }
  function isUserAvailable(date:string,time:string) {
    const sid = getSlotId(date,time);
    return sid!==null && userAvailabilityMap.get(date)?.get(time)?.has(sid)===true;
  }
  function getAvailableUsersCount(date:string,time:string){
    const sid=getSlotId(date,time);
    return sid!==null?availabilityMap.get(date)?.get(time)?.get(sid)?.length||0:0;
  }
  function getTooltipText(date:string,time:string){
    const sid=getSlotId(date,time);
    if(sid===null) return 'Mimo definovaný slot';
    const users=availabilityMap.get(date)?.get(time)?.get(sid)||[];
    return users.length?`Dostupní: ${users.map(u=>u.username).join(', ')}`:'Nikdo není dostupný';
  }
  
  // Třída pro buňku
  function cellClass(date:string,time:string){
    const classes = ['grid-cell'];
    if(isActiveCell(date,time)) classes.push('active-slot');
    if(isUserAvailable(date,time)) classes.push('current-user-available');
    if(isDragging.value&&selection.cells.has(`${date}-${time}`))
      classes.push(selection.isAdding?'selecting':'deselecting');
    return classes;
  }
  
  // Výběr drag & drop
  function handleMouseDown(date:string,time:string){
    if(!isActiveCell(date,time)||props.isGm||isProcessing.value) return;
    isDragging.value=true;
    const key=`${date}-${time}`;
    const sid=getSlotId(date,time);
    selection.startCell={date,time};
    selection.cells.clear();
    selection.cells.add(key);
    selection.slotId=sid;
    selection.isAdding=!isUserAvailable(date,time);
    document.addEventListener('mouseup',handleMouseUp,{once:true});
  }
  function handleMouseOver(date:string,time:string){
    if(!isDragging.value||!selection.startCell) return;
    if(getSlotId(date,time)!==selection.slotId) return;
    updateSelection(selection.startCell,{date,time});
  }
  async function handleMouseUp(){
    isDragging.value=false;
    if(!selection.startCell||!selection.slotId) return reset();
    let start:Date| null=null, end:Date|null=null;
    for(const k of selection.cells){
      const [d,t]=k.split('-').slice(0,2);
      const dt=parseToUTCDate(d,t);
      if(isNaN(dt.getTime())) continue;
      if(!start||dt<start) start=dt;
      const dtEnd=addMinutes(dt,TIME_INCREMENT);
      if(!end||dtEnd>end) end=dtEnd;
    }
    if(!start||!end) return reset();
    isProcessing.value=true; error.value='';
    try{
      if(selection.isAdding){
        await availabilityApi.setMyAvailability(
          props.sessionId, selection.slotId,
          {available_from:start.toISOString(),available_to:end.toISOString(),note:null}
        );
      } else {
        await availabilityApi.deleteMyAvailability(props.sessionId,selection.slotId!);
      }
      emit('availability-changed');
    } catch(e:any){ error.value=e.response?.data?.detail||e.message||'Chyba'; console.error(e); }
    finally{ isProcessing.value=false; reset(); }
  }
  function updateSelection(from:{date:string;time:string},to:{date:string;time:string}){
    selection.cells.clear();
    const daysList=days.value.map(d=>d.date);
    const timesList=timeSlots.value;
    const d0=daysList.indexOf(from.date), d1=daysList.indexOf(to.date);
    const t0=timesList.indexOf(from.time), t1=timesList.indexOf(to.time);
    for(const d of range(Math.min(d0,d1),Math.max(d0,d1))) for(const t of range(Math.min(t0,t1),Math.max(t0,t1))) {
      const dateStr = daysList[d];
      const timeStr = timesList[t];
      if (isActiveCell(dateStr, timeStr)) {
        selection.cells.add(`${dateStr}-${timeStr}`);
      }
    }
  }
  function range(a:number,b:number){ const arr=[]; for(let i=a;i<=b;i++)arr.push(i); return arr; }
  function reset(){ selection.startCell=null; selection.cells.clear(); selection.slotId=null; }
  function parseToUTCDate(d:string,t:string){
    const [y,mo,da]=d.split('-').map(Number);
    const [h,mi]=t.split(':').map(Number);
    return new Date(Date.UTC(y,mo-1,da,h,mi));
  }
  </script>
  
  <style scoped>
  /* Zůstaly stejné styly jako dříve */
  .availability-grid-container { overflow-x: auto; width: 100%; border: 1px solid rgba(0,0,0,0.1); border-radius: 4px; }
  .availability-grid { width:100%; min-width:max-content; border-collapse:collapse; user-select:none; }
  .availability-grid th, .availability-grid td { border:1px solid rgba(0,0,0,0.1); padding:8px; text-align:center; }
  .time-header{position:sticky;left:0;}
  .time-cell{position:sticky;left:0;background:rgba(0,0,0,0.02);font-size:.85rem;font-weight:500;}
  .active-slot{cursor:pointer;background:#fff;} .current-user-available{background:rgba(76,175,80,0.3);} .selecting{background:rgba(76,175,80,0.5)!important;} .deselecting{background:rgba(244,67,54,0.2)!important;}
  .text-error{color:rgb(var(--v-theme-error));font-size:.9rem;}
  </style>
  