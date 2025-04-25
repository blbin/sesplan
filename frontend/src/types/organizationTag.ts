import type { OrganizationTagType } from './organizationTagType';

export interface OrganizationTagBase {
  organization_id: number;
  organization_tag_type_id: number;
}

export interface OrganizationTagCreate extends OrganizationTagBase {}

// Updates are not typical for association tables
// export interface OrganizationTagUpdate {}

export interface OrganizationTag extends OrganizationTagBase {
  id: number;
  created_at: string;
  tag_type?: OrganizationTagType; // Embed the type details
} 