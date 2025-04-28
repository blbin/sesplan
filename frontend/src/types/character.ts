// src/types/character.ts
// import type { User } from './user'; // Assuming User type exists
import type { Journal } from './journal'; // Import Journal type
import type { CharacterTag } from './characterTag'; // Import CharacterTag type

export interface CharacterBase {
    name: string;
    description: string | null;
    user_id?: number | null; // Might not be linked (NPC)
    world_id: number;
}

export interface CharacterCreate extends CharacterBase {
    tag_type_ids?: number[]; // IDs of tag types to associate
}

export interface CharacterUpdate extends Partial<CharacterBase> {
    tag_type_ids?: number[]; // Allow updating tags
}

export interface Character extends CharacterBase {
    id: number;
    created_at: string; // Assuming ISO string format from backend
    updated_at: string;
    journal: Journal | null; // Journal might be loaded optionally
    tags: CharacterTag[]; // Always expect tags array
}

export interface CharacterSimple {
    id: number;
    name: string;
}

export interface CharacterAssignUser {
    user_id: number | null;
}