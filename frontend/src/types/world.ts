// src/types/world.ts

// Typ pro kampaň - nyní odpovídá backendovému schématu Campaign
export interface Campaign { // Přejmenováno z CampaignSummary
  id: number;
  name: string;
  description: string | null;
  world_id: number;
  owner_id: number;
  created_at: string; // Datum jako string (ISO formát)
  updated_at: string; // Datum jako string (ISO formát)
}

// Základní struktura dat světa vracená z API
export interface World {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string; // Datum jako string (ISO formát)
  updated_at: string; // Datum jako string (ISO formát)
  campaigns: Campaign[]; // Použijeme plný typ Campaign
}

// Data potřebná pro vytvoření světa
export interface WorldCreate {
  name: string;
  description?: string | null;
}

// Data povolená pro úpravu světa (všechna jsou volitelná)
export interface WorldUpdate {
  name?: string; // Ponecháme jako volitelné, ale ne undefined
  description?: string | null;
} 