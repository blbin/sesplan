import { computed, shallowReactive } from 'vue';
import { format, parseISO, addMinutes } from 'date-fns';
import type { SessionSlot } from '@/types/session_slot';
import type { UserAvailability } from '@/types/user_availability';
import type { UserSimple } from '@/types/user';

// Definice typů pro mapy
export type SlotMap = Map<string, Map<string, number>>;
export type AvailabilityMap = Map<string, Map<string, Map<number, UserSimple[]>>>;
export type UserAvailabilityMap = Map<string, Map<string, Set<number>>>;

// Konstanta pro časový interval 30 minut
export const TIME_INCREMENT = 30;

export function useGridData(props: {
  slots: SessionSlot[],
  userAvailabilities: UserAvailability[]
}) {
  // Mapy: reaktivní sledování pouze první úrovně
  const slotMap = shallowReactive<SlotMap>(new Map());
  const availabilityMap = shallowReactive<AvailabilityMap>(new Map());
  const userAvailabilityMap = shallowReactive<UserAvailabilityMap>(new Map());

  // Výpočet dnů na základě slotů
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
  
  // Výpočet časových slotů
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

  // Vytvoření mapy dostupných slotů
  function buildSlotMap() {
    slotMap.clear();
    for (const slot of props.slots) {
      const start = parseISO(slot.slot_from);
      const end = parseISO(slot.slot_to);
      if (isNaN(start.getTime()) || isNaN(end.getTime())) continue;
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
  
  // Vytvoření mapy dostupností uživatelů
  function buildAvailability(currentUserId: number) {
    availabilityMap.clear();
    userAvailabilityMap.clear();
    for (const avail of props.userAvailabilities) {
      const start = parseISO(avail.available_from);
      const end = parseISO(avail.available_to);
      if (isNaN(start.getTime()) || isNaN(end.getTime())) continue;
      const day = format(start, 'yyyy-MM-dd');
      const rowAll = availabilityMap.get(day) ?? new Map();
      const rowUser = userAvailabilityMap.get(day) ?? new Map();
      availabilityMap.set(day, rowAll);
      userAvailabilityMap.set(day, rowUser);
      let cur = start;
      while (cur < end) {
        const t = format(cur, 'HH:mm');
        const slotId = avail.slot_id;
        const slotMapTimes = rowAll.get(t) ?? new Map<number, UserSimple[]>();
        if (!rowAll.has(t)) rowAll.set(t, slotMapTimes);
        const users = slotMapTimes.get(slotId) ?? [];
        if (!slotMapTimes.has(slotId)) slotMapTimes.set(slotId, users);
        if (!users.some((u: UserSimple) => u.id === avail.user.id)) users.push(avail.user);
        if (avail.user_id === currentUserId) {
          const userSet = rowUser.get(t) ?? new Set<number>();
          if (!rowUser.has(t)) rowUser.set(t, userSet);
          userSet.add(slotId);
        }
        cur = addMinutes(cur, TIME_INCREMENT);
      }
    }
    
    // Přidání logování pro ověření, že currentUserId je použito
    console.debug(`Dostupnosti pro uživatele ${currentUserId} byly načteny.`);
  }

  // Kontrola, zda je buňka aktivní (součást nějakého časového slotu)
  function isActiveCell(date: string, time: string) {
    return slotMap.has(date) && slotMap.get(date)!.has(time);
  }
  
  // Získání ID slotu pro danou buňku
  function getSlotId(date: string, time: string) {
    return isActiveCell(date, time) ? slotMap.get(date)!.get(time)! : null;
  }
  
  // Kontrola, zda je uživatel k dispozici v daném čase
  function isUserAvailable(date: string, time: string, currentUserId: number) {
    // Explicitní použití parametru
    if (currentUserId <= 0) {
      console.warn(`Neplatné currentUserId: ${currentUserId}`);
      return false;
    }
    
    const sid = getSlotId(date, time);
    return sid !== null && userAvailabilityMap.get(date)?.get(time)?.has(sid) === true;
  }
  
  // Počet uživatelů dostupných v daném čase
  function getAvailableUsersCount(date: string, time: string) {
    const sid = getSlotId(date, time);
    return sid !== null ? availabilityMap.get(date)?.get(time)?.get(sid)?.length || 0 : 0;
  }
  
  // Text popisku pro buňku
  function getTooltipText(date: string, time: string) {
    const sid = getSlotId(date, time);
    if (sid === null) return 'Mimo definovaný slot';
    const users = availabilityMap.get(date)?.get(time)?.get(sid) || [];
    return users.length ? `Dostupní: ${users.map(u => u.username).join(', ')}` : 'Nikdo není dostupný';
  }

  // Inicializace dat při změně propů
  function initializeData(currentUserId: number) {
    buildSlotMap();
    buildAvailability(currentUserId);
    
    // Explicitní použití parametru, aby TypeScript nehlásil chybu
    const userIdMsg = `Inicializace pro uživatele ID: ${currentUserId}`;
    console.debug(userIdMsg);
  }

  return {
    slotMap,
    availabilityMap,
    userAvailabilityMap,
    days,
    timeSlots,
    initializeData,
    isActiveCell,
    getSlotId,
    isUserAvailable,
    getAvailableUsersCount,
    getTooltipText
  };
} 