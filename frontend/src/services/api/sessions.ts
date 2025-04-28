import { api } from '../auth.service';
import type { Session, SessionCreate, SessionUpdate } from '../../types/session';

const BASE_URL = '/V1/sessions';
// CAMPAIGN_BASE_URL is removed as it was unused

// Get all sessions for a specific campaign
export const getSessionsByCampaign = async (campaignId: number): Promise<Session[]> => {
    // Use the /by_campaign/{campaign_id} endpoint
    const response = await api.get<Session[]>(`${BASE_URL}/by_campaign/${campaignId}`);
    // response.data will now include characters based on backend changes
    return response.data;
};

// Get a specific session by ID
export const getSessionById = async (sessionId: number): Promise<Session> => {
    const response = await api.get<Session>(`${BASE_URL}/${sessionId}`);
    // response.data will now include characters based on backend changes
    return response.data;
};

// Get all sessions for the current user across their campaigns
export const getMySessions = async (): Promise<Session[]> => {
    const response = await api.get<Session[]>(`${BASE_URL}/my-sessions`);
    return response.data;
};

// Create a new session
export const createSession = async (sessionData: SessionCreate): Promise<Session> => {
    const response = await api.post<Session>(`${BASE_URL}/`, sessionData);
    return response.data;
};

// Update an existing session
// SessionUpdate type now includes optional character_ids
export const updateSession = async (sessionId: number, sessionData: SessionUpdate): Promise<Session> => {
    const response = await api.put<Session>(`${BASE_URL}/${sessionId}`, sessionData);
    // response.data will be the updated session including characters
    return response.data;
};

// Delete a session
export const deleteSession = async (sessionId: number): Promise<void> => {
    // Backend returns the deleted session, but we might not need it in frontend
    await api.delete(`${BASE_URL}/${sessionId}`);
}; 