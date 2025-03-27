import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://api.sesplan.space';

export interface UserRegistrationData {
  username: string;
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
}

export class UserService {
  async register(userData: UserRegistrationData): Promise<UserResponse> {
    const baseUrl = API_URL?.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
    
    const response = await axios.post(`${baseUrl}/V1/users/`, userData, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    return response.data;
  }

  async getCurrentUser(): Promise<UserResponse | null> {
    const token = localStorage.getItem('token');
    
    if (!token) {
      return null;
    }

    const baseUrl = API_URL?.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
    
    try {
      const response = await axios.get(`${baseUrl}/V1/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });
      
      return response.data;
    } catch (error) {
      // Token is invalid or expired
      localStorage.removeItem('token');
      return null;
    }
  }
}

export const userService = new UserService(); 