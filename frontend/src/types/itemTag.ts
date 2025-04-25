import type { ItemTagType } from './itemTagType';

/**
 * Represents the assignment of a specific tag type to a specific item.
 */
export interface ItemTag {
  id: number; // ID of the assignment itself
  item_id: number;
  item_tag_type_id: number;
  created_at?: string; // ISO date string (Optional, depending on API)
  tag_type?: ItemTagType; // Nested details about the tag type (Optional, depending on API)
}

/**
 * Represents the data needed to assign a tag to an item.
 * Usually just the tag type ID is needed.
 */
export interface ItemTagAssign {
  item_tag_type_id: number;
} 