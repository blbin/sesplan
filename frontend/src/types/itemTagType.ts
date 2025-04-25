export interface ItemTagType {
    id: number;
    name: string;
    world_id: number;
  }
  
  export interface ItemTagTypeCreate {
    name: string;
  }
  
  export type ItemTagTypeUpdate = Partial<ItemTagTypeCreate>;