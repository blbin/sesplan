import axios from 'axios';

// Definice typu User (měla by být v samostatném souboru, např. @/types/user.ts)
export interface User {
  id: number;
  email: string;
  username: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'https://api.sesplan.space';

// Vytvoření centrální Axios instance
const api = axios.create({
  baseURL: API_URL,
});

// Funkce pro získání tokenu
function getCurrentToken(): string | null {
  return localStorage.getItem('token');
}

// Interceptor pro přidání tokenu do hlavičky
api.interceptors.request.use(
  config => {
    const token = getCurrentToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

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

    // Použijeme centrální instanci a relativní cestu
    const response = await api.post<LoginResponse>('/V1/auth/token', params, {
      // withCredentials: true, // Není potřeba pro Bearer token
      headers: {
        // 'Accept': 'application/json' // Axios přidá automaticky pro JSON
        // Hlavičku Content-Type pro x-www-form-urlencoded nastaví Axios také automaticky
      }
    });

    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      // Po úspěšném přihlášení můžeme načíst data uživatele
      // await userService.fetchCurrentUser(); // Toto bude řešit store
    }

    return response.data;
  }

  logout(): void {
    localStorage.removeItem('token');
    // Zde bychom měli také vymazat data uživatele ze store
    // Např. useAuthStore().clearUser();
  }

  // getCurrentToken již není potřeba jako public metoda, používá se interně
}

export const authService = new AuthService();

// Exportujeme i api instanci pro použití v jiných službách
export { api };