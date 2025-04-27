import { api } from '../auth.service';
import type { UserCampaignRead, UserCampaignUpdate } from '@/types/user_campaign';
import type { CampaignRoleEnum } from '@/types/campaign_role';

const BASE_URL = '/V1/campaigns';

export const getCampaignMembers = async (campaignId: number): Promise<UserCampaignRead[]> => {
    const response = await api.get(`${BASE_URL}/${campaignId}/members/`);
    return response.data;
};

export const getCurrentUserMembership = async (campaignId: number): Promise<UserCampaignRead> => {
    const response = await api.get<UserCampaignRead>(`${BASE_URL}/${campaignId}/members/me`);
    return response.data;
};

export const updateCampaignMemberRole = async (
    campaignId: number,
    userId: number,
    role: CampaignRoleEnum
): Promise<UserCampaignRead> => {
    const payload: UserCampaignUpdate = { role };
    const response = await api.put(`${BASE_URL}/${campaignId}/members/${userId}`, payload);
    return response.data;
};

export const removeCampaignMember = async (
    campaignId: number,
    userId: number
): Promise<void> => {
    await api.delete(`${BASE_URL}/${campaignId}/members/${userId}`);
}; 