// import type { Optional } from './common'; // Assuming Optional exists or handle nullable types directly
import type { SessionSlot } from './session_slot'; // Added
import type { CharacterSimple } from './character'; // Import CharacterSimple as type
import type { Campaign } from './campaign'; // Import Campaign type

// Base properties shared by create/update/read
export interface SessionBase {
    title: string;
    description?: string | null;
    summary?: string | null;
    date_time?: string | null; // Use string for dates coming from JSON
    // availability_slots?: SessionSlot[]; // Moved to Session interface, not needed in base/create
}

// For creating a session
export interface SessionCreate extends SessionBase {
    campaign_id: number;
}

// For updating a session (all fields optional)
export interface SessionUpdate {
    title?: string;
    description?: string | null; // Use standard union type
    summary?: string | null;
    date_time?: string | null;
    character_ids?: number[]; // Add character IDs for update
}

// Session object received from API
export interface Session extends SessionBase {
    id: number;
    campaign_id: number;
    created_at: string; // ISO Date string - Belongs here
    updated_at: string; // ISO Date string - Belongs here
    availability_slots?: SessionSlot[]; // Optional relationship data
    characters: CharacterSimple[]; // Add associated characters
    campaign?: Campaign; // Add optional campaign relationship
    // Add relationships here later if needed (e.g., characters, entries)
} 