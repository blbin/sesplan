// Based on backend/src/app/schemas/item.py

export interface ItemBase {
  name: string;
  description?: string | null;
  character_id?: number | null;
  location_id?: number | null;
}

export interface ItemCreate extends ItemBase {
  world_id: number;
}

export interface ItemUpdate {
  name?: string;
  description?: string | null;
  character_id?: number | null;
  location_id?: number | null;
}

export interface Item extends ItemBase {
  id: number;
  world_id: number;
  created_at: string; // Assuming ISO date strings from API
  updated_at: string;
} 