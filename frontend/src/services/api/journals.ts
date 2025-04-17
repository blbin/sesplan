import { api } from '../auth.service'; // Assuming auth service setup
import type { Journal, JournalUpdate } from '@/types/journal';

const BASE_URL = '/V1/journals';

// Get a specific journal by ID
export const getJournalById = async (journalId: number): Promise<Journal> => {
    const response = await api.get<Journal>(`${BASE_URL}/${journalId}`);
    return response.data;
};

// Update an existing journal
export const updateJournal = async (journalId: number, journalData: JournalUpdate): Promise<Journal> => {
    const response = await api.put<Journal>(`${BASE_URL}/${journalId}`, journalData);
    return response.data;
}; 