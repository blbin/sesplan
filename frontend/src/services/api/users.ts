import { api } from '../auth.service';
import type { User, UserUpdate } from '@/types/user'; // Přidán import UserUpdate

const BASE_URL = '/V1/users';
const ME_URL = '/V1/users/me'; // URL pro aktuálního uživatele

/**
 * Fetches the currently logged-in user's data.
 * Requires authentication.
 */
export const getUserMe = async (): Promise<User> => {
    const response = await api.get<User>(ME_URL);
    return response.data;
};

/**
 * Updates the currently logged-in user's data.
 * Requires authentication.
 */
export const updateUserMe = async (userData: UserUpdate): Promise<User> => {
    const response = await api.put<User>(ME_URL, userData);
    return response.data;
};

/**
 * Fetches a user by their ID.
 * Requires authentication.
 */
export const getUserById = async (userId: number): Promise<User> => {
    const response = await api.get<User>(`${BASE_URL}/${userId}`);
    return response.data;
};

// Add other user-related API functions if needed later (e.g., update user) 