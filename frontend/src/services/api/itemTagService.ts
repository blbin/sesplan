import { api } from '../auth.service';
import type { ItemTag } from '@/types/itemTag';

const BASE_URL = '/V1/items';

/**
 * Assigns a tag type to an item.
 * @param itemId - The ID of the item.
 * @param tagTypeId - The ID of the item tag type to assign.
 * @returns A promise resolving to the created item tag assignment.
 */
export const addItemTagToItem = async (itemId: number, tagTypeId: number): Promise<ItemTag> => {
    const response = await api.post<ItemTag>(`${BASE_URL}/${itemId}/tags/${tagTypeId}`);
    return response.data;
};

/**
 * Removes a tag type from an item.
 * @param itemId - The ID of the item.
 * @param tagTypeId - The ID of the item tag type to remove.
 * @returns A promise resolving when the deletion is complete.
 */
export const removeItemTagFromItem = async (itemId: number, tagTypeId: number): Promise<void> => {
    await api.delete(`${BASE_URL}/${itemId}/tags/${tagTypeId}`);
};

// Optional: Function to get all tags for a specific item, if needed
// export const getItemTagsForItem = async (itemId: number): Promise<ItemTag[]> => {
//     const response = await api.get<ItemTag[]>(`${BASE_URL}/${itemId}/tags`);
//     return response.data;
// }; 