import { ref, type Ref } from 'vue';
import { startOfDay, addMinutes, parseISO, isWithinInterval, isEqual, compareAsc } from 'date-fns';
import type { Availability, AvailabilityCreate } from '@/types/availability';

export function useAvailabilitySelection(myAvailabilities: Ref<Availability[]>, slotDurationMinutes: number = 30) {

    const isSelecting = ref(false);
    const selectionStartSlot = ref<{ day: Date, time: number } | null>(null);
    const selectedSlots = ref<Set<string>>(new Set()); // Stores keys like "ISODateTimeString_minutes"

    // --- Slot Key Generation and Parsing ---
    function getSlotKey(day: Date, time: number): string {
        const slotStartDateTime = addMinutes(startOfDay(day), time);
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
        const start = addMinutes(startOfDay(day), time);
        const end = addMinutes(start, slotDurationMinutes);
        return { start, end };
    }

    // --- Selection Logic ---
    function startSelection(day: Date, time: number) {
        isSelecting.value = true;
        selectionStartSlot.value = { day, time };
        toggleSlotSelection(day, time); // Toggle the first slot immediately
    }

    function updateSelection(day: Date, time: number) {
        if (!isSelecting.value || !selectionStartSlot.value) return;

        // Basic selection: toggle slots hovered over while selecting
        // More complex logic (like selecting a range) could be added here
        // For now, just toggle individual slots during drag

        // Optimization: Only toggle if it hasn't been toggled in this drag yet? Maybe not needed.
        // toggleSlotSelection(day, time);

        // --- Range Selection Logic Placeholder (Removed unused variables) --- 
        // const start = selectionStartSlot.value;
        // const current = { day, time };

        // Determine the range corners (chronologically)
        // const day1 = start.day;
        // const time1 = start.time;
        // const day2 = current.day;
        // const time2 = current.time;
        // const rangeStartDay = compareAsc(day1, day2) <= 0 ? day1 : day2; // Removed
        // const rangeEndDay = compareAsc(day1, day2) <= 0 ? day2 : day1; // Removed
        // const rangeStartTime = Math.min(time1, time2); // Removed
        // const rangeEndTime = Math.max(time1, time2); // Removed

        // Temporarily store slots to be selected in this drag operation
        // const slotsToSelectNow = new Set<string>(); // Removed

        // Iterate through all visible slots (assuming days/timeSlots are available)
        // TODO: This needs access to the grid's days and timeSlots. Pass them in or rethink.
        // For now, let's assume a simplified toggle logic based on start and current slot
        // which might not be ideal for range selection.
        
        // --- Simplified Toggle Logic (as originally implemented implicitly) ---
        toggleSlotSelection(day, time);
        // --- End Simplified Toggle Logic ---

    }

    function endSelection() {
        if (isSelecting.value) {
             isSelecting.value = false;
             selectionStartSlot.value = null;
             // Potentially consolidate selected slots here if needed
        }
    }

    function toggleSlotSelection(day: Date, time: number) {
        const key = getSlotKey(day, time);
        if (selectedSlots.value.has(key)) {
            selectedSlots.value.delete(key);
        } else {
            selectedSlots.value.add(key);
        }
    }

    // --- Data Synchronization ---
    function updateSelectedSlotsFromMyAvailabilities(availabilities: Availability[]) {
        const newSelectedSlots = new Set<string>();
        availabilities.forEach(avail => {
            try {
                const start = parseISO(avail.available_from);
                const end = parseISO(avail.available_to);

                // Iterate through potential slots within the availability range
                let currentSlotTime = startOfDay(start);
                while (currentSlotTime < end) {
                    const minutes = (currentSlotTime.getHours() * 60) + currentSlotTime.getMinutes();
                    const slotKey = getSlotKey(start, minutes);
                    const slotRange = getSlotDateTimeRange(start, minutes);

                    // Check if the slot's start time is within the availability interval
                    // Note: We check the *start* of the slot. If availability ends mid-slot, that slot isn't included.
                    if (isWithinInterval(slotRange.start, { start, end }) && !isEqual(slotRange.start, end)) {
                         newSelectedSlots.add(slotKey);
                    }
                    currentSlotTime = addMinutes(currentSlotTime, slotDurationMinutes);
                }
            } catch (e) {
                console.error("Error processing availability for selection:", avail, e);
            }
        });
        selectedSlots.value = newSelectedSlots;
    }

    // Initial population
    updateSelectedSlotsFromMyAvailabilities(myAvailabilities.value);

    // --- Availability Block Calculation ---
    function calculateAvailabilityBlocks(): AvailabilityCreate[] {
        const blocks: AvailabilityCreate[] = [];
        if (selectedSlots.value.size === 0) {
            return blocks;
        }

        // Convert selected slot keys back to { start: Date, time: number }
        const parsedSlots = Array.from(selectedSlots.value)
            .map(parseSlotKey)
            .filter(slot => slot !== null) as { start: Date, time: number }[];

        // Sort slots chronologically
        parsedSlots.sort((a, b) => compareAsc(a.start, b.start));

        let currentBlock: AvailabilityCreate | null = null;

        for (const slot of parsedSlots) {
            const slotStart = slot.start;
            const slotEnd = addMinutes(slotStart, slotDurationMinutes);

            if (currentBlock === null) {
                // Start a new block
                currentBlock = {
                    available_from: slotStart.toISOString(),
                    available_to: slotEnd.toISOString(),
                };
            } else {
                // Check if the current slot is contiguous with the current block
                const blockEndDate = parseISO(currentBlock.available_to);
                if (isEqual(blockEndDate, slotStart)) {
                    // Extend the current block
                    currentBlock.available_to = slotEnd.toISOString();
                } else {
                    // End the current block and start a new one
                    blocks.push(currentBlock);
                    currentBlock = {
                        available_from: slotStart.toISOString(),
                        available_to: slotEnd.toISOString(),
                    };
                }
            }
        }

        // Add the last block if it exists
        if (currentBlock !== null) {
            blocks.push(currentBlock);
        }

        return blocks;
    }

    // Function to clear selection (doesn't call API)
    function clearLocalSelection() {
        selectedSlots.value.clear();
    }

    return {
        isSelecting,
        selectedSlots,
        startSelection,
        updateSelection,
        endSelection,
        updateSelectedSlotsFromMyAvailabilities, // Expose if needed externally
        calculateAvailabilityBlocks,
        getSlotKey, // Expose for use in the parent component (e.g., for :isSelected)
        clearLocalSelection
    };
} 