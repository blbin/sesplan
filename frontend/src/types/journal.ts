// import type { JournalEntry } from './journal_entry'; // Import related type
// import type { Optional } from '@/types/common'; // Assuming a common Optional type exists or define it

// Base properties
export interface JournalBase {
    name: string;
    description: string | null;
}

// REMOVED JournalCreate - Journal is created with Character

// Properties for update (all optional)
export interface JournalUpdate {
    name?: string;
    description?: string | null; // Use string | null | undefined (or just string | null)
}

// Properties returned from API (read)
export interface Journal extends JournalBase {
    id: number;
    character_id: number;
    created_at: string; // ISO Date string
    updated_at: string | null; // ISO Date string or null
    // entries: JournalEntry[]; // Maybe include entries directly?
                       // Or fetch separately for performance.
                       // Keep simple for now.
} 