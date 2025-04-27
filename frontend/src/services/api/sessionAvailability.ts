import { api } from '../auth.service';
import type { SessionSlot, SessionSlotCreate, SessionSlotUpdate } from '@/types/session_slot';
import type { UserAvailability, UserAvailabilityCreateUpdate } from '@/types/user_availability';

const BASE_URL = '/V1/sessions';

// --- Session Slot Endpoints --- 

/**
 * Create a new availability slot for a session.
 */
export const createSlot = async (sessionId: number, slotData: SessionSlotCreate): Promise<SessionSlot> => {
    const response = await api.post<SessionSlot>(`${BASE_URL}/${sessionId}/slots`, slotData);
    return response.data;
};

/**
 * Get all availability slots for a specific session.
 */
export const getSlots = async (sessionId: number, skip: number = 0, limit: number = 100): Promise<SessionSlot[]> => {
    const response = await api.get<SessionSlot[]>(`${BASE_URL}/${sessionId}/slots`, {
        params: { skip, limit },
    });
    return response.data;
};

/**
 * Update an existing availability slot.
 */
export const updateSlot = async (sessionId: number, slotId: number, slotData: SessionSlotUpdate): Promise<SessionSlot> => {
    const response = await api.put<SessionSlot>(`${BASE_URL}/${sessionId}/slots/${slotId}`, slotData);
    return response.data;
};

/**
 * Delete an availability slot.
 */
export const deleteSlot = async (sessionId: number, slotId: number): Promise<SessionSlot> => {
    const response = await api.delete<SessionSlot>(`${BASE_URL}/${sessionId}/slots/${slotId}`);
    return response.data; // Return the deleted slot data
};

// --- User Availability Endpoints --- 

/**
 * Set or update the current user's availability for a specific slot.
 */
export const setMyAvailability = async (
    sessionId: number, 
    slotId: number, 
    availabilityData: UserAvailabilityCreateUpdate
): Promise<UserAvailability> => {
    const response = await api.put<UserAvailability>(
        `${BASE_URL}/${sessionId}/slots/${slotId}/availabilities/me`, 
        availabilityData
    );
    return response.data;
};

/**
 * Delete the current user's availability for a specific slot.
 */
export const deleteMyAvailability = async (sessionId: number, slotId: number): Promise<void> => {
    await api.delete(`${BASE_URL}/${sessionId}/slots/${slotId}/availabilities/me`);
    // No content returned on success (204)
};

/**
 * Get all user availabilities for a specific slot.
 */
export const getSlotAvailabilities = async (
    sessionId: number, 
    slotId: number, 
    skip: number = 0, 
    limit: number = 100
): Promise<UserAvailability[]> => {
    const response = await api.get<UserAvailability[]>(
        `${BASE_URL}/${sessionId}/slots/${slotId}/availabilities`, 
        { params: { skip, limit } }
    );
    return response.data;
};

/**
 * Get all user availabilities across all slots for a specific session.
 */
export const getAllSessionAvailabilities = async (sessionId: number): Promise<UserAvailability[]> => {
    const response = await api.get<UserAvailability[]>(`${BASE_URL}/${sessionId}/availabilities`);
    return response.data;
}; 