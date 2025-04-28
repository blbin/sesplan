import { ref } from 'vue';
import * as availabilityApi from '@/services/api/sessionAvailability';
import { TIME_INCREMENT } from './useGridData';

export function useAvailabilityActions() {
  const error = ref('');
  const successMessage = ref('');
  const isProcessing = ref(false);

  // Zobrazení zprávy o úspěchu
  function showSuccessMessage(message: string) {
    successMessage.value = message;
    setTimeout(() => {
      successMessage.value = '';
    }, 3000);
  }

  // Zpracování jednoduchého výběru jedné buňky
  async function setUserAvailability(date: string, time: string, slotId: number, isAdding: boolean, sessionId: number) {
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
          sessionId, 
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
          sessionId, 
          slotId, 
          startDate.toISOString(), 
          endDate.toISOString()
        );
        showSuccessMessage('Dostupnost byla úspěšně odstraněna');
      }
      
      return true;
    } catch (e: any) {
      console.error('Chyba při nastavování dostupnosti:', e);
      error.value = e.response?.data?.detail || e.message || 'Chyba při ukládání dostupnosti';
      return false;
    } finally {
      isProcessing.value = false;
    }
  }

  // Zpracování výběru více buněk
  async function processSelection(selection: Set<string>, isAdding: boolean, slotId: number, sessionId: number) {
    if (selection.size === 0) return false;
    
    isProcessing.value = true;
    error.value = '';
    
    try {
      // Vybraná data - organizovaná podle dnů
      const selectionByDay = new Map<string, string[]>();
      
      // Roztřídění podle data
      for (const cellKey of selection) {
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
          if (isAdding) {
            // Přidání nového intervalu
            try {
              await availabilityApi.setMyAvailability(
                sessionId, 
                slotId,
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
              sessionId, 
              slotId,
              interval.start.toISOString(),
              interval.end.toISOString()
            );
          }
        }
      }
      
      // Aktualizujeme zobrazení
      showSuccessMessage(isAdding ? 'Dostupnost byla úspěšně uložena' : 'Dostupnost byla úspěšně odstraněna');
      return true;
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message || 'Chyba při ukládání dostupnosti';
      return false;
    } finally {
      isProcessing.value = false;
    }
  }

  return {
    error,
    successMessage,
    isProcessing,
    showSuccessMessage,
    setUserAvailability,
    processSelection
  };
} 