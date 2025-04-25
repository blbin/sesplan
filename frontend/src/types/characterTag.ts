import type { CharacterTagType } from './characterTagType';

/**
 * Reprezentuje přiřazení konkrétního typu tagu ke konkrétnímu charakteru.
 */
export interface CharacterTag {
  id: number; // ID samotného přiřazení
  character_id: number;
  character_tag_type_id: number;
  created_at: string; // ISO date string
  tag_type?: CharacterTagType; // Vnořené detaily o typu tagu (volitelné, záleží na API)
} 