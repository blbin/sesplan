import { api } from '../auth.service';
import type { User, UserUpdate, ChangePasswordPayload } from '@/types/user'; // Přidán import ChangePasswordPayload

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
 * Changes the currently logged-in user's password.
 * Requires authentication.
 */
export const changePassword = async (payload: ChangePasswordPayload): Promise<void> => {
    // Předpokládáme endpoint /me/change-password
    await api.put(`${ME_URL}/change-password`, payload);
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