import { api } from '../auth.service';
import type { Organization, OrganizationCreate, OrganizationUpdate } from '@/types/organization';
import type { OrganizationTag } from '@/types/organizationTag';

const BASE_URL = '/V1/organizations';

export const getOrganizationsByWorld = async (
  worldId: number,
  skip: number = 0,
  limit: number = 100
): Promise<Organization[]> => {
  const response = await api.get(`${BASE_URL}/`, {
    params: { world_id: worldId, skip, limit },
  });
  return response.data;
};

export const createOrganization = async (
  organizationData: OrganizationCreate
): Promise<Organization> => {
  const response = await api.post(`${BASE_URL}/`, organizationData);
  return response.data;
};

export const getOrganizationById = async (
  organizationId: number
): Promise<Organization> => {
  const response = await api.get(`${BASE_URL}/${organizationId}`);
  return response.data;
};

export const updateOrganization = async (
  organizationId: number,
  organizationData: OrganizationUpdate
): Promise<Organization> => {
  const response = await api.put(`${BASE_URL}/${organizationId}`, organizationData);
  return response.data;
};

export const deleteOrganization = async (
  organizationId: number
): Promise<Organization> => {
  // Backend returns the deleted organization, adjust if it returns 204 later
  const response = await api.delete(`${BASE_URL}/${organizationId}`);
  return response.data;
};

// --- Tag Management --- 

export const addTagToOrganization = async (
    organizationId: number, 
    tagTypeId: number
): Promise<OrganizationTag> => {
  const response = await api.post<OrganizationTag>(`${BASE_URL}/${organizationId}/tags/${tagTypeId}`);
  return response.data;
};

export const removeTagFromOrganization = async (
    organizationId: number, 
    tagTypeId: number
): Promise<void> => {
  await api.delete(`${BASE_URL}/${organizationId}/tags/${tagTypeId}`);
};

// Add other potential functions like addTagToOrganization, removeTagFromOrganization later if needed 