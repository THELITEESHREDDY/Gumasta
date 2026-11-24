export type PaymentMethod =
  | "cash"
  | "upi"
  | "bank_transfer"
  | "card";

export type PaymentStatus =
  | "unpaid"
  | "partially_paid"
  | "paid"
  | "cancelled";

export interface PaymentData {
  amount: string;
  payment_method: PaymentMethod;
  reference?: string | null;
}

export interface Payment extends PaymentData {
  id: string;
  order_id: string;
  created_at: string;
}

export interface PaymentSummary {
  order_id: string;
  total_amount: string;
  amount_paid: string;
  amount_due: string;
  payment_status: PaymentStatus;
}