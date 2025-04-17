// src/types/world.ts
import type { Campaign } from './campaign'; // Import Campaign type

// Odstraněna lokální definice Campaign
// export interface Campaign { ... }

// Základní struktura dat světa vracená z API
export interface World {
  id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  campaigns: Campaign[];
}

// Data potřebná pro vytvoření světa
export interface WorldCreate {
  name: string;
  description?: string | null;
  is_public?: boolean;
}

// Data povolená pro úpravu světa
export interface WorldUpdate {
  name?: string;
  description?: string | null;
  is_public?: boolean;
} 