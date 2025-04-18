export interface LocationBase {
  name: string;
  description?: string | null;
  parent_location_id?: number | null;
}

export interface LocationCreate extends LocationBase {
  world_id: number;
}

export interface LocationUpdate {
  name?: string;
  description?: string | null;
  parent_location_id?: number | null;
}

export interface Location extends LocationBase {
  id: number;
  world_id: number;
  created_at: string; // Assuming ISO date strings from API
  updated_at: string;
} 