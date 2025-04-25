import { api } from '../auth.service';
import type { CharacterTagType, CharacterTagTypeCreate, CharacterTagTypeUpdate } from '@/types/characterTagType';

const BASE_URL = '/V1/worlds'; 

/**
 * Získá všechny typy tagů charakterů pro daný svět.
 */
export const getCharacterTagTypes = async (worldId: number): Promise<CharacterTagType[]> => {
  const response = await api.get<CharacterTagType[]>(`${BASE_URL}/${worldId}/character-tag-types`);
  return response.data;
};

/**
 * Vytvoří nový typ tagu charakteru.
 */
export const createCharacterTagType = async (worldId: number, data: CharacterTagTypeCreate): Promise<CharacterTagType> => {
  const response = await api.post<CharacterTagType>(`${BASE_URL}/${worldId}/character-tag-types`, data);
  return response.data;
};

/**
 * Aktualizuje existující typ tagu charakteru.
 */
export const updateCharacterTagType = async (worldId: number, tagTypeId: number, data: CharacterTagTypeUpdate): Promise<CharacterTagType> => {
  const response = await api.put<CharacterTagType>(`${BASE_URL}/${worldId}/character-tag-types/${tagTypeId}`, data);
  return response.data;
};

/**
 * Smaže typ tagu charakteru.
 */
export const deleteCharacterTagType = async (worldId: number, tagTypeId: number): Promise<void> => {
  await api.delete(`${BASE_URL}/${worldId}/character-tag-types/${tagTypeId}`);
}; 