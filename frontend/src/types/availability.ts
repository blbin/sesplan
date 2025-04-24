export interface AvailabilityBase {
  available_from: string; // ISO 8601 format
  available_to: string;   // ISO 8601 format
  note?: string | null;
}

export interface AvailabilityCreate extends AvailabilityBase {}

export interface AvailabilityUpdate extends AvailabilityBase {}

export interface Availability extends AvailabilityBase {
  id: number;
  user_id: number;
  session_id: number;
  created_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
} 