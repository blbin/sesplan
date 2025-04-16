// src/services/api/campaigns.ts
import { api } from '../auth.service'; // Použijeme sdílenou instanci Axios
import type { Campaign, CampaignCreate, CampaignUpdate } from '@/types/campaign';

// Získání všech kampaní (nebo filtrovaných podle světa)
export const getCampaigns = async (worldId?: number): Promise<Campaign[]> => {
    // Pokud je worldId zadáno, přidáme ho jako query parametr
    const params = worldId ? { world_id: worldId } : {};
    const response = await api.get<Campaign[]>('/V1/campaigns/', { params });
    return response.data;
};

// Získání konkrétní kampaně podle ID
export const getCampaignById = async (id: number): Promise<Campaign> => {
    const response = await api.get<Campaign>(`/V1/campaigns/${id}`);
    return response.data;
};

// Vytvoření nové kampaně
export const createCampaign = async (campaignData: CampaignCreate): Promise<Campaign> => {
    const response = await api.post<Campaign>('/V1/campaigns/', campaignData);
    return response.data;
};

// Aktualizace existující kampaně
export const updateCampaign = async (id: number, campaignData: CampaignUpdate): Promise<Campaign> => {
    const response = await api.put<Campaign>(`/V1/campaigns/${id}`, campaignData);
    return response.data;
};

// Smazání kampaně
export const deleteCampaign = async (id: number): Promise<void> => {
    await api.delete(`/V1/campaigns/${id}`);
}; 