import "../../global.css";

import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { View, ActivityIndicator } from "react-native";

import {
  AuthProvider,
  useAuth,
} from "@/contexts/AuthContext";

import {
  ShopProvider,
  useShop,
} from "@/contexts/ShopContext";

function RootNavigator() {
  const { user, loading } = useAuth();
  const { selectedShop } = useShop();

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center bg-background">
        <ActivityIndicator size="large" color="#166534" />
      </View>
    );
  }

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" />

      <Stack.Protected guard={!user}>
        <Stack.Screen name="(auth)" />
      </Stack.Protected>

      <Stack.Protected guard={!!user}>
        <Stack.Screen name="shops" />

        <Stack.Protected guard={!!selectedShop}>
          <Stack.Screen name="(tabs)" />
        </Stack.Protected>
      </Stack.Protected>
    </Stack>
  );
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <ShopProvider>
        <StatusBar style="dark" />
        <RootNavigator />
      </ShopProvider>
    </AuthProvider>
  );
}