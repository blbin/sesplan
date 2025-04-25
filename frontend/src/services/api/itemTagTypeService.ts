import { api } from '../auth.service';
import type { ItemTagType, ItemTagTypeCreate, ItemTagTypeUpdate } from '../../types/itemTagType';

const BASE_URL = (worldId: number) => `/V1/worlds/${worldId}/item-tag-types/`;

/**
 * Fetches all item tag types for a specific world.
 * @param worldId - The ID of the world.
 * @returns A promise resolving to an array of item tag types.
 */
export const getItemTagTypes = async (worldId: number): Promise<ItemTagType[]> => {
    const response = await api.get<ItemTagType[]>(BASE_URL(worldId));
    return response.data;
};

/**
 * Creates a new item tag type for a specific world.
 * @param worldId - The ID of the world.
 * @param tagTypeData - The data for the new tag type.
 * @returns A promise resolving to the created item tag type.
 */
export const createItemTagType = async (worldId: number, tagTypeData: ItemTagTypeCreate): Promise<ItemTagType> => {
    const response = await api.post<ItemTagType>(BASE_URL(worldId), tagTypeData);
    return response.data;
};

/**
 * Updates an existing item tag type.
 * @param worldId - The ID of the world.
 * @param tagTypeId - The ID of the tag type to update.
 * @param tagTypeData - The update data.
 * @returns A promise resolving to the updated item tag type.
 */
export const updateItemTagType = async (worldId: number, tagTypeId: number, tagTypeData: ItemTagTypeUpdate): Promise<ItemTagType> => {
    const response = await api.put<ItemTagType>(`${BASE_URL(worldId)}/${tagTypeId}`, tagTypeData);
    return response.data;
};

/**
 * Deletes an item tag type.
 * @param worldId - The ID of the world.
 * @param tagTypeId - The ID of the tag type to delete.
 * @returns A promise resolving when the deletion is complete.
 */
export const deleteItemTagType = async (worldId: number, tagTypeId: number): Promise<void> => {
    await api.delete(`${BASE_URL(worldId)}/${tagTypeId}`);
}; 