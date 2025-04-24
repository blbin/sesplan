/**
 * Reprezentuje typ tagu pro lokaci (např. Město, Jeskyně, Obchod).
 */
export interface LocationTagType {
  id: number;
  world_id: number;
  name: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  // Případně další vlastnosti jako color, description, pokud je přidáme
}

// Typ pro vytváření nového typu tagu
export interface LocationTagTypeCreate {
  name: string;
}

// Typ pro aktualizaci typu tagu
export interface LocationTagTypeUpdate {
  name?: string;
} 