export interface Customer {
  id: string;
  shop_id: string;
  name: string;
  mobile: string;
  alternate_mobile: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
}

export interface CustomerData {
  name: string;
  mobile: string;
  alternate_mobile?: string | null;
  address?: string | null;
}