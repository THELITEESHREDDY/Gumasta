import { View, Text } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { useAuth } from "@/contexts/AuthContext";
import { useShop } from "@/contexts/ShopContext";
import Button from "@/components/Button";

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const { selectedShop, clearShop } = useShop();

  return (
    <SafeAreaView className="flex-1 bg-background p-6">
      <View className="gap-5">
        <Text className="text-2xl font-bold">
          Profile
        </Text>

        <View className="gap-2 rounded-xl bg-white p-5">
          <Text className="text-lg font-semibold">
            {user?.name}
          </Text>

          <Text className="text-gray-500">{user?.email}</Text>
          <Text className="text-gray-500">{user?.mobile}</Text>
        </View>

        <View className="gap-2 rounded-xl bg-white p-5">
          <Text className="text-sm text-gray-500">
            Current shop
          </Text>

          <Text className="text-lg font-semibold">
            {selectedShop?.name}
          </Text>

          <Text className="text-gray-500">
            {selectedShop?.address}
          </Text>
        </View>

        <Button title="Switch shop" onPress={clearShop} />

        <Button title="Logout" onPress={logout} />
      </View>
    </SafeAreaView>
  );
}