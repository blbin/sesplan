import { api } from '../auth.service';
import type { Item, ItemCreate, ItemUpdate } from '@/types/item';

const BASE_URL = '/V1/items';

/**
 * Fetches a list of items for a specific world, optionally filtered.
 */
export const getItemsByWorld = async (
  worldId: number,
  characterId?: number | null,
  locationId?: number | null,
  skip: number = 0,
  limit: number = 100
): Promise<Item[]> => {
  const params: Record<string, any> = {
    world_id: worldId,
    skip,
    limit,
  };
  if (characterId) {
    params.character_id = characterId;
  }
  if (locationId) {
    params.location_id = locationId;
  }
  const response = await api.get(`${BASE_URL}/`, { params });
  return response.data;
};

/**
 * Creates a new item.
 */
export const createItem = async (itemData: ItemCreate): Promise<Item> => {
  const response = await api.post(`${BASE_URL}/`, itemData);
  return response.data;
};

/**
 * Fetches a single item by its ID.
 */
export const getItem = async (itemId: number): Promise<Item> => {
  const response = await api.get(`${BASE_URL}/${itemId}`);
  return response.data;
};

/**
 * Updates an existing item.
 */
export const updateItem = async (
  itemId: number,
  itemData: ItemUpdate
): Promise<Item> => {
  const response = await api.put(`${BASE_URL}/${itemId}`, itemData);
  return response.data;
};

/**
 * Deletes an item by its ID.
 */
export const deleteItem = async (itemId: number): Promise<Item> => {
  // Backend returns the deleted item, but we might not need it often.
  // Consider changing the return type to void or a simple success message if preferred.
  const response = await api.delete(`${BASE_URL}/${itemId}`);
  return response.data; 
}; 