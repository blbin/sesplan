import { api } from '../auth.service';
import type { 
    OrganizationTagType, 
    OrganizationTagTypeCreate, 
    OrganizationTagTypeUpdate 
} from '@/types/organizationTagType';

// Base URL structure assumes nesting under worlds
const getWorldTagTypeBaseUrl = (worldId: number) => `/V1/worlds/${worldId}/organization-tag-types`;

export const getOrganizationTagTypes = async (worldId: number): Promise<OrganizationTagType[]> => {
  const url = `${getWorldTagTypeBaseUrl(worldId)}/`;
  const response = await api.get<OrganizationTagType[]>(url);
  return response.data;
};

export const createOrganizationTagType = async (
  worldId: number, 
  tagTypeData: Omit<OrganizationTagTypeCreate, 'world_id'> // world_id is from path
): Promise<OrganizationTagType> => {
  const url = `${getWorldTagTypeBaseUrl(worldId)}/`;
  const response = await api.post<OrganizationTagType>(url, tagTypeData);
  return response.data;
};

export const updateOrganizationTagType = async (
  worldId: number, 
  tagTypeId: number, 
  tagTypeData: OrganizationTagTypeUpdate
): Promise<OrganizationTagType> => {
  const url = `${getWorldTagTypeBaseUrl(worldId)}/${tagTypeId}`;
  const response = await api.put<OrganizationTagType>(url, tagTypeData);
  return response.data;
};

export const deleteOrganizationTagType = async (worldId: number, tagTypeId: number): Promise<void> => {
  const url = `${getWorldTagTypeBaseUrl(worldId)}/${tagTypeId}`;
  await api.delete(url);
}; 