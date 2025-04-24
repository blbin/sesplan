import type { LocationTagType } from './locationTagType';

/**
 * Reprezentuje přiřazení konkrétního typu tagu ke konkrétní lokaci.
 */
export interface LocationTag {
  id: number; // ID samotného přiřazení
  location_id: number;
  location_tag_type_id: number;
  created_at: string; // ISO date string
  tag_type?: LocationTagType; // Vnořené detaily o typu tagu (volitelné, záleží na API)
} 