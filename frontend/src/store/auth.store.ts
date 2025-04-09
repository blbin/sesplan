import { defineStore } from 'pinia';
import { authService } from '@/services/auth.service';
import type { User, LoginCredentials } from '@/services/auth.service';
import { userService } from '@/services/user.service';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null as User | null,
    loading: false,
    error: null as string | null,
  }),
  getters: {
    isLoggedIn: (state): boolean => !!state.token && !!state.user,
    currentUser: (state) => state.user,
    isLoading: (state) => state.loading,
    authError: (state) => state.error,
  },
  actions: {
    async login(credentials: LoginCredentials) {
      this.loading = true;
      this.error = null;
      try {
        const response = await authService.login(credentials);
        this.token = response.access_token;
        await this.fetchCurrentUser();
        if (!this.user) {
           throw new Error("Failed to fetch user data after login.");
        }
      } catch (err: any) {
        this.token = null;
        this.user = null;
        this.error = err.response?.data?.detail || err.message || 'Login failed';
        localStorage.removeItem('token');
        console.error("Login error in store:", err);
        throw err;
      } finally {
        this.loading = false;
      }
    },
    logout() {
      authService.logout();
      this.token = null;
      this.user = null;
      this.error = null;
    },
    async fetchCurrentUser() {
       if (!this.token) {
         this.user = null;
         console.log("fetchCurrentUser: No token, clearing user.");
         return;
       }

      if (this.user) {
          console.log("fetchCurrentUser: User already loaded.");
          return;
      }

      this.loading = true;
      this.error = null;
      console.log("fetchCurrentUser: Fetching user data...");
      try {
        const userData = await userService.getCurrentUser();
        this.user = userData;
        if (!userData) {
          console.warn("fetchCurrentUser returned null, logging out.");
          this.logout();
        } else {
           console.log("fetchCurrentUser: User data loaded successfully:", userData);
        }
      } catch (err: any) {
        console.error("Fetch user error in store:", err);
        this.error = err.message || 'Failed to fetch user data';
        this.logout();
        this.user = null;
      } finally {
        this.loading = false;
      }
    },
    async initializeAuth() {
       if (this.token && !this.user) {
         console.log("Initializing auth: Found token, fetching user...");
        await this.fetchCurrentUser();
      } else if (this.token && this.user) {
         console.log("Initializing auth: Token and user already present.");
      } else if (!this.token) {
         console.log("Initializing auth: No token found.");
         this.user = null;
      }
    }
  },
}); 