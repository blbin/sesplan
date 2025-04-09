import { api } from './auth.service';
import type { User } from './auth.service';

export interface UserRegistrationData {
  username: string;
  email: string;
  password: string;
}

export class UserService {
  async register(userData: UserRegistrationData): Promise<User> {
    const response = await api.post<User>('/V1/users/', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await api.get<User>('/V1/users/me');
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch current user:', error);
      return null;
    }
  }
}

export const userService = new UserService(); 