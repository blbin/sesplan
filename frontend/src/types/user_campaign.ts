import type { CampaignRoleEnum } from './campaign_role';
import type { User } from './user'; // Assuming User type exists or will be created

export interface UserCampaignBase {
    user_id: number;
    campaign_id: number;
    role: CampaignRoleEnum;
}

export interface UserCampaignUpdate {
    role: CampaignRoleEnum;
}

export interface UserCampaignRead extends UserCampaignBase {
    id: number;
    user: User; // Nested user details
    created_at: string; // Dates are usually strings from JSON
    updated_at: string;
} 