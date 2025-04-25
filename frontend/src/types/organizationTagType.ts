export interface OrganizationTagTypeBase {
  name: string;
}

export interface OrganizationTagTypeCreate extends OrganizationTagTypeBase {
  world_id: number;
}

export interface OrganizationTagTypeUpdate {
  name?: string;
}

export interface OrganizationTagType extends OrganizationTagTypeBase {
  id: number;
  world_id: number;
  created_at: string;
  updated_at: string;
} 