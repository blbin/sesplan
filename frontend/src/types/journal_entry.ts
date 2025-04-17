// import type { Optional } from '@/types/common'; // Assuming common Optional type

// Base properties
export interface JournalEntryBase {
    title: string | null;
    content: string;
}

// Properties for creation
export interface JournalEntryCreate extends JournalEntryBase {
    journal_id: number;
}

// Properties for update (all optional)
export interface JournalEntryUpdate {
    title?: string | null; // Use string | null | undefined (or just string | null)
    content?: string;
}

// Properties returned from API (read)
export interface JournalEntry extends JournalEntryBase {
    id: number;
    journal_id: number;
    created_at: string; // ISO Date string
    updated_at: string | null; // ISO Date string or null
} 