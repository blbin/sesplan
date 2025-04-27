import type { UserAvailability } from './user_availability';

/**
 * Base interface for SessionSlot data (common fields).
 */
export interface SessionSlotBase {
  slot_from: string; // ISO 8601 datetime string
  slot_to: string;   // ISO 8601 datetime string
  note?: string | null;
}

/**
 * Interface for creating a new SessionSlot.
 */
export interface SessionSlotCreate extends SessionSlotBase {}

/**
 * Interface for updating an existing SessionSlot.
 * All fields are optional.
 */
export interface SessionSlotUpdate {
  slot_from?: string;
  slot_to?: string;
  note?: string | null;
}

/**
 * Interface representing a SessionSlot received from the API.
 */
export interface SessionSlot extends SessionSlotBase {
  id: number;
  session_id: number;
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
  user_availabilities: UserAvailability[]; // Embed user availabilities
} 