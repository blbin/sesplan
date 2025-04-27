import type { UserSimple } from './user'; // Assuming UserSimple exists for embedding

/**
 * Base interface for UserAvailability data (common fields).
 */
export interface UserAvailabilityBase {
  available_from: string; // ISO 8601 datetime string
  available_to: string;   // ISO 8601 datetime string
  note?: string | null;
}

/**
 * Interface for creating or updating UserAvailability.
 */
export interface UserAvailabilityCreateUpdate extends UserAvailabilityBase {}

/**
 * Interface representing a UserAvailability record received from the API.
 */
export interface UserAvailability extends UserAvailabilityBase {
  id: number;
  user_id: number;
  slot_id: number;
  user: UserSimple; // Embed simplified user info
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
} 