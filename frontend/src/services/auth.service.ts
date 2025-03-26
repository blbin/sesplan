import axios from 'axios';


const API_URL = import.meta.env.VITE_API_URL || 'https://api.sesplan.space';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export class AuthService {
   async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);

     const baseUrl = API_URL?.endsWith('/') ? API_URL.slice(0, -1) : API_URL;

    // Úplná URL s endpointem
    const response = await axios.post(`${baseUrl}/V1/auth/token`, params, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }

    return response.data;
  }

  logout(): void {
    localStorage.removeItem('token');
  }

  getCurrentToken(): string | null {
    return localStorage.getItem('token');
  }
}

export const authService = new AuthService();