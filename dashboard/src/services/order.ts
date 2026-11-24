import api from "./api";
import {
  Order,
  OrderDetail,
  CreateOrderData,
} from "@/types/order";

export async function getOrders(shopId: string) {
  const response = await api.get<Order[]>(
    `/shops/${shopId}/orders`
  );

  return response.data;
}

export async function createOrder(
  shopId: string,
  data: CreateOrderData
) {
  const response = await api.post<OrderDetail>(
    `/shops/${shopId}/orders`,
    data
  );

  return response.data;
}

export async function getOrder(
  shopId: string,
  orderId: string
) {
  const response = await api.get<OrderDetail>(
    `/shops/${shopId}/orders/${orderId}`
  );

  return response.data;
}

export async function cancelOrder(
  shopId: string,
  orderId: string
) {
  await api.post(
    `/shops/${shopId}/orders/${orderId}/cancel`
  );
}