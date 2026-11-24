import { useState, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
} from "react-native";

import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter, useFocusEffect } from "expo-router";
import { Store, ChevronRight, LogOut } from "lucide-react-native";

import { useAuth } from "@/contexts/AuthContext";
import { useShop } from "@/contexts/ShopContext";
import { getShops } from "@/services/shop";
import { Shop } from "@/types/shop";
import Button from "@/components/Button";

export default function ShopsScreen() {
  const router = useRouter();
  const { logout } = useAuth();
  const { selectShop } = useShop();

  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadShops() {
    try {
      setLoading(true);
      setError("");
      setShops(await getShops());
    } catch {
      setError("Failed to load shops");
    } finally {
      setLoading(false);
    }
  }

  useFocusEffect(
    useCallback(() => {
      loadShops();
    }, [])
  );

  function handleSelect(shop: Shop) {
    selectShop(shop);
    router.replace("/dashboard");
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <View className="mx-auto w-full max-w-xl flex-1 gap-5 p-6">
        <View className="flex-row items-center justify-between">
          <Text className="text-2xl font-bold text-primary">
            Gumasta
          </Text>

          <TouchableOpacity onPress={logout}>
            <LogOut size={22} color="#6B7280" />
          </TouchableOpacity>
        </View>

        <View>
          <Text className="text-2xl font-bold text-gray-900">
            Your shops
          </Text>

          <Text className="mt-1 text-gray-500">
            Select a shop to continue
          </Text>
        </View>

        {loading ? (
          <ActivityIndicator color="#166534" />
        ) : error ? (
          <View className="gap-3">
            <Text className="text-red-600">{error}</Text>
            <Button title="Retry" onPress={loadShops} />
          </View>
        ) : (
          <FlatList
            data={shops}
            keyExtractor={(item) => item.id}
            contentContainerStyle={{ gap: 12 }}
            ListEmptyComponent={
              <Text className="py-10 text-center text-gray-500">
                No shops yet. Create your first shop.
              </Text>
            }
            renderItem={({ item }) => (
              <TouchableOpacity
                onPress={() => handleSelect(item)}
                className="flex-row items-center gap-4 rounded-xl border border-gray-200 bg-white p-4"
              >
                <View className="rounded-xl bg-green-100 p-3">
                  <Store size={24} color="#166534" />
                </View>

                <View className="flex-1">
                  <Text className="text-base font-semibold">
                    {item.name}
                  </Text>

                  <Text className="mt-1 text-sm text-gray-500">
                    {item.address}
                  </Text>
                </View>

                <ChevronRight size={20} color="#9CA3AF" />
              </TouchableOpacity>
            )}
          />
        )}

        <Button
          title="+ Create new shop"
          onPress={() => router.push("/shops/create")}
        />
      </View>
    </SafeAreaView>
  );
}