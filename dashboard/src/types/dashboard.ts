import { OrderStatus } from "./order";
import { PaymentStatus, PaymentMethod } from "./payment";

export interface DashboardSummary {
  start_date: string;
  end_date: string;
  total_sales: string;
  amount_received: string;
  outstanding_amount: string;
  total_orders: number;
}

export interface DashboardOrder {
  order_id: string;
  customer_id: string;
  customer_name: string;
  customer_mobile: string;
  total_amount: string;
  amount_paid: string;
  amount_due: string;
  order_status: OrderStatus;
  payment_status: PaymentStatus;
  created_at: string;
}

export interface DashboardTransaction {
  payment_id: string;
  order_id: string;
  customer_id: string;
  customer_name: string;
  customer_mobile: string;
  amount: string;
  payment_method: PaymentMethod;
  reference: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface DashboardFilters {
  start_date: string;
  end_date: string;
  search?: string;
  limit?: number;
  offset?: number;
}