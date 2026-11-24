import api from "./api";
import {
  Payment,
  PaymentData,
  PaymentSummary,
} from "@/types/payment";

export async function getPayments(
  shopId: string,
  orderId: string
) {
  const response = await api.get<Payment[]>(
    `/shops/${shopId}/orders/${orderId}/payments`
  );

  return response.data;
}

export async function createPayment(
  shopId: string,
  orderId: string,
  data: PaymentData
) {
  const response = await api.post<Payment>(
    `/shops/${shopId}/orders/${orderId}/payments`,
    data
  );

  return response.data;
}

export async function getPaymentSummary(
  shopId: string,
  orderId: string
) {
  const response = await api.get<PaymentSummary>(
    `/shops/${shopId}/orders/${orderId}/payment-summary`
  );

  return response.data;
}