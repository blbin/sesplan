import { api } from '../auth.service';
import type { Location, LocationCreate, LocationUpdate } from '@/types/location';
import type { LocationTag } from '../../types/locationTag';

const BASE_URL = '/V1/locations'; // Define base URL with prefix

export const getLocationsByWorld = async (
  worldId: number,
  skip: number = 0,
  limit: number = 100
): Promise<Location[]> => {
  const response = await api.get(`${BASE_URL}/`, {
    params: { world_id: worldId, skip, limit },
  });
  return response.data;
};

export const createLocation = async (
  locationData: LocationCreate
): Promise<Location> => {
  const response = await api.post(`${BASE_URL}/`, locationData);
  return response.data;
};

export const getLocation = async (
  locationId: number
): Promise<Location> => {
  const response = await api.get(`${BASE_URL}/${locationId}`);
  return response.data;
};

export const updateLocation = async (
  locationId: number,
  locationData: LocationUpdate
): Promise<Location> => {
  const response = await api.put(`${BASE_URL}/${locationId}`, locationData);
  return response.data;
};

export const deleteLocation = async (
  locationId: number
): Promise<Location> => {
  const response = await api.delete(`${BASE_URL}/${locationId}`);
  return response.data;
};

export const getLocationById = async (id: number): Promise<Location> => {
  const response = await api.get<Location>(`${BASE_URL}/${id}`);
  return response.data;
};

export const addTagToLocation = async (locationId: number, tagTypeId: number): Promise<LocationTag> => {
  const response = await api.post<LocationTag>(`${BASE_URL}/${locationId}/tags/${tagTypeId}`);
  return response.data;
};

export const removeTagFromLocation = async (locationId: number, tagTypeId: number): Promise<void> => {
  await api.delete(`${BASE_URL}/${locationId}/tags/${tagTypeId}`);
}; 