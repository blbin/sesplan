// src/services/api/characters.ts
import { api } from '../auth.service';
import type { Character, CharacterCreate, CharacterUpdate } from '@/types/character';

const BASE_URL = '/V1/characters';
const WORLD_BASE_URL = '/V1/worlds'; // For the nested endpoint

// Get characters owned by the current user (optionally filtered by world)
export const getMyCharacters = async (worldId?: number): Promise<Character[]> => {
    const params = worldId ? { world_id: worldId } : {};
    const response = await api.get<Character[]>(`${BASE_URL}/`, { params });
    return response.data;
};

// Get ALL characters within a specific world (new endpoint)
export const getAllWorldCharacters = async (worldId: number): Promise<Character[]> => {
    const response = await api.get<Character[]>(`${WORLD_BASE_URL}/${worldId}/characters/`);
    return response.data;
};

// Get a specific character by ID
export const getCharacterById = async (id: number): Promise<Character> => {
    const response = await api.get<Character>(`${BASE_URL}/${id}`);
    return response.data;
};

// Create a new character
export const createCharacter = async (characterData: CharacterCreate): Promise<Character> => {
    const response = await api.post<Character>(`${BASE_URL}/`, characterData);
    return response.data;
};

// Update an existing character
export const updateCharacter = async (id: number, characterData: CharacterUpdate): Promise<Character> => {
    const response = await api.put<Character>(`${BASE_URL}/${id}`, characterData);
    return response.data;
};

// Delete a character
export const deleteCharacter = async (id: number): Promise<void> => {
    await api.delete(`${BASE_URL}/${id}`);
}; 