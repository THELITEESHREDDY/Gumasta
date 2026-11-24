import api from "./api";

import {
  Product,
  ProductData,
  CreateProductData,
} from "@/types/product";

export async function getProducts(shopId: string) {
  const response = await api.get<Product[]>(
    `/shops/${shopId}/products`
  );

  return response.data;
}

export async function getProduct(
  shopId: string,
  productId: string
) {
  const response = await api.get<Product>(
    `/shops/${shopId}/products/${productId}`
  );

  return response.data;
}

export async function createProduct(
  shopId: string,
  data: CreateProductData
) {
  const response = await api.post<Product>(
    `/shops/${shopId}/products`,
    data
  );

  return response.data;
}

export async function updateProduct(
  shopId: string,
  productId: string,
  data: Partial<ProductData>
) {
  const response = await api.patch<Product>(
    `/shops/${shopId}/products/${productId}`,
    data
  );

  return response.data;
}

export async function updateStock(
  shopId: string,
  productId: string,
  quantity: number
) {
  const response = await api.patch<Product>(
    `/shops/${shopId}/products/${productId}/stock`,
    { quantity }
  );

  return response.data;
}

export async function deactivateProduct(
  shopId: string,
  productId: string
) {
  await api.delete(
    `/shops/${shopId}/products/${productId}`
  );
}