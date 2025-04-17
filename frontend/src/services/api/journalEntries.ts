import { api } from '../auth.service'; // Assuming auth service setup
import type { JournalEntry, JournalEntryCreate, JournalEntryUpdate } from '@/types/journal_entry';

// Note the prefix from the backend router
const BASE_URL = '/V1/journal-entries'; 

// Create a new journal entry
export const createJournalEntry = async (entryData: JournalEntryCreate): Promise<JournalEntry> => {
    const response = await api.post<JournalEntry>(`${BASE_URL}/`, entryData);
    return response.data;
};

// Get all entries for a specific journal
export const getEntriesByJournal = async (journalId: number): Promise<JournalEntry[]> => {
    const response = await api.get<JournalEntry[]>(`${BASE_URL}/by_journal/${journalId}`);
    return response.data;
};

// Get a specific journal entry by ID
export const getJournalEntryById = async (entryId: number): Promise<JournalEntry> => {
    const response = await api.get<JournalEntry>(`${BASE_URL}/${entryId}`);
    return response.data;
};

// Update an existing journal entry
export const updateJournalEntry = async (entryId: number, entryData: JournalEntryUpdate): Promise<JournalEntry> => {
    const response = await api.put<JournalEntry>(`${BASE_URL}/${entryId}`, entryData);
    return response.data;
};

// Delete a journal entry
export const deleteJournalEntry = async (entryId: number): Promise<void> => {
    await api.delete(`${BASE_URL}/${entryId}`);
}; 