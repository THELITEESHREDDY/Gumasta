export type OrderStatus = "completed" | "cancelled";

export interface OrderItemData {
  product_id: string;
  quantity: number;
  unit_price?: string;
}

export interface CreateOrderData {
  customer_id: string;
  order_items: OrderItemData[];
}

export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: string;
  subtotal: string;
}

export interface Order {
  id: string;
  shop_id: string;
  customer_id: string;
  total_amount: string;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
}

export interface OrderDetail extends Order {
  order_items: OrderItem[];
}