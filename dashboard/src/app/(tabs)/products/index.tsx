import { useState, useCallback } from "react";

import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
} from "react-native";

import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter, useFocusEffect } from "expo-router";
import { Plus, Package, Search, ChevronRight } from "lucide-react-native";

import { useShop } from "@/contexts/ShopContext";
import { getProducts } from "@/services/product";
import { Product } from "@/types/product";
import Button from "@/components/Button";

export default function ProductsScreen() {
  const router = useRouter();
  const { selectedShop } = useShop();

  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadProducts = useCallback(async () => {
    if (!selectedShop) return;

    try {
      setLoading(true);
      setError("");

      setProducts(await getProducts(selectedShop.id));
    } catch {
      setError("Failed to load products");
    } finally {
      setLoading(false);
    }
  }, [selectedShop?.id]);

  useFocusEffect(
    useCallback(() => {
      loadProducts();
    }, [loadProducts])
  );

  const filteredProducts = products.filter((product) =>
    product.name.toLowerCase().includes(
      search.trim().toLowerCase()
    )
  );

  return (
    <SafeAreaView className="flex-1 bg-background">
      <View className="mx-auto w-full max-w-3xl flex-1 gap-4 p-5">

        <View className="flex-row items-center justify-between">
          <Text className="text-2xl font-bold">
            Products
          </Text>

          <TouchableOpacity
            onPress={() => router.push("/products/create")}
            className="flex-row items-center gap-2 rounded-xl bg-primary px-4 py-3"
          >
            <Plus size={18} color="white" />

            <Text className="font-semibold text-white">
              Add product
            </Text>
          </TouchableOpacity>
        </View>

        <View className="flex-row items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3">
          <Search size={20} color="#9CA3AF" />

          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Search products..."
            className="flex-1 text-base"
          />
        </View>

        {loading ? (
          <ActivityIndicator color="#166534" />
        ) : error ? (
          <View className="gap-3">
            <Text className="text-red-600">{error}</Text>
            <Button title="Retry" onPress={loadProducts} />
          </View>
        ) : (
          <>
            <Text className="text-sm text-gray-500">
              {filteredProducts.length} products
            </Text>

            <FlatList
              data={filteredProducts}
              keyExtractor={(item) => item.id}
              contentContainerStyle={{ gap: 12 }}
              ListEmptyComponent={
                <Text className="py-10 text-center text-gray-500">
                  No products found
                </Text>
              }
              renderItem={({ item }) => (
                <TouchableOpacity
                  onPress={() =>
                    router.push({
                      pathname: "/products/[id]",
                      params: { id: item.id },
                    })
                  }
                  className="gap-3 rounded-xl border border-gray-200 bg-white p-4"
                >
                  <View className="flex-row items-center gap-3">
                    <View className="rounded-xl bg-green-50 p-3">
                      <Package size={24} color="#166534" />
                    </View>

                    <View className="flex-1">
                      <Text className="text-base font-semibold">
                        {item.name}
                      </Text>

                      <Text className="text-sm text-gray-500">
                        ₹{item.selling_price} / {item.unit}
                      </Text>
                    </View>

                    <ChevronRight size={20} color="#9CA3AF" />
                  </View>

                  <View className="flex-row justify-between border-t border-gray-100 pt-3">
                    <Text className="text-gray-500">
                      Available stock
                    </Text>

                    <Text
                      className={`font-semibold ${
                        item.stock_quantity === 0
                          ? "text-red-600"
                          : "text-primary"
                      }`}
                    >
                      {item.stock_quantity} {item.unit}
                    </Text>
                  </View>
                </TouchableOpacity>
              )}
            />
          </>
        )}
      </View>
    </SafeAreaView>
  );
}