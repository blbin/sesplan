/**
 * Reprezentuje typ tagu pro charakter (např. NPC, Player Controlled, Merchant).
 */
export interface CharacterTagType {
  id: number;
  world_id: number;
  name: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

// Typ pro vytváření nového typu tagu
export interface CharacterTagTypeCreate {
  name: string;
}

// Typ pro aktualizaci typu tagu
export interface CharacterTagTypeUpdate {
  name?: string;
} 