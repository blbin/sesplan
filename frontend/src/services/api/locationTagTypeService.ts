import { api } from '../auth.service'; // Správný import API klienta
import type { LocationTagType, LocationTagTypeCreate, LocationTagTypeUpdate } from '@/types/locationTagType';

const BASE_URL = '/V1/worlds'; // Přidán prefix /V1

/**
 * Získá všechny typy tagů lokací pro daný svět.
 */
export const getLocationTagTypes = async (worldId: number): Promise<LocationTagType[]> => {
  const response = await api.get<LocationTagType[]>(`${BASE_URL}/${worldId}/location-tag-types`);
  return response.data;
};

/**
 * Vytvoří nový typ tagu lokace.
 */
export const createLocationTagType = async (worldId: number, data: LocationTagTypeCreate): Promise<LocationTagType> => {
  const response = await api.post<LocationTagType>(`${BASE_URL}/${worldId}/location-tag-types`, data);
  return response.data;
};

/**
 * Aktualizuje existující typ tagu lokace.
 */
export const updateLocationTagType = async (worldId: number, tagTypeId: number, data: LocationTagTypeUpdate): Promise<LocationTagType> => {
  const response = await api.put<LocationTagType>(`${BASE_URL}/${worldId}/location-tag-types/${tagTypeId}`, data);
  return response.data;
};

/**
 * Smaže typ tagu lokace.
 */
export const deleteLocationTagType = async (worldId: number, tagTypeId: number): Promise<void> => {
  await api.delete(`${BASE_URL}/${worldId}/location-tag-types/${tagTypeId}`);
}; 