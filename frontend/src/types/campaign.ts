// src/types/campaign.ts

// Základní struktura dat kampaně vracená z API
export interface Campaign {
  id: number;
  name: string;
  description: string | null;
  world_id: number;
  created_at: string; // Datum jako string (ISO formát)
  updated_at: string; // Datum jako string (ISO formát)
  // Zde můžeme přidat další pole, pokud API vrací např. info o světě
  // world?: { id: number; name: string };
}

// Data potřebná pro vytvoření kampaně
export interface CampaignCreate {
  name: string;
  world_id: number; // Povinné při vytváření
  description?: string | null;
}

// Data povolená pro úpravu kampaně
export interface CampaignUpdate {
  name?: string;
  description?: string | null;
  // world_id zde neumožňujeme měnit přes standardní update
} 