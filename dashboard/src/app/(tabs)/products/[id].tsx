import { useState, useEffect } from "react";

import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";

import { useLocalSearchParams, useRouter } from "expo-router";

import { useShop } from "@/contexts/ShopContext";
import ProductForm from "@/components/ProductForm";
import Input from "@/components/Input";
import Button from "@/components/Button";

import {
  getProduct,
  updateProduct,
  updateStock,
  deactivateProduct,
} from "@/services/product";

import {
  Product,
  CreateProductData,
} from "@/types/product";

export default function ProductDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { selectedShop } = useShop();
  const router = useRouter();

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [confirmDeactivate, setConfirmDeactivate] =
    useState(false);

  async function loadProduct() {
    if (!selectedShop || !id) return;

    try {
      setLoading(true);
      setError("");

      setProduct(await getProduct(selectedShop.id, id));
    } catch {
      setError("Failed to load product");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProduct();
  }, [selectedShop?.id, id]);

  async function handleUpdate(data: CreateProductData) {
    if (!selectedShop || !id) {
      throw new Error("Product unavailable");
    }

    const updated = await updateProduct(
      selectedShop.id,
      id,
      {
        name: data.name,
        cost_price: data.cost_price,
        selling_price: data.selling_price,
        unit: data.unit,
      }
    );

    setProduct(updated);
    router.back();
  }

  async function handleStock(direction: number) {
    if (!selectedShop || !id || !product || busy) return;

    const amount = Number(quantity);

    if (!Number.isSafeInteger(amount) || amount <= 0) {
      setError("Enter a positive whole number");
      return;
    }

    if (
      direction === -1 &&
      amount > product.stock_quantity
    ) {
      setError("Insufficient stock");
      return;
    }

    try {
      setBusy(true);
      setError("");

      const updated = await updateStock(
        selectedShop.id,
        id,
        amount * direction
      );

      setProduct(updated);
      setQuantity("");
    } catch {
      setError("Failed to update stock");
    } finally {
      setBusy(false);
    }
  }

  async function handleDeactivate() {
    if (!selectedShop || !id || busy) return;

    try {
      setBusy(true);
      setError("");

      await deactivateProduct(selectedShop.id, id);

      router.back();
    } catch {
      setError("Failed to deactivate product");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center">
        <ActivityIndicator color="#166534" />
      </View>
    );
  }

  if (!product) {
    return (
      <View className="gap-4 p-5">
        <Text className="text-red-600">{error}</Text>
        <Button title="Retry" onPress={loadProduct} />
      </View>
    );
  }

  return (
    <ScrollView
      className="flex-1 bg-background"
      keyboardShouldPersistTaps="handled"
    >
      <View className="mx-auto w-full max-w-xl gap-5 p-5">

        <View className="gap-4 rounded-xl border border-gray-200 bg-white p-5">
          <Text className="text-gray-500">
            Available stock
          </Text>

          <Text className="text-3xl font-bold text-primary">
            {product.stock_quantity} {product.unit}
          </Text>

          <Input
            label="Quantity"
            value={quantity}
            onChangeText={setQuantity}
            keyboardType="number-pad"
          />

          <View className="flex-row gap-3">
            <View className="flex-1">
              <Button
                title="+ Add stock"
                onPress={() => handleStock(1)}
                disabled={busy}
              />
            </View>

            <TouchableOpacity
              disabled={busy}
              onPress={() => handleStock(-1)}
              className="flex-1 items-center justify-center rounded-xl border border-red-200 p-3"
            >
              <Text className="font-semibold text-red-600">
                Remove stock
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {error ? (
          <Text className="text-red-600">{error}</Text>
        ) : null}

        <Text className="text-xl font-bold">
          Edit product
        </Text>

        <ProductForm
          key={product.id}
          product={product}
          onSubmit={handleUpdate}
        />

        {confirmDeactivate ? (
          <View className="gap-3 rounded-xl border border-red-200 bg-white p-4">
            <Text className="text-red-600">
              Deactivate this product? It will no longer
              appear in the active product list.
            </Text>

            <Button
              title="Confirm deactivation"
              onPress={handleDeactivate}
              loading={busy}
            />

            <Button
              title="Cancel"
              onPress={() => setConfirmDeactivate(false)}
              disabled={busy}
            />
          </View>
        ) : (
          <TouchableOpacity
            onPress={() => setConfirmDeactivate(true)}
            disabled={busy}
            className="items-center rounded-xl border border-red-200 p-4"
          >
            <Text className="font-semibold text-red-600">
              Deactivate product
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}