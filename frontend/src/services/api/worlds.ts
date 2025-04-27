// src/services/api/worlds.ts
// import apiClient from './apiClient'; // Odstraníme původní import
import { api } from '../auth.service'; // Importujeme sdílenou instanci z auth.service
// import type { World, WorldCreate, WorldUpdate } from '@/types/world'; // Definice typů
import type { World, WorldCreate, WorldUpdate } from '../../types/world';
// Import Campaign type directly from campaign.ts
import type { Campaign } from '../../types/campaign';

// Define UserSimple type for the new function
export interface UserSimple {
    id: number;
    username: string;
}

// Získání všech světů aktuálního uživatele
export const getWorlds = async (): Promise<World[]> => {
    const response = await api.get<World[]>('/V1/worlds/'); // Použijeme 'api'
    return response.data;
};

// Získání konkrétního světa podle ID
export const getWorldById = async (id: number): Promise<World> => {
    const response = await api.get<World>(`/V1/worlds/${id}`); // Použijeme 'api'
    return response.data;
};

// Vytvoření nového světa
export const createWorld = async (worldData: WorldCreate): Promise<World> => {
    const response = await api.post<World>('/V1/worlds/', worldData); // Použijeme 'api'
    return response.data;
};

// Aktualizace existujícího světa
export const updateWorld = async (id: number, worldData: WorldUpdate): Promise<World> => {
    const response = await api.put<World>(`/V1/worlds/${id}`, worldData); // Použijeme 'api'
    return response.data;
};

// Smazání světa
export const deleteWorld = async (id: number): Promise<void> => {
    await api.delete(`/V1/worlds/${id}`); // Použijeme 'api'
};

// Získání kampaní pro daný svět
export const getWorldCampaigns = async (worldId: number): Promise<Campaign[]> => {
    const response = await api.get<Campaign[]>(`/V1/worlds/${worldId}/campaigns/`);
    return response.data;
};

// Get users participating in campaigns within a specific world
export const getCampaignUsersInWorld = async (worldId: number): Promise<UserSimple[]> => {
    const response = await api.get<UserSimple[]>(`/V1/worlds/${worldId}/campaign_users`);
    return response.data;
};