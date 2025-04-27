export interface User {
    id: number;
    username: string;
    email: string;
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