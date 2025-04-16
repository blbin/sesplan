// src/services/api/worlds.ts
// import apiClient from './apiClient'; // Odstraníme původní import
import { api } from '../auth.service'; // Importujeme sdílenou instanci z auth.service
// import type { World, WorldCreate, WorldUpdate } from '@/types/world'; // Definice typů
import type { World, WorldCreate, WorldUpdate } from '../../types/world'; // Zkusíme relativní cestu

// Získání všech světů aktuálního uživatele
export const getWorlds = async (): Promise<World[]> => {
    const response = await api.get<World[]>('/worlds'); // Použijeme 'api'
    return response.data;
};

// Získání konkrétního světa podle ID
export const getWorldById = async (id: number): Promise<World> => {
    const response = await api.get<World>(`/worlds/${id}`); // Použijeme 'api'
    return response.data;
};

// Vytvoření nového světa
export const createWorld = async (worldData: WorldCreate): Promise<World> => {
    const response = await api.post<World>('/worlds', worldData); // Použijeme 'api'
    return response.data;
};

// Aktualizace existujícího světa
export const updateWorld = async (id: number, worldData: WorldUpdate): Promise<World> => {
    const response = await api.put<World>(`/worlds/${id}`, worldData); // Použijeme 'api'
    return response.data;
};

// Smazání světa
export const deleteWorld = async (id: number): Promise<void> => {
    await api.delete(`/worlds/${id}`); // Použijeme 'api'
};

// Pokud budeme potřebovat získat kampaně pro svět:
// export const getWorldCampaigns = async (worldId: number): Promise<Campaign[]> => {
//     const response = await apiClient.get<Campaign[]>(`/worlds/${worldId}/campaigns/`);
//     return response.data;
// }; 