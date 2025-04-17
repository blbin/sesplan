// import type { Optional } from './common'; // Assuming Optional exists or handle nullable types directly

// Base properties
export interface SessionBase {
    title: string;
    description?: string | null;
    summary?: string | null;
    date_time?: string | null; // Use string for dates coming from JSON
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
}

// Session object received from API
export interface Session extends SessionBase {
    id: number;
    campaign_id: number;
    created_at: string; // ISO Date string
    updated_at: string; // ISO Date string
    // Add relationships here later if needed (e.g., characters, entries)
} 