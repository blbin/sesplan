import { api } from '../auth.service';
import type { CharacterTag } from '@/types/characterTag';

const BASE_URL = '/V1/characters';

/**
 * Přidá tag k charakteru.
 */
export const addTagToCharacter = async (characterId: number, tagTypeId: number): Promise<CharacterTag> => {
  // Backend endpoint očekává ID typu tagu v cestě, ne v těle požadavku
  const response = await api.post<CharacterTag>(`${BASE_URL}/${characterId}/tags/${tagTypeId}`);
  return response.data;
};

/**
 * Odebere tag z charakteru.
 */
export const removeTagFromCharacter = async (characterId: number, tagTypeId: number): Promise<void> => {
  await api.delete(`${BASE_URL}/${characterId}/tags/${tagTypeId}`);
}; 