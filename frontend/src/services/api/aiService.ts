import { api } from '../auth.service'; // Importujeme sdílenou instanci z auth.service
import type { AxiosResponse } from 'axios';

// Define types for the request body and response (can be refined later)
// Consider creating specific types in @/types/ai.ts if needed
interface GenerateEntityPayload {
    existing_entities: Record<string, any>[];
    context?: string | null;
}

// The response type depends on the generated entity, using 'any' for now
type GenerateEntityResponse = any;

export const aiService = {
    /**
     * Generates a new entity using the AI backend.
     * @param worldId - The ID of the world context.
     * @param entityType - The type of entity to generate (e.g., 'character', 'location').
     * @param payload - The request body containing examples and context.
     * @returns The newly generated entity data.
     */
    generateEntity(
        worldId: number,
        entityType: string,
        payload: GenerateEntityPayload
    ): Promise<GenerateEntityResponse> {
        // Use the correct API base path if needed (assuming '/api/v1' is handled by 'api' instance)
        return api.post<GenerateEntityResponse>(
            `/V1/ai/worlds/${worldId}/generate/${entityType}`,
            payload
        ).then((response: AxiosResponse<GenerateEntityResponse>) => response.data);
    }

    // TODO: Add function for summarizeSession if needed
}; 