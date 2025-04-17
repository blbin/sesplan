// src/types/character.ts
// import type { User } from './user'; // Assuming User type exists

export interface CharacterBase {
    name: string;
    description: string | null;
}

export interface CharacterCreate extends CharacterBase {
    world_id: number;
}

// All fields are optional for update
export interface CharacterUpdate {
    name?: string;
    description?: string | null;
    // Cannot change world_id or user_id via update
}

export interface Character extends CharacterBase {
    id: number;
    world_id: number;
    user_id: number; // ID of the user who owns/created the character
    created_at: string; // ISO Date string
    updated_at: string; // ISO Date string
    // Optional: Include user details if backend sends them (check API response)
    // user?: User;
} 