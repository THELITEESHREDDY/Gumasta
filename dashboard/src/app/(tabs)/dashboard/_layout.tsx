import { Stack } from "expo-router";

export default function DashboardLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{ headerShown: false }}
      />

      <Stack.Screen
        name="orders/create"
        options={{ title: "New order" }}
      />

      <Stack.Screen
        name="orders/[id]"
        options={{ title: "Order details" }}
      />
    </Stack>
  );
}