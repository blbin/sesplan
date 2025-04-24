import { ref, watch, type Ref } from 'vue';
import { availabilityService } from '@/services/api/availabilityService';
import type { Availability, AvailabilityCreate } from '@/types/availability';

export function useMyAvailabilityApi(sessionId: Ref<number | undefined>) {

    const myAvailabilities = ref<Availability[]>([]);
    const isLoadingMine = ref(false);
    const loadErrorMine = ref<string | null>(null);
    const isSaving = ref(false);
    const saveError = ref<string | null>(null);

    async function fetchMyAvailability() {
        if (!sessionId.value) return;
        isLoadingMine.value = true;
        loadErrorMine.value = null;
        try {
            myAvailabilities.value = await availabilityService.getMyAvailability(sessionId.value);
        } catch (err: any) {
            loadErrorMine.value = err.message || 'Failed to fetch my availability';
            console.error("Fetch My Availability Error:", err);
            myAvailabilities.value = []; // Reset on error
        } finally {
            isLoadingMine.value = false;
        }
    }

    async function saveMyAvailability(blocks: AvailabilityCreate[]): Promise<boolean> {
        if (!sessionId.value) return false;
        
        isSaving.value = true;
        saveError.value = null;
        try {
            const updatedList = await availabilityService.setMyAvailability(sessionId.value, blocks);
            myAvailabilities.value = updatedList;
            return true; // Indicate success
        } catch (err: any) {
            saveError.value = err.message || 'Failed to save availability';
            console.error("Save Availability Error:", err);
            return false; // Indicate failure
        } finally {
            isSaving.value = false;
        }
    }

    async function clearMyAvailabilityOnServer(): Promise<boolean> {
        if (!sessionId.value) return false;
        // Only call delete if there seems to be something to delete based on local state
        // The API should handle the case where nothing exists anyway.
        // if (myAvailabilities.value.length === 0) {
        //     return true; // Nothing to clear server-side
        // }

        isSaving.value = true; // Use saving indicator for delete as well
        saveError.value = null;
        try {
            await availabilityService.deleteMyAvailability(sessionId.value);
            myAvailabilities.value = []; // Clear local state on successful deletion
            return true; // Indicate success
        } catch (err: any) {
            saveError.value = err.message || 'Failed to delete availability';
            console.error("Delete Availability Error:", err);
             // Don't clear local state if delete failed
            return false; // Indicate failure
        } finally {
            isSaving.value = false;
        }
    }

    // Watch for sessionId changes to refetch
    watch(sessionId, (newSessionId) => {
        if (newSessionId) {
            fetchMyAvailability();
        } else {
            // Clear data if session ID becomes invalid
            myAvailabilities.value = [];
            loadErrorMine.value = null;
            saveError.value = null;
        }
    }, { immediate: true }); // Fetch immediately on mount

    return {
        myAvailabilities,
        isLoadingMine,
        loadErrorMine,
        isSaving,
        saveError,
        fetchMyAvailability,
        saveMyAvailability,
        clearMyAvailabilityOnServer
    };
} 