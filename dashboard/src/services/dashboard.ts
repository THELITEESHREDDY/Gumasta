import api from "./api";

import {
  DashboardSummary,
  DashboardOrder,
  DashboardTransaction,
  DashboardFilters,
  PaginatedResponse,
} from "@/types/dashboard";

export async function getDashboardSummary(
  shopId: string,
  filters: Pick<DashboardFilters, "start_date" | "end_date">
) {
  const response = await api.get<DashboardSummary>(
    `/shops/${shopId}/dashboard/summary`,
    { params: filters }
  );

  return response.data;
}

export async function getDashboardOrders(
  shopId: string,
  filters: DashboardFilters
) {
  const response = await api.get<
    PaginatedResponse<DashboardOrder>
  >(
    `/shops/${shopId}/dashboard/orders`,
    { params: filters }
  );

  return response.data;
}

export async function getDashboardTransactions(
  shopId: string,
  filters: DashboardFilters
) {
  const response = await api.get<
    PaginatedResponse<DashboardTransaction>
  >(
    `/shops/${shopId}/dashboard/transactions`,
    { params: filters }
  );

  return response.data;
}