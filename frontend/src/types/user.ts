export interface User {
    id: number;
    username: string;
    email: string;
    first_name?: string | null;
    last_name?: string | null;
    // Add other relevant fields if needed, e.g., created_at
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
} 

/**
 * Simplified user information for embedding.
 */
export interface UserSimple {
  id: number;
  username: string;
} 

export interface UserUpdate {
  first_name?: string | null;
  last_name?: string | null;
  // Add other fields that can be updated
} 

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
} 