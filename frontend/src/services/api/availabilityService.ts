import { api } from '../auth.service'; // Correct import from auth service
import type { Availability, AvailabilityCreate } from '@/types/availability';

const BASE_URL = '/V1/sessions'; // Base URL includes API version prefix now

export const availabilityService = {
  /**
   * Get all availabilities for a specific session.
   * GET /V1/sessions/{session_id}/availabilities/
   */
  async getAvailabilities(sessionId: number): Promise<Availability[]> {
    const response = await api.get<Availability[]>(`${BASE_URL}/${sessionId}/availabilities/`);
    return response.data;
  },

  /**
   * Get the current user's availability for a specific session.
   * GET /V1/sessions/{session_id}/availabilities/me
   */
  async getMyAvailability(sessionId: number): Promise<Availability[]> {
    const response = await api.get<Availability[]>(`${BASE_URL}/${sessionId}/availabilities/me`);
    return response.data;
  },

  /**
   * Set (Create or Replace) the current user's availability for a specific session.
   * PUT /V1/sessions/{session_id}/availabilities/me
   */
  async setMyAvailability(sessionId: number, data: AvailabilityCreate[]): Promise<Availability[]> {
    const response = await api.put<Availability[]>(`${BASE_URL}/${sessionId}/availabilities/me`, data);
    return response.data;
  },

  /**
   * Delete all of the current user's availability records for a specific session.
   * DELETE /V1/sessions/{session_id}/availabilities/me
   */
  async deleteMyAvailability(sessionId: number): Promise<void> {
    await api.delete(`${BASE_URL}/${sessionId}/availabilities/me`);
    // No return needed for void
  },
}; 