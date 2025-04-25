import type { OrganizationTag } from './organizationTag';

export interface OrganizationBase {
  name: string;
  description?: string | null;
  parent_organization_id?: number | null;
}

export interface OrganizationCreate extends OrganizationBase {
  world_id: number;
}

export interface OrganizationUpdate {
  name?: string;
  description?: string | null;
  parent_organization_id?: number | null;
}

export interface Organization extends OrganizationBase {
  id: number;
  world_id: number;
  created_at: string; // Assuming ISO date strings from API
  updated_at: string;
  // Add potential future relationships like tags or child organizations if needed
  tags: OrganizationTag[];
  // child_organizations: Organization[]; 
} 