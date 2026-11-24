import api from "./api";
import { Customer, CustomerData } from "@/types/customer";

export async function getCustomers(
  shopId: string,
  search?: string
) {
  const response = await api.get<Customer[]>(
    `/shops/${shopId}/customers`,
    { params: { search } }
  );

  return response.data;
}

export async function getCustomer(
  shopId: string,
  customerId: string
) {
  const response = await api.get<Customer>(
    `/shops/${shopId}/customers/${customerId}`
  );

  return response.data;
}

export async function createCustomer(
  shopId: string,
  data: CustomerData
) {
  const response = await api.post<Customer>(
    `/shops/${shopId}/customers`,
    data
  );

  return response.data;
}

export async function updateCustomer(
  shopId: string,
  customerId: string,
  data: Partial<CustomerData>
) {
  const response = await api.patch<Customer>(
    `/shops/${shopId}/customers/${customerId}`,
    data
  );

  return response.data;
}