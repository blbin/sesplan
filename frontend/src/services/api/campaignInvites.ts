import { api } from '../auth.service';
import type { CampaignInvite, CampaignInviteCreate, CampaignInviteAcceptResponse } from '../../types/campaign_invite'; // Use relative path

const CAMPAIGN_BASE_URL = '/V1/campaigns';
const INVITE_BASE_URL = '/V1/invites';

// --- Campaign Specific Invites --- 

export const getCampaignInvites = async (campaignId: number): Promise<CampaignInvite[]> => {
    const response = await api.get(`${CAMPAIGN_BASE_URL}/${campaignId}/invites/`);
    return response.data;
};

export const createCampaignInvite = async (campaignId: number, inviteData: CampaignInviteCreate): Promise<CampaignInvite> => {
    const response = await api.post(`${CAMPAIGN_BASE_URL}/${campaignId}/invites/`, inviteData);
    return response.data;
};

// --- General Invite Operations --- 

export const acceptCampaignInvite = async (token: string): Promise<CampaignInviteAcceptResponse> => {
    // No payload needed, token is in URL
    const response = await api.post(`${INVITE_BASE_URL}/${token}/accept`);
    return response.data;
};

export const deleteCampaignInvite = async (inviteId: number): Promise<CampaignInvite> => {
    const response = await api.delete(`${INVITE_BASE_URL}/${inviteId}`);
    return response.data; // Backend returns the deleted invite
}; 