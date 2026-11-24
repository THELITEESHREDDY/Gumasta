import { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";

import { useRouter } from "expo-router";
import { Plus, Minus } from "lucide-react-native";
import axios from "axios";

import { useShop } from "@/contexts/ShopContext";
import { getCustomers } from "@/services/customer";
import { getProducts } from "@/services/product";
import { createOrder } from "@/services/order";

import { Customer } from "@/types/customer";
import { Product } from "@/types/product";

import Input from "@/components/Input";
import Button from "@/components/Button";

export default function CreateOrderScreen() {
  const router = useRouter();
  const { selectedShop } = useShop();

  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Product[]>([]);

  const [customerId, setCustomerId] = useState("");
  const [customerSearch, setCustomerSearch] = useState("");
  const [productSearch, setProductSearch] = useState("");

  const [cart, setCart] = useState<Record<string, number>>({});

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    if (!selectedShop) return;

    try {
      setLoading(true);
      setError("");

      const [customerData, productData] = await Promise.all([
        getCustomers(selectedShop.id),
        getProducts(selectedShop.id),
      ]);

      setCustomers(customerData);
      setProducts(productData);
    } catch {
      setError("Failed to load customers and products");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [selectedShop?.id]);

  function changeQuantity(product: Product, change: number) {
    setCart((previous) => {
      const current = previous[product.id] ?? 0;

      const quantity = Math.max(
        0,
        Math.min(product.stock_quantity, current + change)
      );

      return {
        ...previous,
        [product.id]: quantity,
      };
    });
  }

  const selectedProducts = products.filter(
    (product) => (cart[product.id] ?? 0) > 0
  );

  const total = selectedProducts.reduce(
    (sum, product) =>
      sum +
      Math.round(Number(product.selling_price) * 100) *
        cart[product.id],
    0
  ) / 100;

  async function handleCreate() {
    if (!selectedShop || submitting) return;

    if (!customerId || selectedProducts.length === 0) {
      setError("Select a customer and at least one product");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      const order = await createOrder(selectedShop.id, {
        customer_id: customerId,
        order_items: selectedProducts.map((product) => ({
          product_id: product.id,
          quantity: cart[product.id],
        })),
      });

      router.replace({
        pathname: "/dashboard/orders/[id]",
        params: { id: order.id },
      });
    } catch (err) {
      const detail = axios.isAxiosError(err)
        ? err.response?.data?.detail
        : null;

      setError(
        typeof detail === "string"
          ? detail
          : "Failed to create order"
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center">
        <ActivityIndicator color="#166534" />
      </View>
    );
  }

  return (
    <View className="flex-1 bg-background">
      <ScrollView keyboardShouldPersistTaps="handled">
        <View className="mx-auto w-full max-w-xl gap-4 p-5">

          <Text className="text-xl font-bold">
            Select customer
          </Text>

          <Input
            label="Search customer"
            value={customerSearch}
            onChangeText={setCustomerSearch}
            placeholder="Name or mobile"
          />

          {customers
            .filter(
              (customer) =>
                customer.name.toLowerCase().includes(
                  customerSearch.toLowerCase()
                ) ||
                customer.mobile.includes(customerSearch)
            )
            .map((customer) => (
              <TouchableOpacity
                key={customer.id}
                disabled={submitting}
                onPress={() => setCustomerId(customer.id)}
                className={`rounded-xl border p-4 ${
                  customerId === customer.id
                    ? "border-primary bg-green-50"
                    : "border-gray-200 bg-white"
                }`}
              >
                <Text className="font-semibold">
                  {customer.name}
                </Text>

                <Text className="text-gray-500">
                  {customer.mobile}
                </Text>
              </TouchableOpacity>
            ))}

          <Text className="mt-4 text-xl font-bold">
            Add products
          </Text>

          <Input
            label="Search product"
            value={productSearch}
            onChangeText={setProductSearch}
          />

          {products
            .filter((product) =>
              product.name.toLowerCase().includes(
                productSearch.toLowerCase()
              )
            )
            .map((product) => (
              <View
                key={product.id}
                className="flex-row items-center gap-3 rounded-xl border border-gray-200 bg-white p-4"
              >
                <View className="flex-1">
                  <Text className="font-semibold">
                    {product.name}
                  </Text>

                  <Text className="text-gray-500">
                    ₹{product.selling_price} / {product.unit}
                  </Text>

                  <Text className="text-xs text-gray-400">
                    Stock: {product.stock_quantity}
                  </Text>
                </View>

                <TouchableOpacity
                  disabled={submitting}
                  onPress={() => changeQuantity(product, -1)}
                  className="rounded-lg bg-gray-100 p-2"
                >
                  <Minus size={18} color="#374151" />
                </TouchableOpacity>

                <Text className="font-bold">
                  {cart[product.id] ?? 0}
                </Text>

                <TouchableOpacity
                  disabled={submitting}
                  onPress={() => changeQuantity(product, 1)}
                  className="rounded-lg bg-primary p-2"
                >
                  <Plus size={18} color="white" />
                </TouchableOpacity>
              </View>
            ))}

          {error ? (
            <Text className="text-red-600">{error}</Text>
          ) : null}

        </View>
      </ScrollView>

      <View className="gap-3 border-t border-gray-200 bg-white p-5">
        <View className="flex-row items-center justify-between">
          <Text className="text-gray-500">Total amount</Text>

          <Text className="text-2xl font-bold text-primary">
            ₹{total.toFixed(2)}
          </Text>
        </View>

        <Button
          title="Create order"
          onPress={handleCreate}
          loading={submitting}
          disabled={!customerId || selectedProducts.length === 0}
        />
      </View>
    </View>
  );
}