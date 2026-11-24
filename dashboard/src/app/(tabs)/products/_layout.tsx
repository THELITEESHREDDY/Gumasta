import { Stack } from "expo-router";

export default function ProductsLayout() {
  return (
    <Stack>
      <Stack.Screen
        name="index"
        options={{ headerShown: false }}
      />

      <Stack.Screen
        name="create"
        options={{ title: "Add product" }}
      />

      <Stack.Screen
        name="[id]"
        options={{ title: "Product details" }}
      />
    </Stack>
  );
}