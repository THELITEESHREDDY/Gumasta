import api from "./api";
import { Shop, CreateShopData } from "@/types/shop";

export async function getShops() {
  const response = await api.get<Shop[]>("/shops");
  return response.data;
}

export async function createShop(data: CreateShopData) {
  const response = await api.post<Shop>("/shops", data);
  return response.data;
}

export async function getShop(shopId: string) {
  const response = await api.get<Shop>(`/shops/${shopId}`);
  return response.data;
}

export async function updateShop(
  shopId: string,
  data: Partial<CreateShopData>
) {
  const response = await api.patch<Shop>(
    `/shops/${shopId}`,
    data
  );

  return response.data;
}