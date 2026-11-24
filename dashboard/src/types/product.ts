export interface Product {
  id: string;
  shop_id: string;
  name: string;
  cost_price: string;
  selling_price: string;
  stock_quantity: number;
  unit: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductData {
  name: string;
  cost_price: string;
  selling_price: string;
  unit: string;
}

export interface CreateProductData extends ProductData {
  stock_quantity: number;
}