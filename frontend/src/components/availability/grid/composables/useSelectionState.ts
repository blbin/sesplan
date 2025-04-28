import { ref, computed, shallowReactive } from 'vue';
import { format, parseISO } from 'date-fns';

export interface SelectionCell {
  date: string;
  time: string;
}

export function useSelectionState() {
  // Stav tažení
  const isDragging = ref(false);
  
  // Výběr při tažení
  const selection = shallowReactive({
    startCell: null as SelectionCell | null,
    endCell: null as SelectionCell | null,
    cells: new Set<string>(),
    slotId: null as number | null,
    isAdding: true,
  });

  // Resetování stavu výběru
  function reset() {
    selection.startCell = null;
    selection.endCell = null;
    selection.cells.clear();
    selection.slotId = null;
  }

  // Formátování rozsahu výběru pro zobrazení uživateli
  const formattedSelectionRange = computed(() => {
    if (selection.cells.size === 0 || !selection.startCell) return '';
    
    // Získání všech dat a časů z výběru
    const dateTimeMap = new Map<string, string[]>();
    for (const cellKey of selection.cells) {
      const parts = cellKey.split('-');
      if (parts.length < 2) continue;
      
      const time = parts.pop()!;
      const date = parts.join('-');
      
      if (!dateTimeMap.has(date)) {
        dateTimeMap.set(date, []);
      }
      dateTimeMap.get(date)!.push(time);
    }
    
    // Pokud je jen jedno datum, zobrazím rozsah časů
    if (dateTimeMap.size === 1) {
      const date = Array.from(dateTimeMap.keys())[0];
      const times = dateTimeMap.get(date)!.sort();
      const firstTime = times[0];
      const lastTime = times[times.length - 1];
      
      // Pokud je to jen jeden časový slot
      if (times.length === 1) {
        // Formátování data a času
        try {
          const dt = parseISO(`${date}T${firstTime}`);
          return `${format(dt, 'd.M.')} ${firstTime}`;
        } catch (e) {
          return `${date} ${firstTime}`;
        }
      }
      
      // Více časových slotů v jednom dni
      try {
        const dt = parseISO(`${date}T${firstTime}`);
        return `${format(dt, 'd.M.')} ${firstTime}-${lastTime} (${times.length} slotů)`;
      } catch (e) {
        return `${date} ${firstTime}-${lastTime}`;
      }
    }
    
    // Více dnů
    const dates = Array.from(dateTimeMap.keys()).sort();
    const totalSlots = Array.from(dateTimeMap.values()).reduce((acc, times) => acc + times.length, 0);
    
    try {
      const firstDate = parseISO(dates[0]);
      const lastDate = parseISO(dates[dates.length - 1]);
      return `${format(firstDate, 'd.M.')}-${format(lastDate, 'd.M.')} (${totalSlots} slotů)`;
    } catch (e) {
      return `${dates[0]}-${dates[dates.length - 1]} (${totalSlots} slotů)`;
    }
  });

  // Aktualizace výběru při tažení
  function updateSelection(from: SelectionCell, to: SelectionCell, daysList: string[], timesList: string[], isActiveCellFn: (date: string, time: string) => boolean, getSlotIdFn: (date: string, time: string) => number | null) {
    // Nejprve vyčistíme výběr (ale uložíme původní klíče pro kontrolu změn)
    const originalKeys = [...selection.cells];
    selection.cells.clear();
    
    const d0 = daysList.indexOf(from.date);
    const d1 = daysList.indexOf(to.date);
    const t0 = timesList.indexOf(from.time);
    const t1 = timesList.indexOf(to.time);
    
    // Kontrola platnosti indexů
    if (d0 === -1 || d1 === -1 || t0 === -1 || t1 === -1) {
      console.error("Invalid indices in selection:", { from, to, d0, d1, t0, t1 });
      return;
    }
    
    // Uložím poslední políčko výběru
    selection.endCell = to;
    
    // Vytvoření výběru
    const newKeys = new Set<string>();
    for (let d = Math.min(d0, d1); d <= Math.max(d0, d1); d++) {
      for (let t = Math.min(t0, t1); t <= Math.max(t0, t1); t++) {
        const dateStr = daysList[d];
        const timeStr = timesList[t];
        if (isActiveCellFn(dateStr, timeStr) && getSlotIdFn(dateStr, timeStr) === selection.slotId) {
          const key = `${dateStr}-${timeStr}`;
          selection.cells.add(key);
          newKeys.add(key);
        }
      }
    }
    
    // Detekce změn ve výběru pro vyvolání reaktivity
    let hasChanged = originalKeys.length !== newKeys.size;
    if (!hasChanged) {
      for (const key of originalKeys) {
        if (!newKeys.has(key)) {
          hasChanged = true;
          break;
        }
      }
    }
    
    // Pokud se výběr změnil, logujeme změnu pro snazší debugování
    if (hasChanged) {
      console.debug(`Výběr aktualizován: ${newKeys.size} buněk`);
    }
  }

  // Klasifikace buňky z hlediska výběru
  function getSelectionClassification(date: string, time: string) {
    // Pokud se netáhne, nebo buňka není v selekci, vrátíme null
    if (!isDragging.value) {
      return null;
    }
    
    const cellKey = `${date}-${time}`;
    const isInSelection = selection.cells.has(cellKey);
    
    // Pokud buňka není v selekci, ale máme startCell a endCell, 
    // zkontrolujeme, zda není na cestě mezi nimi (pro lepší vizuální odezvu)
    if (!isInSelection && selection.startCell && selection.endCell) {
      return null;
    }
    
    if (!isInSelection) {
      return null;
    }

    // Typy výběru
    const result = {
      isInSelection: true,
      isSelectionStart: false,
      isSelectionEnd: false,
      isAdding: selection.isAdding
    };

    // Detekce prvního a posledního políčka ve výběru
    if (selection.startCell && selection.startCell.date === date && selection.startCell.time === time) {
      result.isSelectionStart = true;
    }
    
    if (selection.endCell && selection.endCell.date === date && selection.endCell.time === time) {
      result.isSelectionEnd = true;
    }

    return result;
  }

  return {
    isDragging,
    selection,
    reset,
    formattedSelectionRange,
    updateSelection,
    getSelectionClassification
  };
} 