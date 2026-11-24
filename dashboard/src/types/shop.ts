export interface Shop {
  id: string;
  owner_id: string;
  name: string;
  gst_id: string | null;
  address: string;
  contact: string;
  created_at: string;
  updated_at: string;
}

export interface CreateShopData {
  name: string;
  gst_id?: string | null;
  address: string;
  contact: string;
}