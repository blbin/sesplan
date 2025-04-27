import { api } from '../auth.service';
import type { User } from '@/types/user'; // Assume User type exists in @/types

const BASE_URL = '/V1/users';

/**
 * Fetches a user by their ID.
 * Requires authentication.
 */
export const getUserById = async (userId: number): Promise<User> => {
    const response = await api.get<User>(`${BASE_URL}/${userId}`);
    return response.data;
};

// Add other user-related API functions if needed later (e.g., update user) 