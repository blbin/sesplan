export interface CampaignInviteBase {
    campaign_id: number;
    token: string;
    max_uses: number | null;
    uses: number;
    expires_at: string | null; // ISO Date string or null
}

export interface CampaignInviteCreate {
    max_uses?: number | null; // Optional on creation
    expires_at?: string | null; // Optional on creation, ISO Date string
}

export interface CampaignInvite extends CampaignInviteBase {
    id: number;
    created_at: string; // ISO Date string
    updated_at: string; // ISO Date string
}

export interface CampaignInviteAcceptResponse {
    message: string;
    campaign_id: number;
    role: string; // Role might be an enum later
} 